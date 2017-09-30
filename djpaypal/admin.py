from django.contrib import admin

from . import models
from .settings import PAYPAL_WEBHOOK_ID


class BasePaypalObjectAdmin(admin.ModelAdmin):
	_common_fields = ("id", "djpaypal_created", "djpaypal_updated", "livemode")
	change_form_template = "djpaypal/admin/change_form.html"

	def get_fieldsets(self, request, obj=None):
		# Have to remove the fields from the common set, otherwise they'll show up twice.
		fields = [f for f in self.get_fields(request, obj) if f not in self._common_fields]
		return (
			(None, {"fields": self._common_fields}),
			(self.model.__name__, {"fields": fields}),
		)

	def get_list_display(self, request):
		return ("__str__", ) + self.list_display + self._common_fields[1:]

	def get_list_filter(self, request):
		return self.list_filter + ("livemode", )

	def get_readonly_fields(self, request, obj=None):
		return self.readonly_fields + self._common_fields

	def get_search_fields(self, request):
		return self.search_fields + ("id", )

	def has_add_permission(self, request):
		return False


@admin.register(models.BillingPlan)
class BillingPlanAdmin(BasePaypalObjectAdmin):
	list_display = ("state", "type", "create_time")
	list_filter = ("type", "state", "create_time", "update_time")
	raw_id_fields = ("payment_definitions", )

	def activate_plans(self, request, queryset):
		for obj in queryset:
			obj.activate()

	actions = (activate_plans, )


@admin.register(models.BillingAgreement)
class BillingAgreementAdmin(BasePaypalObjectAdmin):
	list_display = ("user", "state")
	list_filter = ("state", )
	raw_id_fields = ("user", "payer_model")


@admin.register(models.PreparedBillingAgreement)
class PreparedBillingAgreementAdmin(admin.ModelAdmin):
	list_display = (
		"__str__", "user", "executed_agreement", "executed_at", "created", "updated", "livemode"
	)
	list_filter = ("livemode", "executed_at")
	readonly_fields = ("id", "created", "updated")
	raw_id_fields = ("user", "executed_agreement")

	def has_add_permission(self, request):
		return False


@admin.register(models.ChargeModel)
class ChargeModelAdmin(BasePaypalObjectAdmin):
	list_display = ("type", )
	list_filter = ("type", )


@admin.register(models.Dispute)
class DisputeAdmin(BasePaypalObjectAdmin):
	list_display = ("status", "reason", "create_time")
	list_filter = ("status", "reason")
	readonly_fields = (
		"create_time", "update_time", "disputed_transactions", "reason",
		"dispute_amount", "dispute_outcome", "seller_response_due_date", "dispute_flow"
	)


@admin.register(models.Payer)
class PayerAdmin(admin.ModelAdmin):
	list_display = (
		"__str__", "first_name", "last_name", "email", "user", "livemode"
	)
	search_fields = ("id", "first_name", "last_name", "email")
	raw_id_fields = ("user", )

	def has_add_permission(self, request):
		return False


@admin.register(models.PaymentDefinition)
class PaymentDefinitionAdmin(BasePaypalObjectAdmin):
	list_display = (
		"type", "frequency", "frequency_interval", "cycles",
	)
	list_filter = ("type", "frequency")
	raw_id_fields = ("charge_models", )


@admin.register(models.Refund)
class RefundAdmin(BasePaypalObjectAdmin):
	date_hierarchy = "create_time"
	list_display = (
		"state", "invoice_number", "refund_reason_code", "create_time",
	)
	list_filter = ("refund_reason_code", )
	raw_id_fields = ("sale", "parent_payment")
	readonly_fields = (
		"state", "sale", "parent_payment", "refund_reason_code",
		"refund_funding_type", "create_time", "update_time",
	)


@admin.register(models.Sale)
class SaleAdmin(BasePaypalObjectAdmin):
	date_hierarchy = "create_time"
	list_display = ("state", "create_time", "update_time")
	list_filter = ("state", "payment_mode")
	raw_id_fields = ("billing_agreement", "parent_payment")
	readonly_fields = (
		"amount", "payment_mode", "state", "reason_code",
		"protection_eligibility", "protection_eligibility_type",
		"clearing_time", "transaction_fee", "receivable_amount",
		"exchange_rate", "fmf_details", "receipt_id", "parent_payment",
		"processor_response", "billing_agreement", "soft_descriptor",
		"create_time", "update_time",
	)
	search_fields = ("receipt_id", )


@admin.register(models.WebhookEvent)
class WebhookEventAdmin(BasePaypalObjectAdmin):
	list_display = ("event_type", "resource_type", "create_time")
	list_filter = ("create_time", )
	ordering = ("-create_time", )
	readonly_fields = (
		"summary", "event_type", "resource_type", "create_time",
		"event_version", "resource", "status", "transmissions",
	)


@admin.register(models.WebhookEventTrigger)
class WebhookEventTriggerAdmin(admin.ModelAdmin):
	list_display = (
		"created", "updated", "valid", "processed", "exception", "webhook_event"
	)
	list_filter = ("created", "valid", "processed")
	raw_id_fields = ("webhook_event", )

	def reverify(self, request, queryset):
		for trigger in queryset:
			if trigger.verify(webhook_id=PAYPAL_WEBHOOK_ID):
				trigger.valid = True
				trigger.save()

	def reprocess(self, request, queryset):
		for trigger in queryset:
			if not trigger.valid:
				# Skip invalid webhooks (never process them)
				continue
			trigger.process()

	def has_add_permission(self, request):
		return False

	actions = (reverify, reprocess)
