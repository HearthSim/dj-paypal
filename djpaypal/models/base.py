from django.db import models

from ..settings import PAYPAL_LIVE_MODE


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

	id = models.CharField(max_length=128, primary_key=True, editable=False, serialize=True)
	livemode = models.BooleanField()

	djpaypal_created = models.DateTimeField(auto_now_add=True)
	djpaypal_updated = models.DateTimeField(auto_now=True)

	objects = PaypalObjectManager()

	id_field_name = "id"
	dashboard_url_template = ""

	@staticmethod
	def sdk_object_as_dict(obj):
		if isinstance(obj, dict):
			return obj.copy()
		# Paypal SDK object
		return obj.to_dict()

	@classmethod
	def clean_api_data(cls, data):
		cleaned_data = cls.sdk_object_as_dict(data)

		# Delete links (only useful in the API itself)
		if "links" in cleaned_data:
			del cleaned_data["links"]

		# Extract the ID to return it separately
		id = cleaned_data.pop(cls.id_field_name)

		# Set the livemode
		cleaned_data["livemode"] = PAYPAL_LIVE_MODE

		return id, cleaned_data, {}

	@classmethod
	def get_or_update_from_api_data(cls, data, always_sync=False):
		id, cleaned_data, m2ms = cls.clean_api_data(data)
		db_obj, created = cls.objects.get_or_create(**{
			cls.id_field_name: id,
			"defaults": cleaned_data,
		})
		if always_sync or not created:
			db_obj.sync_data(cleaned_data)
			db_obj.save()

		for field, objs in m2ms.items():
			for obj in objs:
				getattr(db_obj, field).add(obj)

		return db_obj, created

	@classmethod
	def find_and_sync(cls, id):
		obj = cls.paypal_model.find(id)
		db_obj, created = cls.get_or_update_from_api_data(obj, always_sync=True)
		return db_obj

	def __str__(self):
		if hasattr(self, "name") and self.name:
			return self.name
		return self.id

	@property
	def dashboard_url(self):
		if self.livemode:
			paypal_url = "https://www.paypal.com"
		else:
			paypal_url = "https://www.sandbox.paypal.com"

		return self.dashboard_url_template.format(
			paypal=paypal_url, webscr=paypal_url + "/cgi-bin/webscr",
			id=getattr(self, self.id_field_name)
		)

	def _sync_data_field(self, k, v):
		if k == "links":
			return False

		if getattr(self, k) != v:
			setattr(self, k, v)
			return True

		return False

	def find_paypal_object(self):
		return self.paypal_model.find(self.id)

	def sync_data(self, obj):
		obj = self.sdk_object_as_dict(obj)
		updated = False
		for k, v in obj.items():
			if self._sync_data_field(k, v):
				updated = True

		if updated:
			self.save()
