from django.conf import settings
from django.db import models

from ..fields import JSONField


class Payer(models.Model):
	id = models.CharField(max_length=13, primary_key=True)
	first_name = models.CharField(max_length=64, db_index=True)
	last_name = models.CharField(max_length=64, db_index=True)
	email = models.CharField(max_length=127, db_index=True)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
		related_name="paypal_payers"
	)
	shipping_address = JSONField(null=True)
	livemode = models.BooleanField()
	djpaypal_created = models.DateTimeField(auto_now_add=True)
	djpaypal_updated = models.DateTimeField(auto_now=True)
