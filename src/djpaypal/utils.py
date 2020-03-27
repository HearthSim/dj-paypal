from decimal import Decimal

from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html


def admin_urlify(column, help_text=None):  # pragma: no cover
	"""
	Can be used to add a link to a model referenced in another admin.

	Example:
		fields = [admin_urlify("user")]
	"""
	def inner(*args):
		if len(args) > 1:
			obj = args[1]
		else:
			obj = args[0]
		_obj = getattr(obj, column)
		if _obj is None:
			return "-"
		try:
			url = _obj.get_absolute_url()
		except (AttributeError, NoReverseMatch):
			url = ""
		admin_pattern = "admin:%s_%s_change" % (_obj._meta.app_label, _obj._meta.model_name)
		admin_url = reverse(admin_pattern, args=[_obj.pk])

		ret = format_html('<a href="{url}">{obj}</a>', url=admin_url, obj=_obj)
		if url:
			ret += format_html(' (<a href="{url}">View</a>)', url=url)
		return ret

	inner.short_description = column.replace("_", " ")

	return inner


def fix_django_headers(meta):
	"""
	Fix this nonsensical API:
	https://docs.djangoproject.com/en/1.11/ref/request-response/
	https://code.djangoproject.com/ticket/20147
	"""
	ret = {}
	for k, v in meta.items():
		if k.startswith("HTTP_"):
			k = k[len("HTTP_"):]
		elif k not in ("CONTENT_LENGTH", "CONTENT_TYPE"):
			# Skip CGI garbage
			continue

		ret[k.lower().replace("_", "-")] = v

	return ret


CURRENCY_SIGILS = {
	"CAD": "$",
	"EUR": "€",
	"GBP": "£",
	"USD": "$",
}


def get_friendly_currency_amount(amount, currency):
	currency = currency.upper()
	sigil = CURRENCY_SIGILS.get(currency, "")
	# Always show two decimal places on the amount
	# Note that amount is usually a string, so convert to Decimal first.
	amount = "{:.2f}".format(Decimal(amount))
	return "{sigil}{amount} {currency}".format(sigil=sigil, amount=amount, currency=currency)


def get_version():
	"""
	Returns the current dj-paypal version
	"""
	from . import __version__
	return __version__
