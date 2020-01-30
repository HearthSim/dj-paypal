from django.conf import settings


PAYPAL_MODE = getattr(settings, "PAYPAL_MODE", None)
PAYPAL_CLIENT_ID = getattr(settings, "PAYPAL_CLIENT_ID", None)
PAYPAL_CLIENT_SECRET = getattr(settings, "PAYPAL_CLIENT_SECRET", None)

PAYPAL_LIVE_MODE = PAYPAL_MODE == "live"

PAYPAL_WEBHOOK_ID = getattr(settings, "PAYPAL_WEBHOOK_ID", "")

PAYPAL_SETTINGS = {
	"mode": PAYPAL_MODE,
	"client_id": PAYPAL_CLIENT_ID,
	"client_secret": PAYPAL_CLIENT_SECRET,
}

if PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET:
	from paypalrestsdk import configure
	configure(PAYPAL_SETTINGS)
