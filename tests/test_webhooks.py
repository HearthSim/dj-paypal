import json
from unittest import mock

import pytest

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
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["dispute_id"] == resource["dispute_id"]
	assert models.Dispute.objects.get(id=resource["dispute_id"])


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
