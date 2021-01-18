from django.db.models import JSONField


__all__ = ("CurrencyAmountField", "JSONField")


class CurrencyAmountField(JSONField):
	pass
