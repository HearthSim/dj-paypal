from django.utils.translation import ugettext as _
from djstripe.enums import Enum


class PaypalBool(Enum):
	YES = _("Yes")
	NO = _("No")


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
