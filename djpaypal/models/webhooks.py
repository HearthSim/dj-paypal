import json
from traceback import format_exc
from django.db import models
from django.utils.functional import cached_property
from paypalrestsdk import notifications as paypal_models

from ..fields import JSONField
from ..settings import PAYPAL_WEBHOOK_ID
from ..utils import fix_django_headers, get_version
from .base import PaypalObject


class WebhookEvent(PaypalObject):
	event_version = models.CharField(max_length=8, editable=False)
	create_time = models.DateTimeField(db_index=True, editable=False)
	event_type = models.CharField(max_length=64, editable=False)
	resource_type = models.CharField(max_length=64, editable=False)
	resource = JSONField(editable=False)
	status = models.CharField(max_length=64, blank=True, editable=False)
	summary = models.CharField(max_length=256, editable=False)
	transmissions = JSONField(null=True, blank=True, editable=False)

	paypal_model = paypal_models.WebhookEvent

	def __str__(self):
		return self.summary or super().__str__()

	@classmethod
	def process(cls, data):
		ret, created = cls.get_or_update_from_api_data(data)
		ret.create_or_update_resource()
		return ret

	def create_or_update_resource(self):
		if self.resource_type == "sale":
			from .payments import Sale
			return Sale.get_or_update_from_api_data(self.resource)
		if self.resource_type == "Agreement":
			from .billing import BillingAgreement
			return BillingAgreement.get_or_update_from_api_data(self.resource)
		if self.resource_type == "plan":
			from .billing import BillingPlan
			return BillingPlan.get_or_update_from_api_data(self.resource)
		if self.resource_type == "dispute":
			if self.event_type.lower().startswith("risk.dispute."):
				# risk.dispute.* events are different dispute object.
				# Also, who the **** knows what these objects actually are.
				# TODO: Get/Create the actual dispute object.
				# Depends on SDK implementation which is currently missing:
				# https://github.com/paypal/PayPal-Python-SDK/issues/216
				return
			from .disputes import Dispute
			return Dispute.get_or_update_from_api_data(self.resource)
		raise NotImplementedError(self.resource_type)


class WebhookEventTrigger(models.Model):
	id = models.BigAutoField(primary_key=True)
	headers = JSONField()
	body = models.TextField(blank=True)
	valid = models.BooleanField(default=False)
	processed = models.BooleanField(default=False)
	exception = models.CharField(max_length=128, blank=True)
	traceback = models.TextField(blank=True)
	webhook_event = models.ForeignKey(
		"WebhookEvent", on_delete=models.SET_NULL, null=True, blank=True
	)
	djpaypal_version = models.CharField(
		max_length=32,
		default=get_version,
		help_text="The version of dj-paypal when the webhook was received"
	)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	@classmethod
	def from_request(cls, request, webhook_id=PAYPAL_WEBHOOK_ID):
		"""
		Create, validate and process a WebhookEventTrigger given a Django
		request object.

		The webhook_id parameter expects the ID of the Webhook that was
		triggered (defaults to settings.PAYPAL_WEBHOOK_ID). This is required
		for Webhook verification.

		The process is three-fold:
		1. Create a WebhookEventTrigger object from a Django request.
		2. Verify the WebhookEventTrigger as a Paypal webhook using the SDK.
		3. If valid, process it into a WebhookEvent object (and child resource).
		"""
		headers = fix_django_headers(request.META)
		assert headers
		try:
			body = request.body.decode(request.encoding or "utf-8")
		except Exception:
			body = "(error decoding body)"
		obj = cls.objects.create(headers=headers, body=body)
		try:
			obj.valid = obj.verify(PAYPAL_WEBHOOK_ID)
			if obj.valid:
				# Process the item (do not save it, it'll get saved below)
				obj.process(save=False)
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
		return self.headers.get("paypal-transmission-sig", "")

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
			actual_sig=self.transmission_sig,
			auth_algo=self.auth_algo,
		)

	def process(self, save=True):
		obj = WebhookEvent.process(self.data)
		self.webhook_event = obj
		self.processed = True
		if save:
			self.save()
		return obj
