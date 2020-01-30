"""
dj-paypal exceptions
"""


class PaypalApiError(Exception):
	pass


class AgreementAlreadyExecuted(Exception):
	pass
