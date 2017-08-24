import re

from django.conf import settings
from django.db import models, transaction
from django.utils.timezone import now
from paypalrestsdk import payments as paypal_models

from .. import enums
from ..exceptions import PaypalApiError
from ..fields import CurrencyAmountField, JSONField
from ..settings import PAYPAL_MODE
from .base import PaypalObject


class BillingPlan(PaypalObject):
	name = models.CharField(max_length=128)
	description = models.CharField(max_length=127)
	type = models.CharField(max_length=20, choices=enums.BillingPlanType.choices)
	state = models.CharField(max_length=20, choices=enums.BillingPlanState.choices)
	create_time = models.DateTimeField()
	update_time = models.DateTimeField()
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

	def create_agreement(self, user, start_date=now, payment_method="paypal"):
		if callable(start_date):
			from datetime import timedelta
			start_date = start_date() + timedelta(seconds=60)

		billing_agreement = paypal_models.BillingAgreement({
			"name": self.name,
			"description": self.description,
			"plan": {"id": self.id},
			"payer": {"payment_method": payment_method},
			"start_date": start_date.replace(microsecond=0).isoformat(),
		})
		if not billing_agreement.create():
			raise PaypalApiError("Error creating Billing Agreement: %r" % (billing_agreement.error))

		return PreparedBillingAgreement.create_from_data(billing_agreement, user)


class PreparedBillingAgreement(models.Model):
	"""
	A class that stores a billing agreement execution token,
	and ties it to the user who requested it.
	"""
	id = models.CharField(
		max_length=128, primary_key=True,
		help_text="Same as the BillingAgreement token"
	)
	livemode = models.BooleanField()
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	data = JSONField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

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
		livemode = PAYPAL_MODE == "production"
		return cls.objects.create(
			id=cls._extract_token(data), livemode=livemode, user=user, data=data
		)

	def execute(self):
		with transaction.atomic():
			ret = BillingAgreement.execute(self.id)
			ret.user = self.user
			ret.save()

		return ret


class BillingAgreement(PaypalObject):
	name = models.CharField(max_length=128, blank=True)
	state = models.CharField(
		max_length=128, editable=False, choices=enums.BillingAgreementState.choices
	)
	description = models.CharField(max_length=128)
	start_date = models.DateTimeField()
	agreement_details = JSONField()
	payer = JSONField()
	shipping_address = JSONField()
	override_merchant_preferences = JSONField(default={})
	override_charge_mode = JSONField(default={})
	plan = JSONField()

	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

	@classmethod
	def execute(cls, token):
		if not token:
			raise ValueError("Invalid token argument")

		ba = paypal_models.BillingAgreement.execute(token)
		if ba.error:
			raise PaypalApiError(str(ba.error))  # , ba.error)

		return cls.get_or_update_from_api_data(ba, always_sync=True)


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

		charge_models = cleaned_data.pop("charge_models")
		# Sync payment definitions but do not fetch them (we have them in full)
		m2ms["charge_models"] = ChargeModel.objects.sync_data(charge_models, fetch=False)

		return id, cleaned_data, m2ms


class ChargeModel(PaypalObject):
	type = models.CharField(max_length=20, choices=enums.ChargeModelType.choices)
	amount = CurrencyAmountField()
