from django.db import models

from .. import enums
from ..fields import CurrencyAmountField, JSONField
from .base import PaypalObject


class Dispute(PaypalObject):
	dispute_id = models.CharField(
		max_length=128, primary_key=True, editable=False, serialize=True
	)
	create_time = models.DateTimeField(db_index=True, editable=False)
	update_time = models.DateTimeField(null=True, blank=True, db_index=True, editable=False)
	disputed_transactions = JSONField(editable=False)
	reason = models.CharField(
		max_length=39, choices=enums.DisputeReason.choices, editable=False
	)
	status = models.CharField(max_length=27, choices=enums.DisputeStatus.choices)
	dispute_amount = CurrencyAmountField(editable=False)
	dispute_channel = models.CharField(max_length=8, blank=True, editable=False)
	dispute_life_cycle_stage = models.CharField(max_length=15, blank=True, editable=False)
	dispute_outcome = JSONField(null=True, blank=True, editable=False)
	messages = JSONField(null=True, blank=True)
	seller_response_due_date = models.DateTimeField(null=True, blank=True, editable=False)
	dispute_flow = models.CharField(
		max_length=25, choices=enums.DisputeFlow.choices, editable=False
	)
	offer = JSONField(null=True, blank=True, editable=False)

	id_field_name = "dispute_id"
	dashboard_url_template = "{paypal}/resolutioncenter/achcb/case/{id}"

	@property
	def id(self):
		return self.dispute_id
