from django.core.management import BaseCommand

from djpaypal import models


class Command(BaseCommand):
	help = "Delete all locally-stored test data (sandbox data)"

	def handle(self, *args, **options):
		# The order of the models matters because of PROTECT foreignkeys
		for model in (
			models.PreparedBillingAgreement, models.Sale,
			models.BillingAgreement, models.BillingPlan, models.ChargeModel,
			models.Dispute, models.Payer, models.PaymentDefinition,
			models.WebhookEvent,
		):
			deleted, objs = model.objects.filter(livemode=False).delete()
			self.stdout.write("Deleted {amt} {cls} objects".format(
				amt=deleted, cls=model.__name__
			))
			# Note: We do not delete WebhookEventTrigger instances (no livemode)
