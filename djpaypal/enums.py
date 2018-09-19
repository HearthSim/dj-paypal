import operator
from collections import OrderedDict

from django.utils.translation import ugettext as _


class EnumMetaClass(type):
	@classmethod
	def __prepare__(self, name, bases):
		return OrderedDict()

	def __new__(self, name, bases, classdict):
		members = []
		keys = {}
		choices = OrderedDict()
		for key, value in classdict.items():
			if key.startswith("__"):
				continue
			members.append(key)
			if isinstance(value, tuple):
				value, alias = value
				keys[alias] = key
			else:
				alias = None
			keys[alias or key] = key
			choices[alias or key] = value

		for k, v in keys.items():
			classdict[v] = k

		classdict["__choices__"] = choices
		classdict["__members__"] = members

		# Note: Differences between Python 2.x and Python 3.x force us to
		# explicitly use unicode here, and to explicitly sort the list. In
		# Python 2.x, class members are unordered and so the ordering will
		# vary on different systems based on internal hashing. Without this
		# Django will continually require new no-op migrations.
		classdict["choices"] = tuple(
			(str(k), str(v))
			for k, v in sorted(choices.items(), key=operator.itemgetter(0))
		)

		return type.__new__(self, name, bases, classdict)


class Enum(metaclass=EnumMetaClass):
	pass


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


class DisputeChannel(Enum):
	INTERNAL = _("Internal")
	EXTERNAL = _("External")


class DisputeLifecycleStage(Enum):
	INQUIRY = _("Inquiry")
	CHARGEBACK = _("Chargeback")
	PRE_ARBITRATION = _("Pre-arbitration")
	ARBITRATION = _("Arbitration")


class DisputeFlow(Enum):
	ACH_RETURNS = _("ACH returns")
	ACCOUNT_ISSUES = _("Account issues")
	ADMIN_FRAUD_REVERSAL = _("Admin fraud reversal")
	BILLING = _("Billing")
	CHARGEBACKS = _("Chargebacks")
	COMPLAINT_RESOLUTION = _("Complaint resolution")
	CORRECTION = _("Correction")
	DEBIT_CARD_CHARGEBACK = _("Debit card chargeback")
	FAX_ROUTING = _("Fax routing")
	MIPS_COMPLAINT_ITEM = _("MIPS complaint item")
	MIPS_COMPLAINT = _("MIPS complaint")
	OPS_VERIFICATION_FLOW = _("OPS verification flow")
	PAYPAL_DISPUTE_RESOLUTION = _("Paypal dispute resolution")
	PINLESS_DEBIT_RETURN = _("Pinless debit return")
	PRICING_ADJUSTMENT = _("Pricing adjustment")
	SPOOF_UNAUTH_CHILD = _("Spoof Unauth Child")
	SPOOF_UNAUTH_PARENT = _("Spoof Unauth Parent")
	THIRD_PARTY_CLAIM = _("Third party claim")
	THIRD_PARTY_DISPUTE = _("Third party dispute")
	TICKET_RETRIEVAL = _("Ticket retrieval")
	UK_EXPRESS_RETURNS = _("UK Express returns")
	UNKNOWN_FAXES = _("Unknown faxes")
	VETTING = _("Vetting")
	OTHER = _("Other")


class DisputeReason(Enum):
	MERCHANDISE_OR_SERVICE_NOT_RECEIVED = _("Merchandise or service not received")
	MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED = _("Merchandise or service not as described")
	UNAUTHORISED = _("Unauthorized")
	CREDIT_NOT_PROCESSED = _("Credit not processed")
	DUPLICATE_TRANSACTION = _("Duplicate transaction")
	INCORRECT_AMOUNT = _("Incorrect amount")
	PAYMENT_BY_OTHER_MEANS = _("Payment by other means")
	CANCELED_RECURRING_BILLING = _("Canceled recurring billing")
	PROBLEM_WITH_REMITTANCE = _("Problem occurred with the remittance")
	OTHER = _("Other")


class DisputeStatus(Enum):
	OPEN = _("Open")
	WAITING_FOR_BUYER_RESPONSE = _("Waiting for buyer response")
	WAITING_FOR_SELLER_RESPONSE = _("Waiting for seller response")
	UNDER_REVIEW = _("Under review")
	RESOLVED = _("Resolved")
	OTHER = _("Other")


class PaymentDefinitionFrequency(Enum):
	DAY = _("Day")
	WEEK = _("Week")
	MONTH = _("Month")
	YEAR = _("Year")


class PaymentDefinitionType(Enum):
	TRIAL = _("Trial")
	REGULAR = _("Regular")


class PaymentFailureReason(Enum):
	UNABLE_TO_COMPLETE_TRANSACTION = _("Unable to complete transaction")
	INVALID_PAYMENT_METHOD = _("Invalid payment method")
	PAYER_CANNOT_PAY = _("Payer cannot pay")
	CANNOT_PAY_THIS_PAYEE = _("Cannot pay this payee")
	REDIRECT_REQUIRED = _("Redirect required")
	PAYEE_FILTER_RESTRICTIONS = _("Payee filter restrictions")


class PaymentIntent(Enum):
	sale = _("Sale")
	authorize = _("Authorize")
	order = _("Order")


class PaymentState(Enum):
	created = _("Created")
	approved = _("Approved")
	failed = _("Failed")


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


class RefundFundingType(Enum):
	PAYOUT = _("Payout")


class RefundPendingReasonCode(Enum):
	ECHECK = _("eCheck")


class RefundReasonCode(Enum):
	ADJUSTMENT_REVERSAL = _("Adjustment reversal")
	ADMIN_FRAUD_REVERSAL = _("Admin fraud reversal")
	ADMIN_REVERSAL = _("Admin reversal")
	APPEAL = _("Appeal")
	BUYER_COMPLAINT = _("Buyer complaint")
	CHARGEBACK = _("Chargeback")
	CHARGEBACK_SETTLEMENT = _("Chargeback settlement")
	DENIED = _("Denied")
	DISPUTE_PAYOUT = _("Dispute payout")
	FUNDING = _("Funding")
	GUARANTEE = _("Guarantee")
	LIMITS = _("Limits")
	NO_FAULT = _("No fault")
	OTHER = _("Other")
	REFUND = _("Refund")
	REGULATORY_BLOCK = _("Regulatory block")
	REGULATORY_REJECT = _("Regulatory reject")
	REGULATORY_REVIEW_EXCEEDING_SLA = _("Regulatory review exceeding SLA")
	RISK = _("Risk")
	SELLER_FAULT = _("Seller fault")
	SELLER_VOLUNTARY = _("Seller voluntary")
	THIRDPARTY_LOGISTICS_FAULT = _("Third-party logistics fault")
	UNAUTH_CLAIM = _("Unauth claim")
	UNAUTH_SPOOF = _("Unauth spoof")


class RefundState(Enum):
	pending = _("Pending")
	completed = _("Completed")
	cancelled = _("Cancelled")
	failed = _("Failed")


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
