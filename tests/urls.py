from django.contrib import admin
from django.urls import re_path

from djpaypal.views import ProcessWebhookView


urlpatterns = [
	re_path(r"^admin/", admin.site.urls),
	re_path(r"^paypal/webhook/$", ProcessWebhookView.as_view(), name="paypal_webhook"),
]
