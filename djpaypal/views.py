from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import WebhookEventTrigger


@method_decorator(csrf_exempt, name="dispatch")
class ProcessWebhookView(View):
	"""
	A Paypal Webhook handler view.

	This will create a WebhookEventTrigger instance, verify it,
	then attempt to process it.

	If the webhook cannot be verified, returns HTTP 400.

	If an exception happens during processing, returns HTTP 500.
	"""
	def post(self, request):
		if "HTTP_PAYPAL_TRANSMISSION_ID" not in request.META:
			# Do not even attempt to process/store the event if there is
			# no paypal transmission id so we avoid overfilling the db.
			return HttpResponseBadRequest()

		trigger = WebhookEventTrigger.from_request(request)

		if trigger.exception:
			# An exception happened, return 500
			return HttpResponseServerError()

		if not trigger.valid:
			# Webhook Event did not validate, return 400
			return HttpResponseBadRequest()

		return HttpResponse(str(trigger.id))
