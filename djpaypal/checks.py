from django.core import checks

from . import settings as djpaypal_settings


VALID_MODES = ("live", "sandbox")


@checks.register("djpaypal")
def check_paypal_api_key(app_configs=None, **kwargs):
	"""Check that the Paypal API keys are configured correctly"""
	messages = []

	mode = getattr(djpaypal_settings, "PAYPAL_MODE", None)
	if mode not in VALID_MODES:
		msg = "Invalid PAYPAL_MODE specified: {}.".format(repr(mode))
		hint = "PAYPAL_MODE must be one of {}".format(", ".join(repr(k) for k in VALID_MODES))
		messages.append(checks.Critical(msg, hint=hint, id="djpaypal.C001"))

	for setting in "PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET":
		if not getattr(djpaypal_settings, setting, None):
			msg = "Invalid value specified for {}".format(setting)
			hint = "Add PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET to your settings."
			messages.append(checks.Critical(msg, hint=hint, id="djpaypal.C002"))

	return messages
