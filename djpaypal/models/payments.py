from django.db import models
from paypalrestsdk import payments as paypal_models

from .. import enums
from ..fields import CurrencyAmountField, JSONField
from .base import PaypalObject


class Sale(PaypalObject):
	amount = CurrencyAmountField(editable=False)
	payment_mode = models.CharField(
		max_length=20, choices=enums.SalePaymentMode.choices, editable=False
	)
	state = models.CharField(max_length=20, choices=enums.SaleState.choices, editable=False)
	reason_code = models.CharField(
		max_length=43, choices=enums.SaleReasonCode.choices, editable=False
	)
	protection_eligibility = models.CharField(
		max_length=18, choices=enums.SaleProtectionEligibility.choices, editable=False
	)
	protection_eligibility_type = models.CharField(
		max_length=56, choices=enums.SaleProtectionEligibilityType.choices, editable=False
	)
	clearing_time = models.DateTimeField(null=True, editable=False)
	transaction_fee = CurrencyAmountField(editable=False)
	receivable_amount = CurrencyAmountField(null=True, editable=False)
	exchange_rate = models.CharField(max_length=64, editable=False)
	fmf_details = JSONField(null=True, editable=False)
	receipt_id = models.CharField(max_length=19, db_index=True, editable=False)
	# parent_payment = models.ForeignKey("Payment", editable=False)
	processor_response = JSONField(null=True, editable=False)
	billing_agreement = models.ForeignKey("BillingAgreement", editable=False)
	create_time = models.DateTimeField(editable=False)
	update_time = models.DateTimeField(editable=False)

	paypal_model = paypal_models.Sale

	@classmethod
	def clean_api_data(cls, data):
		from .billing import BillingAgreement

		id, cleaned_data, m2ms = super().clean_api_data(data)

		ba_id = cleaned_data["billing_agreement_id"]
		# Ensure that the billing agreement exists in the db
		try:
			BillingAgreement.objects.get(id=ba_id)
		except BillingAgreement.DoesNotExist:
			BillingAgreement.find_and_sync(ba_id)

		return id, cleaned_data, m2ms
