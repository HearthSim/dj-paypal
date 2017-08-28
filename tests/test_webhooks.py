import json
import pytest
from djpaypal import models
from .conftest import get_fixture


@pytest.mark.django_db
def test_webhook_billing_subscription_created():
	data = get_fixture("webhooks/billing.subscription.created.json")
	resource = data["resource"]
	webhook = models.WebhookEventTrigger(headers={}, body=json.dumps(data))
	webhook.save()
	webhook.process()
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["id"] == resource["id"]
	assert models.BillingAgreement.objects.get(id=resource["id"])


@pytest.mark.django_db
def test_webhook_customer_dispute_created():
	data = get_fixture("webhooks/customer.dispute.created.json")
	resource = data["resource"]
	webhook = models.WebhookEventTrigger(headers={}, body=json.dumps(data))
	webhook.save()
	webhook.process()
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["dispute_id"] == resource["dispute_id"]
	assert models.Dispute.objects.get(id=resource["dispute_id"])


@pytest.mark.django_db
def test_webhook_payment_sale_completed():
	data = get_fixture("webhooks/payment.sale.completed.json")
	resource = data["resource"]
	webhook = models.WebhookEventTrigger(headers={}, body=json.dumps(data))
	webhook.save()
	webhook.process()
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["id"] == resource["id"]
	assert models.Sale.objects.get(id=resource["id"])


@pytest.mark.django_db
def test_webhook_payment_sae_completed_from_subscription():
	data = get_fixture("webhooks/payment.sale.completed--from-subscription.json")
	resource = data["resource"]
	webhook = models.WebhookEventTrigger(headers={}, body=json.dumps(data))
	webhook.save()
	webhook.process()
	assert webhook.webhook_event.id == data["id"]
	assert webhook.webhook_event.resource["id"] == resource["id"]
	assert models.Sale.objects.get(id=resource["id"])
