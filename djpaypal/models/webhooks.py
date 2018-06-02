import json
from fnmatch import fnmatch
from traceback import format_exc

from django.db import models
from django.dispatch import Signal
from django.utils.functional import cached_property
from paypalrestsdk import notifications as paypal_models

from ..fields import JSONField
from ..settings import PAYPAL_WEBHOOK_ID
from ..utils import fix_django_headers, get_version
from .base import PaypalObject


WEBHOOK_EVENT_TYPES = {
	"billing.plan.created",
	"billing.plan.updated",
	"billing.subscription.cancelled",
	"billing.subscription.created",
	"billing.subscription.re-activated",
	"billing.subscription.suspended",
	"billing.subscription.updated",
	"customer.dispute.created",
	"customer.dispute.resolved",
	"identity.authorization-consent.revoked",
	"invoicing.invoice.cancelled",
	"invoicing.invoice.created",
	"invoicing.invoice.paid",
	"invoicing.invoice.refunded",
	"invoicing.invoice.updated",
	"merchant.onboarding.completed",
	"payment.authorization.created",
	"payment.authorization.voided",
	"payment.capture.completed",
	"payment.capture.denied",
	"payment.capture.pending",
	"payment.capture.refunded",
	"payment.capture.reversed",
	"payment.order.cancelled",
	"payment.order.created",
	"payment.payoutsbatch.denied",
	"payment.payoutsbatch.processing",
	"payment.payoutsbatch.success",
	"payment.payouts-item.blocked",
	"payment.payouts-item.canceled",
	"payment.payouts-item.denied",
	"payment.payouts-item.failed",
	"payment.payouts-item.held",
	"payment.payouts-item.refunded",
	"payment.payouts-item.returned",
	"payment.payouts-item.succeeded",
	"payment.payouts-item.unclaimed",
	"payment.sale.completed",
	"payment.sale.denied",
	"payment.sale.pending",
	"payment.sale.refunded",
	"payment.sale.reversed",
	"risk.dispute.created",
	"vault.credit-card.created",
	"vault.credit-card.deleted",
	"vault.credit-card.updated",
}

WEBHOOK_SIGNALS = {
	hook: Signal(providing_args=["event"]) for hook in WEBHOOK_EVENT_TYPES
}


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
		if created:
			ret.send_signal()
		return ret

	@property
	def resource_model(self):
		resource_type = self.resource_type.lower()
		if resource_type == "agreement":
			from .billing import BillingAgreement
			return BillingAgreement
		elif resource_type == "dispute":
			from .disputes import Dispute
			return Dispute
		elif resource_type == "plan":
			from .billing import BillingPlan
			return BillingPlan
		elif resource_type == "refund":
			from .payments import Refund
			return Refund
		if resource_type == "sale":
			from .payments import Sale
			return Sale
		raise NotImplementedError("Unimplemented webhook resource: %r" % (self.resource_type))

	def create_or_update_resource(self):
		if self.event_type.lower().startswith("risk.dispute."):
			# risk.dispute.* events are a different kind of dispute object.
			# Also, who the **** knows what these objects actually are.
			# TODO: Get/Create the actual dispute object.
			# Depends on SDK implementation which is currently missing:
			# https://github.com/paypal/PayPal-Python-SDK/issues/216
			return

		model = self.resource_model
		return model.get_or_update_from_api_data(self.resource)

	def get_resource(self):
		cls = self.resource_model
		return cls.objects.get(id=self.resource[cls.id_field_name])

	def send_signal(self):
		event_type = self.event_type.lower()
		signal = WEBHOOK_SIGNALS.get(event_type)
		if signal:
			signal.send(sender=self.__class__, event=self)


class WebhookEventTrigger(models.Model):
	id = models.BigAutoField(primary_key=True)
	remote_ip = models.GenericIPAddressField(
		help_text="IP address of the request client."
	)
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

		ip = request.META["REMOTE_ADDR"]
		obj = cls.objects.create(headers=headers, body=body, remote_ip=ip)

		try:
			obj.valid = obj.verify(PAYPAL_WEBHOOK_ID)
			if obj.valid:
				# Process the item (do not save it, it'll get saved below)
				obj.process(save=False)
		except Exception as e:
			max_length = WebhookEventTrigger._meta.get_field("exception").max_length
			obj.exception = str(e)[:max_length]
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
		self.webhook_event = WebhookEvent.process(self.data)
		self.processed = True
		self.exception = ""
		self.traceback = ""
		if save:
			self.save()

		return self.webhook_event


def webhook_handler(*event_types):
	"""
	Decorator that registers a function as a webhook handler.

	Usage examples:

	>>> # Hook a single event
	>>> @webhook_handler("payment.sale.completed")
	>>> def on_payment_received(event):
	>>>     payment = event.get_resource()
	>>>     print("Received payment:", payment)

	>>> # Multiple events supported
	>>> @webhook_handler("billing.subscription.suspended", "billing.subscription.cancelled")
	>>> def on_subscription_stop(event):
	>>>     subscription = event.get_resource()
	>>>     print("Stopping subscription:", subscription)

	>>> # Using a wildcard works as well
	>>> @webhook_handler("billing.subscription.*")
	>>> def on_subscription_update(event):
	>>>     subscription = event.get_resource()
	>>>     print("Updated subscription:", subscription)
	"""

	# First expand all wildcards and verify the event types are valid
	event_types_to_register = set()
	for event_type in event_types:
		# Always convert to lowercase
		event_type = event_type.lower()
		if "*" in event_type:
			# expand it
			for t in WEBHOOK_EVENT_TYPES:
				if fnmatch(t, event_type):
					event_types_to_register.add(t)
		elif event_type not in WEBHOOK_EVENT_TYPES:
			raise ValueError("Unknown webhook event: %r" % (event_type))
		else:
			event_types_to_register.add(event_type)

	# Now register them
	def decorator(func):
		for event_type in event_types_to_register:
			WEBHOOK_SIGNALS[event_type].connect(func)
		return func

	return decorator
