import pytest
from djpaypal import models
from paypalrestsdk import payments as paypal_models


@pytest.mark.django_db
def test_sale_sync():
	sale_id = "7D51924877811803R"
	sale = paypal_models.Sale.find(sale_id)
	assert sale.id == sale_id
	db_sale, created = models.Sale.get_or_update_from_api_data(sale)
	assert created
	assert db_sale.id == sale_id
