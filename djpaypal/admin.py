from django.contrib import admin

from . import models


@admin.register(models.BillingPlan)
class BillingPlanAdmin(admin.ModelAdmin):
	pass


@admin.register(models.ChargeModel)
class ChargeModelAdmin(admin.ModelAdmin):
	pass


@admin.register(models.PaymentDefinition)
class PaymentDefinitionAdmin(admin.ModelAdmin):
	pass


@admin.register(models.Webhook)
class WebhookAdmin(admin.ModelAdmin):
	pass
