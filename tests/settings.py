SECRET_KEY = "hunter2"
DEBUG = True
SITE_ID = 1
USE_TZ = True

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.postgresql",
		"NAME": "test_djpaypal",
		"USER": "postgres",
		"PASSWORD": "",
		"HOST": "localhost",
		"PORT": "",
	},
}

INSTALLED_APPS = [
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"djpaypal",
]


PAYPAL_MODE = "sandbox"
# PAYPAL_CLIENT_ID = ""
# PAYPAL_CLIENT_SECRET = ""
