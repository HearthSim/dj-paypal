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
	list_display = ("__str__", "type", "livemode")
	list_filter = ("type", "livemode")


@admin.register(models.PaymentDefinition)
class PaymentDefinitionAdmin(admin.ModelAdmin):
	list_display = (
		"__str__", "type", "frequency", "frequency_interval", "cycles", "livemode"
	)
	list_filter = ("type", "frequency", "livemode")
	raw_id_fields = ("charge_models", )


@admin.register(models.Sale)
class SaleAdmin(admin.ModelAdmin):
	date_hierarchy = "create_time"
	list_display = ("__str__", "state", "create_time", "update_time", "livemode")
	list_filter = ("state", "payment_mode", "livemode")
	raw_id_fields = ("billing_agreement", "parent_payment")
	readonly_fields = (
		"id", "amount", "payment_mode", "state", "reason_code",
		"protection_eligibility", "protection_eligibility_type",
		"clearing_time", "transaction_fee", "receivable_amount",
		"exchange_rate", "fmf_details", "receipt_id", "parent_payment",
		"processor_response", "billing_agreement", "create_time",
		"update_time",
	)
	search_fields = ("id", "receipt_id")

	def has_add_permission(self, request):
		return False


@admin.register(models.WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
	list_filter = ("create_time", "livemode")

	def has_add_permission(self, request):
		return False
