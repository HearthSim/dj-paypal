from django.contrib.postgres.fields import JSONField


__all__ = ("CurrencyAmountField", "JSONField")


class CurrencyAmountField(JSONField):
	pass
