from django.utils.translation import ugettext as _
from djstripe.enums import Enum


class PaypalBool(Enum):
	YES = _("Yes")
	NO = _("No")


class BillingAgreementState(Enum):
	Active = _("Active")
	Cancelled = _("Cancelled")
	Completed = _("Completed")
	Created = _("Created")
	Pending = _("Pending")
	Reactivated = _("Reactivated")
	Suspended = _("Suspended")


class BillingPlanState(Enum):
	CREATED = _("Created")
	ACTIVE = _("Active")
	INACTIVE = _("Inactive")
	DELETED = _("Deleted")


class BillingPlanType(Enum):
	FIXED = _("Fixed")
	INFINITE = _("Infinite")


class ChargeModelType(Enum):
	TAX = _("Tax")
	SHIPPING = _("Shipping")


class PaymentDefinitionFrequency(Enum):
	DAY = _("Day")
	WEEK = _("Week")
	MONTH = _("Month")
	YEAR = _("Year")


class PaymentDefinitionType(Enum):
	TRIAL = _("Trial")
	REGULAR = _("Regular")


class TermsType(Enum):
	WEEKLY = _("Weekly")
	MONTHLY = _("Monthly")
	YEARLY = _("Yearly")


class JsonPatchOp(Enum):
	add = _("add")
	remove = _("remove")
	replace = _("replace")
	move = _("move")
	copy = _("copy")
	test = _("test")


class PaypalAction(Enum):
	CONTINUE = _("Continue")
	CANCEL = _("Cancel")


class SalePaymentMode(Enum):
	INSTANT_TRANSFER = _("Instant transfer")
	MANUAL_BANK_TRANSFER = _("Manual bank transfer")
	DELAYED_TRANSFER = _("Delayed transfer")
	ECHECK = _("eCheck")


class SaleState(Enum):
	completed = _("Completed")
	partially_refunded = _("Partially refunded")
	pending = _("Pending")
	refunded = _("Refunded")
	denied = _("Denied")


class SaleReasonCode(Enum):
	CHARGEBACK = _("Chargeback")
	GUARANTEE = _("Guarantee")
	BUYER_COMPLAINT = _("Buyer complaint")
	REFUND = _("Refund")
	UNCONFIRMED_SHIPPING_ADDRESS = _("Unconfirmed shipping address")
	ECHECK = _("eCheck")
	INTERNATIONAL_WITHDRAWAL = _("International withdrawal")
	RECEIVING_PREFERENCE_MANDATES_MANUAL_ACTION = _(
		"Receiving preference mandates manual action"
	)
	PAYMENT_REVIEW = _("Payment review")
	REGULATORY_REVIEW = _("Regulatory review")
	UNILATERAL = _("Unilateral")
	VERIFICATION_REQUIRED = _("Verification required")
	TRANSACTION_APPROVED_AWAITING_FUNDING = _("Transaction approved awaiting funding")


class SaleProtectionEligibility(Enum):
	ELIGIBLE = _("Eligible")
	PARTIALLY_ELIGIBLE = _("Partially eligible")
	INELIGIBLE = _("Ineligible")


class SaleProtectionEligibilityType(Enum):
	ITEM_NOT_RECEIVED_ELIGIBLE = _("Item not received eligible")
	UNAUTHORIZED_PAYMENT_ELIGIBLE = _("Unauthorized payment eligible")
	BOTH = (_("Both"), "ITEM_NOT_RECEIVED_ELIGIBLE,UNAUTHORIZED_PAYMENT_ELIGIBLE")
