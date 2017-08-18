from django.db import models

from ..fields import JSONField
from .base import PaypalObject


class Webhook(PaypalObject):
	event_version = models.CharField(max_length=8)
	create_time = models.DateTimeField()
	event_type = models.CharField(max_length=64)

	headers = JSONField()
	data = JSONField()
