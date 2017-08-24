import pytest
from iso8601 import parse_date
from djpaypal import enums, models, settings
from .conftest import get_fixture


def test_settings():
	assert settings.PAYPAL_MODE == "sandbox"


@pytest.mark.django_db
def test_sync_all_active_plans():
	all_plans = get_fixture("rest.billingplan.all.active.json")
	models.BillingPlan.objects.sync_data(all_plans["plans"])

	assert models.BillingPlan.objects.count() == len(all_plans["plans"])

	for plan in all_plans["plans"]:
		plan_obj = get_fixture(
			"GET/v1/payments/billing-plans/{id}.json".format(id=plan["id"])
		)
		plan = models.BillingPlan.objects.get(id=plan_obj["id"])
		assert plan.id == plan_obj["id"]
		assert plan.state == getattr(enums.BillingPlanState, plan_obj["state"])
		assert plan.type == getattr(enums.BillingPlanType, plan_obj["type"])
		assert plan.name == plan_obj["name"]
		assert plan.description == plan_obj["description"]
		assert plan.merchant_preferences == plan_obj["merchant_preferences"]
		assert plan.create_time == parse_date(plan_obj["create_time"])
		assert plan.update_time == parse_date(plan_obj["update_time"])

		for definition in plan_obj["payment_definitions"]:
			pd = models.PaymentDefinition.objects.get(id=definition["id"])
			assert pd.id == definition["id"]
			assert pd.name == definition["name"]
			assert pd.type == getattr(enums.PaymentDefinitionType, definition["type"])
			assert plan.payment_definitions.filter(id=pd.id).count() == 1


@pytest.mark.django_db
def test_sync_executed_billing_agreement():
	ba = get_fixture("rest.billingagreement.execute.json")
	inst, created = models.BillingAgreement.get_or_update_from_api_data(ba, always_sync=True)
	assert created
	assert inst.id == ba["id"]


def test_token_extract_billing_agreement():
	token = "EC-XXXXXXXX00000000Z"
	url = (
		"https://api.sandbox.paypal.com/v1/payments/billing-agreements/" +
		token + "/agreement-execute"
	)
	links = {"links": [{"href": url, "method": "POST", "rel": "execute"}]}
	assert models.PreparedBillingAgreement._extract_token(links) == token
