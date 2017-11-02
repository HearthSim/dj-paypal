import pytest

from djpaypal import models

from .conftest import get_fixture


@pytest.mark.django_db
def test_billingagreement_admin_view(admin_client):
	ba = get_fixture("rest.billingagreement.execute.json")
	inst, created = models.BillingAgreement.get_or_update_from_api_data(ba, always_sync=True)

	response = admin_client.get("/admin/djpaypal/billingagreement/{}/change/".format(inst.id))
	assert response.status_code == 200
