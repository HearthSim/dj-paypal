import json
from traceback import format_exc
from django.db import models
from django.utils.functional import cached_property
from paypalrestsdk import notifications as paypal_models

from ..fields import JSONField
from ..utils import fix_django_headers
from .base import PaypalObject


class WebhookEvent(PaypalObject):
	event_version = models.CharField(max_length=8)
	create_time = models.DateTimeField()
	event_type = models.CharField(max_length=64)
	resource_type = models.CharField(max_length=64)
	resource = JSONField()
	status = models.CharField(max_length=64)
	summary = models.CharField(max_length=256)
	transmissions = JSONField(null=True)

	paypal_model = paypal_models.WebhookEvent

	@classmethod
	def process(cls, data):
		ret, created = cls.get_or_update_from_api_data(data)
		ret.create_or_update_resource()
		return ret

	def create_or_update_resource(self):
		if self.resource_type == "sale":
			from .payments import Sale
			return Sale.get_or_update_from_api_data(self.resource)
		raise NotImplementedError(self.resource_type)


class WebhookEventTrigger(models.Model):
	id = models.BigAutoField(primary_key=True)
	headers = JSONField()
	body = models.TextField()
	valid = models.BooleanField(default=False)
	processed = models.BooleanField(default=False)
	exception = models.CharField(max_length=128)
	traceback = models.TextField()
	webhook_event = models.ForeignKey(
		"WebhookEvent", on_delete=models.SET_NULL, null=True
	)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	@classmethod
	def from_request(cls, request):
		headers = fix_django_headers(request.META)
		try:
			body = request.body.decode(request.encoding or "utf-8")
		except Exception:
			body = "(error decoding body)"
		obj = cls.objects.create(headers=headers, body=body)
		try:
			obj.valid = obj.verify()
			if obj.valid:
				obj.process()
		except Exception as e:
			obj.exception = str(e)
			obj.traceback = format_exc()
		finally:
			obj.save()

		return obj

	@cached_property
	def data(self):
		try:
			return json.loads(self.body)
		except ValueError:
			return {}

	@property
	def auth_algo(self):
		return self.headers.get("paypal-auth-algo", "")

	@property
	def cert_url(self):
		return self.headers.get("paypal-cert-url", "")

	@property
	def transmission_id(self):
		return self.headers.get("paypal-transmission-id", "")

	@property
	def transmission_sig(self):
		return self.headers.get("Paypal-Transmission-Sig", "")

	@property
	def transmission_time(self):
		return self.headers.get("paypal-transmission-time", "")

	def verify(self, webhook_id):
		return paypal_models.WebhookEvent.verify(
			transmission_id=self.transmission_id,
			timestamp=self.transmission_time,
			webhook_id=webhook_id,
			event_body=self.body,
			cert_url=self.cert_url,
			actual_signature=self.transmission_sig,
			auth_algo=self.auth_algo,
		)

	def process(self):
		obj = WebhookEvent.process(self.data)
		self.webhook_event = obj
		return obj
