import json
from datetime import timedelta
from unittest import mock

import pytest
from django.utils import timezone

from djpaypal import models
from djpaypal.models.webhooks import webhook_handler

from .conftest import get_fixture


def signal_template(sender, event, **kwargs):
	pass


def make_fake_signal(*event_types):
	return webhook_handler(*event_types)(
		mock.create_autospec(signal_template)
	)


always_triggers = make_fake_signal("*")
on_subscription = make_fake_signal("billing.subscription.*")
on_subscription_created = make_fake_signal("billing.subscription.created")


def get_webhook_from_fixture(event_type):
	always_triggers.reset_mock()
	on_subscription.reset_mock()
	on_subscription_created.reset_mock()
	data = get_fixture("webhooks/{event_type}.json".format(event_type=event_type))
	webhook = models.WebhookEventTrigger(
		headers={}, body=json.dumps(data), remote_ip="0.0.0.0"
	)
	webhook.save()
	webhook.process()
	return data, data["resource"], webhook


@pytest.mark.django_db
def test_webhook_billing_plan_created():
	data, resource, webhook = get_webhook_from_fixture("billing.plan.created")
	always_triggers.assert_called_once()
	on_subscription.assert_not_called()
	on_subscription_created.assert_not_called()
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["id"] == resource["id"]
	assert models.BillingPlan.objects.get(id=resource["id"])


@pytest.mark.django_db
def test_webhook_billing_subscription_created_then_cancelled():
	data, resource, webhook = get_webhook_from_fixture("billing.subscription.created")
	always_triggers.assert_called_once()
	on_subscription.assert_called_once()
	on_subscription_created.assert_called_once()
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["id"] == resource["id"]
	assert models.BillingAgreement.objects.get(id=resource["id"])
	assert models.BillingAgreement.objects.get(id=resource["id"]).state == "Pending"

	# Cancel the subscription
	data, resource, webhook = get_webhook_from_fixture("billing.subscription.cancelled")
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["id"] == resource["id"]
	assert models.BillingAgreement.objects.get(id=resource["id"]).state == "Cancelled"


@pytest.mark.django_db
def test_webhook_customer_dispute_created():
	data, resource, webhook = get_webhook_from_fixture("customer.dispute.created")
	webhook_resource = webhook.webhook_event.resource
	assert webhook.webhook_event.id == data["id"]
	assert webhook_resource["dispute_id"] == resource["dispute_id"]
	assert models.Dispute.objects.get(dispute_id=resource["dispute_id"])

	# https://github.com/paypal/PayPal-REST-API-issues/issues/214
	data, resource, webhook = get_webhook_from_fixture("customer.dispute.created--ppra214")
	webhook_resource = webhook.webhook_event.resource
	assert webhook.webhook_event.id == data["id"]
	assert webhook_resource["dispute_id"] == resource["dispute_id"]
	assert webhook_resource["dispute_channel"] == resource["dispute_channel"]
	assert webhook_resource["dispute_life_cycle_stage"] == resource["dispute_life_cycle_stage"]
	assert models.Dispute.objects.get(dispute_id=resource["dispute_id"])

	data, resource, webhook = get_webhook_from_fixture("customer.dispute.created--2019-11")
	webhook_resource = webhook.webhook_event.resource
	assert webhook.webhook_event.id == data["id"]
	assert webhook_resource["messages"] == resource["messages"]
	assert webhook_resource["refund_details"] == resource["refund_details"]
	assert webhook_resource["buyer_response_due_date"] == resource["buyer_response_due_date"]
	assert webhook_resource["seller_response_due_date"] == resource["seller_response_due_date"]
	assert models.Dispute.objects.get(dispute_id=resource["dispute_id"])


@pytest.mark.django_db
def test_webhook_risk_dispute_created():
	data, resource, webhook = get_webhook_from_fixture("customer.dispute.created")
	assert webhook.webhook_event.id == data["id"]
	# TODO: ensure actual Dispute object is created
	# Depends on https://github.com/paypal/PayPal-Python-SDK/issues/216


@pytest.mark.django_db
def test_webhook_payment_sale_completed():
	data, resource, webhook = get_webhook_from_fixture("payment.sale.completed")
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["id"] == resource["id"]
	assert models.Sale.objects.get(id=resource["id"])


@pytest.mark.django_db
def test_webhook_payment_sale_completed_from_subscription():
	data, resource, webhook = get_webhook_from_fixture(
		"payment.sale.completed--from-subscription"
	)
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["id"] == resource["id"]
	assert models.Sale.objects.get(id=resource["id"])


SANDBOX_CERT_URL = (
	"https://api.sandbox.paypal.com/v1/notifications/certs/CERT-00000000-00000000-00000000"
)


def format_transmission_time(dt):
	return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def post_webhook(client, body, cert_url=SANDBOX_CERT_URL, transmission_time=None):
	if transmission_time is None:
		transmission_time = format_transmission_time(timezone.now())
	return client.post(
		"/paypal/webhook/",
		data=body,
		content_type="application/json",
		HTTP_PAYPAL_TRANSMISSION_ID="b2384410-f8d2-11e7-9a2d-4f8d6d2e8f9a",
		HTTP_PAYPAL_TRANSMISSION_TIME=transmission_time,
		HTTP_PAYPAL_TRANSMISSION_SIG="c2lnbmF0dXJl",
		HTTP_PAYPAL_AUTH_ALGO="SHA256withRSA",
		HTTP_PAYPAL_CERT_URL=cert_url,
	)


@pytest.mark.django_db
@pytest.mark.parametrize("cert_url", [
	"",
	"http://169.254.169.254/latest/meta-data/",
	"http://api.sandbox.paypal.com/v1/notifications/certs/CERT-1",
	"https://api.sandbox.paypal.com.example.com/v1/notifications/certs/CERT-1",
	"https://example.com/?https://api.sandbox.paypal.com/v1/notifications/certs/CERT-1",
	"https://user@api.sandbox.paypal.com/v1/notifications/certs/CERT-1",
	"https://api.sandbox.paypal.com:8443/v1/notifications/certs/CERT-1",
	"https://api.sandbox.paypal.com/v1/oauth2/token",
	"https://api.sandbox.paypal.com/v1/notifications/certs/../../oauth2/token",
	"https://api.sandbox.paypal.com/v1/notifications/certs/CERT-1?redirect=1",
	"https://api.paypal.com/v1/notifications/certs/CERT-1",
])
def test_webhook_view_rejects_untrusted_cert_url_without_fetching(client, cert_url):
	with mock.patch("requests.get") as requests_get:
		response = post_webhook(client, "{}", cert_url=cert_url)

	assert response.status_code == 400
	requests_get.assert_not_called()
	assert not models.WebhookEventTrigger.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("transmission_time", [
	"",
	"not a date",
	"2018-01-15T12:00:00",
	format_transmission_time(timezone.now() - timedelta(hours=1)),
	format_transmission_time(timezone.now() + timedelta(hours=1)),
], ids=["empty", "invalid", "naive", "past", "future"])
def test_webhook_view_rejects_stale_transmission_without_fetching(
	client, transmission_time
):
	with mock.patch("requests.get") as requests_get:
		response = post_webhook(client, "{}", transmission_time=transmission_time)

	assert response.status_code == 400
	requests_get.assert_not_called()
	assert not models.WebhookEventTrigger.objects.exists()


@pytest.mark.django_db
def test_webhook_view_processes_verified_event(client):
	data = get_fixture("webhooks/billing.subscription.created.json")
	on_subscription_created.reset_mock()
	cert_response = mock.Mock(status_code=200)
	cert_response.iter_content.return_value = [b"-----BEGIN CERTIFICATE-----"]
	cert = mock.sentinel.cert

	sdk_webhook_event = models.webhooks.paypal_models.WebhookEvent

	with mock.patch("requests.get", return_value=cert_response) as requests_get, \
		mock.patch("OpenSSL.crypto.load_certificate", return_value=cert), \
		mock.patch.object(sdk_webhook_event, "_verify_certificate") as verify_certificate, \
		mock.patch.object(sdk_webhook_event, "_verify_signature") as verify_signature:
		verify_certificate.return_value = True
		verify_signature.return_value = True
		response = post_webhook(client, json.dumps(data))

	assert response.status_code == 200
	requests_get.assert_called_once_with(
		SANDBOX_CERT_URL, timeout=mock.ANY, allow_redirects=False, stream=True
	)
	verify_certificate.assert_called_once_with(cert)
	assert verify_signature.call_args.kwargs["cert"] is cert
	assert verify_signature.call_args.kwargs["auth_algo"] == "sha256WithRSAEncryption"

	trigger = models.WebhookEventTrigger.objects.get()
	assert response.content.decode() == str(trigger.id)
	assert trigger.valid
	assert trigger.processed
	assert trigger.webhook_event.id == data["id"]
	on_subscription_created.assert_called_once()
	assert models.BillingAgreement.objects.get(id=data["resource"]["id"]).state == "Pending"
