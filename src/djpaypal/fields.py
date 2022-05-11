from django.db.models.fields.json import JSONField


__all__ = ("CurrencyAmountField", "JSONField")


class CurrencyAmountField(JSONField):
	pass
