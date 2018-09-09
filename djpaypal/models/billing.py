import re

from dateutil.parser import parse
from django.conf import settings
from django.db import models, transaction
from django.utils.timezone import now
from paypalrestsdk import payments as paypal_models

from .. import enums
from ..exceptions import AgreementAlreadyExecuted, PaypalApiError
from ..fields import CurrencyAmountField, JSONField
from ..settings import PAYPAL_LIVE_MODE
from .base import PaypalObject


def get_frequency_delta(frequency, frequency_interval):
	from dateutil.relativedelta import relativedelta

	frequency_kw = {
		enums.PaymentDefinitionFrequency.DAY: "days",
		enums.PaymentDefinitionFrequency.WEEK: "weeks",
		enums.PaymentDefinitionFrequency.MONTH: "months",
		enums.PaymentDefinitionFrequency.YEAR: "years",
	}[frequency.upper()]

	return relativedelta(**{frequency_kw: frequency_interval})


class BillingPlan(PaypalObject):
	name = models.CharField(max_length=128)
	description = models.CharField(max_length=127)
	type = models.CharField(max_length=20, choices=enums.BillingPlanType.choices)
	state = models.CharField(max_length=20, choices=enums.BillingPlanState.choices)
	create_time = models.DateTimeField(db_index=True, editable=False)
	update_time = models.DateTimeField(db_index=True, editable=False)
	merchant_preferences = JSONField()

	payment_definitions = models.ManyToManyField("PaymentDefinition")

	paypal_model = paypal_models.BillingPlan

	@classmethod
	def clean_api_data(cls, data):
		id, cleaned_data, m2ms = super().clean_api_data(data)

		pds = cleaned_data.pop("payment_definitions")
		# Sync payment definitions but do not fetch them (we have them in full)
		m2ms["payment_definitions"] = PaymentDefinition.objects.sync_data(pds, fetch=False)

		return id, cleaned_data, m2ms

	@classmethod
	def create(cls, data, activate=False):
		obj = cls.paypal_model(data)
		obj.create()
		if not obj:
			raise PaypalApiError("Could not create plan: %r" % (obj.error))

		instance, created = cls.get_or_update_from_api_data(obj, always_sync=True)
		if activate:
			instance.activate()

		return instance

	@property
	def regular_payment_definition(self):
		return self.payment_definitions.get(type=enums.PaymentDefinitionType.REGULAR)

	@property
	def human_readable_price(self):
		pd = self.regular_payment_definition
		if pd:
			return pd.human_readable_price
		return ""

	def activate(self):
		"""
		Activate an plan in a CREATED state.
		"""
		obj = self.find_paypal_object()
		if obj.state == enums.BillingPlanState.CREATED:
			success = obj.activate()
			if not success:
				raise PaypalApiError("Failed to activate plan: %r" % (obj.error))
		# Resync the updated data to the database
		self.get_or_update_from_api_data(obj, always_sync=True)
		return obj

	def create_agreement(
		self, user, start_date,
		payment_method="paypal", override_merchant_preferences=None
	):
		billing_agreement = paypal_models.BillingAgreement({
			"name": self.name,
			"description": self.description,
			"plan": {"id": self.id},
			"payer": {"payment_method": payment_method},
			"start_date": start_date.replace(microsecond=0).isoformat(),
		})

		if override_merchant_preferences:
			billing_agreement["override_merchant_preferences"] = override_merchant_preferences.copy()

		if not billing_agreement.create():
			raise PaypalApiError("Error creating Billing Agreement: %r" % (billing_agreement.error))

		return PreparedBillingAgreement.create_from_data(billing_agreement, user)


class PreparedBillingAgreement(models.Model):
	"""
	A class that stores a billing agreement execution token,
	and ties it to the user who requested it.
	"""
	id = models.CharField(
		max_length=128, primary_key=True, editable=False, serialize=True,
		help_text="Same as the BillingAgreement token"
	)
	livemode = models.BooleanField()
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	data = JSONField()
	executed_agreement = models.ForeignKey(
		"BillingAgreement", on_delete=models.SET_NULL, null=True, blank=True,
		related_name="prepared_agreements"
	)
	executed_at = models.DateTimeField(null=True, blank=True)
	canceled_at = models.DateTimeField(null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True, db_index=True)
	updated = models.DateTimeField(auto_now=True, db_index=True)

	@staticmethod
	def _extract_token(data):
		# Paypal does not provide a clear field for the token.
		# In order to offer a way to securely tie the user to a token, we
		# use it as a primary key in this model but we have to extract it
		# from the HATEOAS urls first.
		token_match = re.compile(r"/billing-agreements/([^/]+)/agreement-execute")
		for link in data.get("links", []):
			sre = token_match.search(link.get("href", ""))
			if sre:
				return sre.groups(0)[0]
		raise ValueError("Could not find token in billing agreement data")

	@classmethod
	def create_from_data(cls, data, user):
		data = data.to_dict()
		return cls.objects.create(
			id=cls._extract_token(data), livemode=PAYPAL_LIVE_MODE, user=user, data=data
		)

	def __str__(self):
		return "<{}: {}>".format(self.__class__.__name__, self.id)

	@property
	def approval_url(self):
		for link in self.data.get("links", []):
			if link["rel"] == "approval_url":
				return link["href"]
		return ""

	def cancel(self):
		if self.executed_at:
			raise AgreementAlreadyExecuted("Agreement has already been executed")
		self.canceled_at = now()
		self.save()

	def execute(self):
		"""
		Execute the PreparedBillingAgreement by creating and executing a
		matching BillingAgreement.
		"""
		# Save the execution time first.
		# If execute() fails, executed_at will be set, with no executed_agreement set.
		self.executed_at = now()
		self.save()

		with transaction.atomic():
			ret = BillingAgreement.execute(self.id)
			ret.user = self.user
			ret.save()
			self.executed_agreement = ret
			self.save()

		return ret


class BillingAgreement(PaypalObject):
	name = models.CharField(max_length=128, blank=True)
	state = models.CharField(
		max_length=128, editable=False, choices=enums.BillingAgreementState.choices
	)
	description = models.CharField(max_length=128)
	start_date = models.DateTimeField(db_index=True)
	agreement_details = JSONField()
	payer = JSONField()
	shipping_address = JSONField()
	override_merchant_preferences = JSONField(default=dict, blank=True)
	override_charge_mode = JSONField(default=dict, blank=True)
	plan = JSONField()
	merchant = JSONField(null=True, blank=True)

	payer_model = models.ForeignKey(
		"Payer", on_delete=models.SET_NULL, null=True, blank=True
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
	)
	end_of_period = models.DateTimeField(db_index=True)

	paypal_model = paypal_models.BillingAgreement
	dashboard_url_template = (
		"{webscr}?cmd=_profile-recurring-payments&encrypted_profile_id={id}"
	)

	@classmethod
	def execute(cls, token):
		if not token:
			raise ValueError("Invalid token argument")

		ba = cls.paypal_model.execute(token)
		if ba.error:
			raise PaypalApiError(str(ba.error))  # , ba.error)

		obj, created = cls.get_or_update_from_api_data(ba, always_sync=True)
		return obj

	def save(self, **kwargs):
		from .payer import Payer

		# On save, get the payer_info object and do a best effort attempt at
		# saving a Payer model and relation into the db.
		payer_info = self.payer.get("payer_info", {})
		if payer_info and "payer_id" in payer_info:
			# Copy the payer_info dict before mutating it
			payer_info = payer_info.copy()
			payer_id = payer_info.pop("payer_id")
			payer_info["user"] = self.user
			payer_info["livemode"] = self.livemode
			self.payer_model, created = Payer.objects.update_or_create(
				id=payer_id, defaults=payer_info
			)

		self.end_of_period = self.calculate_end_of_period()
		return super().save(**kwargs)

	@property
	def last_payment_date(self):
		date = self.agreement_details.get("last_payment_date", "")
		if date:
			return parse(date)

	def calculate_end_of_period(self):
		# The next payment date is not reliably set.
		# When a subscription is cancelled, we do not have access to it anymore...
		# So instead, keep the end_of_period attribute up to date.
		last_payment_date = self.last_payment_date
		if not last_payment_date:
			return parse("1970-01-01T00:00:00Z")

		rpd = next(filter(
			lambda pd: pd["type"] == enums.PaymentDefinitionType.REGULAR,
			self.plan["payment_definitions"]
		))

		delta = get_frequency_delta(rpd["frequency"], int(rpd["frequency_interval"]))

		return last_payment_date + delta


class PaymentDefinition(PaypalObject):
	name = models.CharField(max_length=128)
	type = models.CharField(max_length=20, choices=enums.PaymentDefinitionType.choices)
	frequency_interval = models.PositiveSmallIntegerField()
	frequency = models.CharField(
		max_length=20, choices=enums.PaymentDefinitionFrequency.choices
	)
	cycles = models.PositiveSmallIntegerField()
	amount = CurrencyAmountField()

	charge_models = models.ManyToManyField("ChargeModel")

	@classmethod
	def clean_api_data(cls, data):
		id, cleaned_data, m2ms = super().clean_api_data(data)

		cleaned_data["frequency"] = cleaned_data["frequency"].upper()
		if "charge_models" in cleaned_data:
			charge_models = cleaned_data.pop("charge_models")
			# Sync payment definitions but do not fetch them (we have them in full)
			m2ms["charge_models"] = ChargeModel.objects.sync_data(charge_models, fetch=False)

		return id, cleaned_data, m2ms

	@property
	def human_readable_price(self):
		from ..utils import get_friendly_currency_amount

		amount = get_friendly_currency_amount(self.amount["value"], self.amount["currency"])
		interval_count = self.frequency_interval

		if interval_count == 1:
			interval = self.frequency.lower()
			template = "{amount}/{interval}"
		else:
			interval = {
				enums.PaymentDefinitionFrequency.DAY: "days",
				enums.PaymentDefinitionFrequency.WEEK: "weeks",
				enums.PaymentDefinitionFrequency.MONTH: "months",
				enums.PaymentDefinitionFrequency.YEAR: "years",
			}[self.frequency]
			template = "{amount} every {interval_count} {interval}"

		return template.format(amount=amount, interval=interval, interval_count=interval_count)

	@property
	def frequency_delta(self):
		"""
		Helper property that returns a dateutil.relativedelta.relativedelta
		object which represents a full billing period.

		https://dateutil.readthedocs.io/en/stable/relativedelta.html
		"""

		return get_frequency_delta(self.frequency, self.frequency_interval)


class ChargeModel(PaypalObject):
	type = models.CharField(max_length=20, choices=enums.ChargeModelType.choices)
	amount = CurrencyAmountField()
