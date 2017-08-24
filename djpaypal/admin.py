from django.contrib import admin

from . import models


def activate_plans(admin, request, queryset):
	for obj in queryset:
		obj.activate()


@admin.register(models.BillingPlan)
class BillingPlanAdmin(admin.ModelAdmin):
	list_display = ("__str__", "state", "type", "create_time", "livemode")
	list_filter = ("type", "state", "create_time", "update_time", "livemode")
	actions = (activate_plans, )


@admin.register(models.BillingAgreement)
class BillingAgreementAdmin(admin.ModelAdmin):
	list_display = ("__str__", "user", "state", "livemode")
	list_filter = ("state", )
	raw_id_fields = ("user", )


@admin.register(models.PreparedBillingAgreement)
class PreparedBillingAgreementAdmin(admin.ModelAdmin):
	list_display = ("__str__", "user", "livemode")
	list_filter = ("livemode", )
	raw_id_fields = ("user", )


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
