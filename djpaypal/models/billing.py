from django.db import models
from paypalrestsdk import payments as paypal_models

from .. import enums
from ..exceptions import PaypalApiError
from ..fields import CurrencyAmountField, JSONField
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


class BillingAgreement(PaypalObject):
	name = models.CharField(max_length=128, blank=True)
	state = models.CharField(max_length=128, editable=False)
	description = models.CharField(max_length=128)
	start_date = models.DateTimeField()
	agreement_details = JSONField()
	payer = JSONField()
	shipping_address = JSONField()
	override_merchant_preferences = JSONField(default={})
	override_charge_mode = JSONField(default={})
	plan = JSONField()

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
