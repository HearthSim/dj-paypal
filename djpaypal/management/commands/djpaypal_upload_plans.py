from django.conf import settings
from django.core.management import BaseCommand

from djpaypal import models


class Command(BaseCommand):
	help = "Create plans on Paypal from settings.PAYPAL_PLANS"

	def handle(self, *args, **options):
		for name, plan in settings.PAYPAL_PLANS.items():
			self.stdout.write("Creating plan %r..." % (name))
			obj = models.BillingPlan.create(plan, activate=True)
			self.stdout.write("Created plan: %r (%r)" % (obj, obj.id))
