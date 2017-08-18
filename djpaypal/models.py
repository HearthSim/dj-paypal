from django.contrib.postgres.fields import JSONField
from django.db import models
from paypalrestsdk import payments as paypal_models
from . import enums


class CurrencyAmountField(JSONField):
	pass


class PaypalObjectManager(models.Manager):
	def sync_data(self, paypal_data, fetch=True):
		ret = []
		for obj in paypal_data:
			if fetch:
				api_full_data = self.model.paypal_model.find(obj["id"])
			else:
				api_full_data = obj
			db_obj, _ = self.model.get_or_update_from_api_data(api_full_data)
			ret.append(db_obj)
		return ret


class PaypalObject(models.Model):
	class Meta:
		abstract = True

	id = models.CharField(max_length=128, primary_key=True)
	livemode = models.BooleanField()

	objects = PaypalObjectManager()

	@classmethod
	def clean_api_data(cls, data):
		if isinstance(data, dict):
			cleaned_data = data.copy()
		else:
			# Paypal SDK object
			cleaned_data = data.to_dict()

		# Delete links (only useful in the API itself)
		if "links" in cleaned_data:
			del cleaned_data["links"]

		# Extract the ID to return it separately
		id = cleaned_data.pop("id")

		# Set the livemode
		cleaned_data["livemode"] = False

		return id, cleaned_data

	@classmethod
	def get_or_update_from_api_data(cls, data):
		id, cleaned_data = cls.clean_api_data(data)
		db_obj, created = cls.objects.get_or_create(id=id, defaults=cleaned_data)
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

	paypal_model = paypal_models.BillingPlan

	@classmethod
	def clean_api_data(cls, data):
		id, cleaned_data = super().clean_api_data(data)

		payment_definitions = cleaned_data.pop("payment_definitions")
		# Sync payment definitions but do not fetch them (we have them in full)
		PaymentDefinition.objects.sync_data(payment_definitions, fetch=False)

		return id, cleaned_data


class PaymentDefinition(PaypalObject):
	name = models.CharField(max_length=128)
	type = models.CharField(max_length=20, choices=enums.PaymentDefinitionType.choices)
	frequency_interval = models.PositiveSmallIntegerField()
	frequency = models.CharField(
		max_length=20, choices=enums.PaymentDefinitionFrequency.choices
	)
	cycles = models.PositiveSmallIntegerField()
	amount = CurrencyAmountField()

	@classmethod
	def clean_api_data(cls, data):
		id, cleaned_data = super().clean_api_data(data)

		charge_models = cleaned_data.pop("charge_models")
		# Sync payment definitions but do not fetch them (we have them in full)
		ChargeModel.objects.sync_data(charge_models, fetch=False)

		return id, cleaned_data


class ChargeModel(PaypalObject):
	type = models.CharField(max_length=20, choices=enums.ChargeModelType.choices)
	amount = CurrencyAmountField()


class Webhook(PaypalObject):
	event_version = models.CharField(max_length=8)
	create_time = models.DateTimeField()
	event_type = models.CharField(max_length=64)

	headers = JSONField()
	data = JSONField()
