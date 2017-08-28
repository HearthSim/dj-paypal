from django.core.management import BaseCommand
from djpaypal import models
from paypalrestsdk import payments as paypal_models


class Command(BaseCommand):
	help = "Syncs plan data from upstream Paypal"

	def handle(self, *args, **options):
		for status in ("created", "active"):
			all_plans = paypal_models.BillingPlan.all({"status": status})
			models.BillingPlan.objects.sync_data(all_plans.plans)
