from django.contrib.postgres.fields import JSONField
from django.db import models
from . import enums


class CurrencyAmountField(JSONField):
	pass


class PaypalObjectManager(models.Manager):
	def sync_data(self, paypal_data):
		ret = []
		for obj in paypal_data:
			data = obj.__data__.copy()
			db_obj, _ = self.model.get_or_update_from_api_data(data)
			ret.append(db_obj)
		return ret


class PaypalObject(models.Model):
	class Meta:
		abstract = True

	id = models.CharField(max_length=128, primary_key=True)
	livemode = models.BooleanField()

	objects = PaypalObjectManager()

	@classmethod
	def get_or_update_from_api_data(cls, data):
		id = data.pop("id")
		db_obj, created = cls.objects.get_or_create(id=id, defaults=data)
		if not created:
			db_obj.sync_data(id)
			db_obj.save()

		return db_obj, created

	def _sync_data_field(self, k, v):
		if k == "links":
			return False

		if getattr(self, k) != v:
			setattr(self, k, v)
			return True

		return False

	def sync_data(self, obj):
		updated = False
		for k, v in obj.items():
			if self._sync_data_field(k, v):
				updated = True

		if updated:
			self.save()


class BillingPlan(PaypalObject):
	name = models.CharField(max_length=128)
	description = models.CharField(max_length=127)
	type = models.CharField(max_length=20, choices=enums.BillingPlanType.choices)
	state = models.CharField(max_length=20, choices=enums.BillingPlanState.choices)
	create_time = models.DateTimeField()
	update_time = models.DateTimeField()
	merchant_preferences = JSONField()


class PaymentDefinition(PaypalObject):
	name = models.CharField(max_length=128)
	type = models.CharField(max_length=20, choices=enums.PaymentDefinitionType.choices)
	frequency_interval = models.PositiveSmallIntegerField()
	frequency = models.CharField(
		max_length=20, choices=enums.PaymentDefinitionFrequency.choices
	)
	cycles = models.PositiveSmallIntegerField()
	amount = CurrencyAmountField()


class Webhook(PaypalObject):
	event_version = models.CharField(max_length=8)
	create_time = models.DateTimeField()
	event_type = models.CharField(max_length=64)

	headers = JSONField()
	data = JSONField()
