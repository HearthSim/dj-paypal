from django.contrib import admin

from . import models


@admin.register(models.BillingPlan)
class BillingPlanAdmin(admin.ModelAdmin):
	list_filter = ("type", "state", "create_time", "update_time", "livemode")


@admin.register(models.ChargeModel)
class ChargeModelAdmin(admin.ModelAdmin):
	list_filter = ("type", "livemode")


@admin.register(models.PaymentDefinition)
class PaymentDefinitionAdmin(admin.ModelAdmin):
	list_filter = ("type", "frequency", "livemode")


@admin.register(models.Webhook)
class WebhookAdmin(admin.ModelAdmin):
	list_filter = ("create_time", "livemode")

	def has_add_permission(self, request):
		return False
