# dj-paypal

[![Build Status](https://api.travis-ci.org/HearthSim/dj-paypal.svg?branch=master)](https://travis-ci.org/HearthSim/dj-paypal)


A Paypal integration for Django, inspired by [dj-stripe](https://github.com/dj-stripe/dj-stripe).

Currently only supports subscriptions.


## Requirements

- Python 3.6+
- Django 2.0+
- Postgres 9.6+ (Non-postgres engines not supported)


## Installation

1. Install dj-paypal with `pip install dj-paypal`
2. Add `djpaypal` to django `INSTALLED_APPS` setting
3. Get a client ID and client secret from paypal and add them to the settings
   `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET`
4. Set `PAYPAL_MODE = "sandbox"` (or `"live"`) in the settings
5. Install your Billing Plans (see below)


### Setting up billing plans

#### Download already-created billing plans from Paypal

Run `manage.py djpaypal_download_plans` to sync all plans already created upstream
into the local database.

This will create `djpaypal.models.BillingPlan` objects, which can be listed from
the Django admin.


#### Creating new Paypal billing plans

The `manage.py djpaypal_upload_plans` management command creates billing plans using
the Paypal API. An extra `PAYPAL_PLANS` setting must be set, which will contain a dict
of Paypal billing plans to create.

See `example_settings.py` for an example of plans to create.


## Webhooks

The `djpaypal.views.ProcessWebhookView` view should be hooked up to an URL endpoint
which you then set up in Paypal as a webhook endpoint (https://developer.paypal.com).

In order to verify webhooks being transmitted to your app, dj-paypal needs to know the
ID of the webhook that is expected at that URL. Set it in the setting `PAYPAL_WEBHOOK_ID`.


## Sandbox vs. Live

All models have a `livemode` boolean attribute. That attribute is set to `True` if created
in Live (production) mode, `False` otherwise (sandbox mode).
Sandbox and Live data can co-exist without issues. Once you are done testing in Sandbox
mode, use the `manage.py djpaypal_delete_all_test_data` management command to (locally)
clear all the test data. This command has no impact on the upstream data.


## Data considerations

Most of the models defined in dj-paypal are copies of the upstream Paypal model data.
Deleting or editing objects (be it from the admin or in the database) does not actually
change any of the upstream Paypal data.


## License and Sponsorship

This project was designed and developed by [HearthSim](https://hearthsim.net). It is
licensed under the MIT license. The full license text is available in the LICENSE file.
