from django.db import models
from paypalrestsdk import payments as paypal_models

from .. import enums
from ..fields import CurrencyAmountField, JSONField
from .base import PaypalObject


class Payment(PaypalObject):
	intent = models.CharField(max_length=9, choices=enums.PaymentIntent.choices)
	cart = models.CharField(max_length=127, db_index=True, null=True, blank=True)
	payer = JSONField(null=True, blank=True)
	transactions = JSONField()
	state = models.CharField(max_length=8, choices=enums.PaymentState.choices)
	experience_profile_id = models.CharField(max_length=127, db_index=True)
	note_to_payer = models.CharField(max_length=165)
	create_time = models.DateTimeField(db_index=True, editable=False)
	update_time = models.DateTimeField(db_index=True, editable=False)
	redirect_urls = JSONField()
	failure_reason = models.CharField(
		max_length=30, choices=enums.PaymentFailureReason.choices
	)

	paypal_model = paypal_models.Payment

	@property
	def refund_url(self):
		base_url = "https://www.paypal.com/activity/actions/refund/issuerefund/"
		return base_url + self.id


class Refund(PaypalObject):
	amount = CurrencyAmountField(
		help_text=(
			"The refund amount. Includes both the amount refunded to the "
			"payer and amount of the fee refunded to the payee."
		)
	)
	state = models.CharField(
		max_length=9, choices=enums.RefundState.choices, editable=False,
		help_text="The state of the refund."
	)
	reason = models.TextField(
		blank=True, help_text="The reason that the transaction is being refunded."
	)
	invoice_number = models.CharField(
		max_length=127, blank=True, help_text="Your own invoice or tracking ID number."
	)
	sale = models.ForeignKey(
		"Sale", on_delete=models.PROTECT, related_name="refunds", editable=False,
		help_text="The sale transaction being refunded."
	)
	# TODO
	# capture = models.ForeignKey("Capture", null=True, related_name="refunds")
	parent_payment = models.ForeignKey(
		"Payment", on_delete=models.PROTECT, null=True, related_name="refunds", editable=False,
		help_text="The payment on which this transaction is based"
	)
	description = models.TextField(blank=True, help_text="The refund description.")
	create_time = models.DateTimeField(db_index=True, editable=False)
	update_time = models.DateTimeField(db_index=True, editable=False)
	reason_code = models.CharField(
		max_length=6, choices=enums.RefundPendingReasonCode.choices, editable=False,
		help_text="The reason code for the pending refund state."
	)
	refund_reason_code = models.CharField(
		max_length=31, choices=enums.RefundReasonCode.choices, editable=False,
		help_text="The PayPal-assigned reason codes for the refund."
	)
	refund_funding_type = models.CharField(
		max_length=6, choices=enums.RefundFundingType.choices, editable=False,
		help_text=(
			"Indicates whether the refund amount is funded by the payee's "
			"funding account or another funding account."
		)
	)
	refund_from_transaction_fee = CurrencyAmountField(
		null=True, editable=False, help_text=(
			"The currency and amount of the transaction fee that is "
			"refunded to original the recipient of payment."
		)
	)
	refund_from_received_amount = CurrencyAmountField(
		null=True, editable=False, help_text=(
			"The currency and amount of the refund that is subtracted from "
			"the original payment recipient's PayPal balance."
		)
	)
	total_refunded_amount = CurrencyAmountField(
		null=True, editable=False, help_text=(
			"The currency and amount of the total refund from the original "
			"purchase."
		)
	)

	paypal_model = paypal_models.Refund


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
	clearing_time = models.DateTimeField(null=True, blank=True, editable=False)
	transaction_fee = CurrencyAmountField(null=True, blank=True, editable=False)
	receivable_amount = CurrencyAmountField(null=True, blank=True, editable=False)
	exchange_rate = models.CharField(max_length=64, editable=False)
	fmf_details = JSONField(null=True, blank=True, editable=False)
	receipt_id = models.CharField(max_length=19, db_index=True, editable=False)
	parent_payment = models.ForeignKey(
		"Payment", on_delete=models.PROTECT, null=True, blank=True, editable=False
	)
	processor_response = JSONField(null=True, blank=True, editable=False)
	billing_agreement = models.ForeignKey(
		"BillingAgreement", on_delete=models.PROTECT, null=True, blank=True, editable=False
	)
	create_time = models.DateTimeField(db_index=True, editable=False)
	update_time = models.DateTimeField(db_index=True, editable=False)
	soft_descriptor = models.CharField(max_length=127, blank=True, editable=False)

	paypal_model = paypal_models.Sale
	dashboard_url_template = "{paypal}/activity/payment/63819926JU0458337"

	@classmethod
	def clean_api_data(cls, data):
		from .billing import BillingAgreement

		id, cleaned_data, m2ms = super().clean_api_data(data)

		if "billing_agreement_id" in cleaned_data:
			ba_id = cleaned_data["billing_agreement_id"]
			# Ensure that the billing agreement exists in the db
			# If it exists, it will be updated with new data
			BillingAgreement.find_and_sync(ba_id)

		# Ensure the parent payment exists in the db
		if "parent_payment" in cleaned_data:
			pp_id = cleaned_data["parent_payment"]
			try:
				Payment.objects.get(id=pp_id)
			except Payment.DoesNotExist:
				Payment.find_and_sync(pp_id)

			# Replace the parent_payment in the cleaned data with parent_payment_id
			cleaned_data["parent_payment_id"] = pp_id
			del cleaned_data["parent_payment"]

		return id, cleaned_data, m2ms
