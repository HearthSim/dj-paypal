# Get these from https://developer.paypal.com/
PAYPAL_CLIENT_ID = "XXXXXXXXXXXXXXXXXXXXXXXXX"
PAYPAL_CLIENT_SECRET = "XXXXXXXXXXXXXXXXXXXXX"

# "sandbox" or "live"
PAYPAL_MODE = "sandbox"

# Only used by manage.py djpaypal_upload_plans
PAYPAL_PLANS = {
	"monthly": {
		"name": "1 Month Subscription",
		"description": "Support us every month!",
		"type": "INFINITE",  # enums.BillingPlanType.INFINITE,
		"merchant_preferences": {
			"auto_bill_amount": "YES",  # enums.PaypalBool.YES,
			"initial_fail_amount_action": "CANCEL",  # enums.PaypalAction.CANCEL,
			"max_fail_attempts": "1",
			# The following URLs must point to a return and cancel view.
			# They must be absolute.
			"return_url": "http://localhost:8000/account/billing/paypal/return/",
			"cancel_url": "http://localhost:8000/account/billing/paypal/cancel/",
			"setup_fee": {"value": "0", "currency": "USD"},
		},
		"payment_definitions": [
			{
				"amount": {"value": "5.00", "currency": "USD"},
				"charge_models": [],
				"cycles": "0",
				"frequency": "MONTH",  # enums.PaymentDefinitionFrequency.MONTH,
				"frequency_interval": "1",
				"name": "Monthly Billing",
				"type": "REGULAR",  # enums.PaymentDefinitionType.REGULAR,
			},
		],
	},
	"semiannual": {
		"name": "6 Months Subscription",
		"description": "Support us every 6 months!",
		"type": "INFINITE",  # enums.BillingPlanType.INFINITE,
		"merchant_preferences": {
			"auto_bill_amount": "YES",  # enums.PaypalBool.YES,
			"initial_fail_amount_action": "CANCEL",  # enums.PaypalAction.CANCEL,
			"max_fail_attempts": "1",
			"return_url": "http://localhost:8000/account/billing/paypal/return/",
			"cancel_url": "http://localhost:8000/account/billing/paypal/cancel/",
			"setup_fee": {"value": "0", "currency": "USD"},
		},
		"payment_definitions": [
			{
				"amount": {"value": "25.00", "currency": "USD"},
				"charge_models": [],
				"cycles": "0",
				"frequency": "MONTH",  # enums.PaymentDefinitionFrequency.MONTH,
				"frequency_interval": "6",
				"name": "Semiannual Billing",
				"type": "REGULAR",  # enums.PaymentDefinitionType.REGULAR,
			},
		],
	}
}
