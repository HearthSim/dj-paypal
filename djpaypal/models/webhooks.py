from django.db import models
from paypalrestsdk import notifications as paypal_models

from ..fields import JSONField
from .base import PaypalObject


class WebhookEvent(PaypalObject):
	event_version = models.CharField(max_length=8)
	create_time = models.DateTimeField()
	event_type = models.CharField(max_length=64)
	resource_type = models.CharField(max_length=64)
	resource = JSONField()
	status = models.CharField(max_length=64)
	summary = models.CharField(max_length=256)
	transmissions = JSONField()

	paypal_model = paypal_models.WebhookEvent

	@classmethod
	def process(cls, data):
		ret, created = cls.get_or_update_from_api_data(data)
		return ret
