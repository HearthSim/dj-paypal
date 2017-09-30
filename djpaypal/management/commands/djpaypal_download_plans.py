from django.core.management import BaseCommand
from paypalrestsdk import payments as paypal_models

from djpaypal import models


class Command(BaseCommand):
	help = "Syncs plan data from upstream Paypal"

	def handle(self, *args, **options):
		for status in ("created", "active"):
			all_plans = paypal_models.BillingPlan.all({"status": status})
			if all_plans.plans is None:
				continue
			models.BillingPlan.objects.sync_data(all_plans.plans)
