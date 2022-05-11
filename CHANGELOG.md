# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.16.0] - 2022-05-11
### Added
- Added list-view link to user in BillingAgreement admin
- Search more fields in BillingAgreement admin (user id, username, email)
### Breaking
- Django versions earlier than 3.1 are no longer supported

## [0.15.3] - 2020-03-25
### Fixed
- Fix a potential crash when calling "cancel" or "suspend" in BillingAgreement

## [0.15.2] - 2020-03-25
### Fixed
- Fix stale BillingAgreement state after calling "cancel" or "suspend"

## [0.15.1] - 2020-03-24
### Fixed
- Fix broken search in WebhookEventAdmin
- Fix overriding "end_of_period" for canceled billing agreements

## [0.15.0] - 2020-01-30
### Added
- Add "plan_id" property to PreparedBillingAgreement
- Add "plan_model" property to BillingAgreement

### Changed
- Test against Django 2.2 and 3.0

## [0.14.0] - 2019-12-30
### Added
- Add "immediately" parameter to "cancel" method in BillingAgreement
- Add "cancel_immediately" and "expire" actions to BillingAgreementAdmin

### Fixed
- Fix "state" field having values of both "Canceled" and "Cancelled" in BillingAgreement model

## [0.13.0] - 2019-11-11
### Added
- Add "webhook_error" signal for custom error logging

## [0.12.1] - 2019-11-10
### Fixed
- Fix required "shipping_adress" in BillingAgreement model
- Fix missing payment hold fields in Sale model
- Fix missing fields in Dispute model

## [0.12.0] - 2019-02-13
### Added
- Start searching in WebhookEvent admin by resource id
- Add "cancel" action to BillingAgreementAdmin

## [0.11.2] - 2018-12-21
### Fixed
- Fix missing dashoard url in Refund model
- Fix outdated properties in Sale model after a refund

## [0.11.1] - 2018-12-18
### Fixed
- Fix disputes breaking WebhookEvent admin

## [0.11.0] - 2018-12-18
### Added
- Add "admin_url" property in PaypalObject model
- Add link to resource in WebhookEvent admin
- Add event type as filter to WebhookEventAdmin

### Fixed
- Fix dashboard url in Sale model

## [0.10.1] - 2018-11-18
### Fixed
- Fix missing field "refund_to_payer" in Refund model

## [0.10.0] - 2018-11-18
### Added
- Add BillingAgreement.suspend and BillingAgreement.cancel

### Changed
- Sort various admin views by creation time

### Fixed
- Fix missing field "invoice_number" in Sale model

## [0.9.1] - 2018-10-18
### Fixed
- Fix missing Refund fields

[Unreleased]: https://github.com/HearthSim/dj-paypal/compare/0.16.0...HEAD
[0.16.0]: https://github.com/HearthSim/dj-paypal/compare/0.15.3...0.16.0
[0.15.3]: https://github.com/HearthSim/dj-paypal/compare/0.15.2...0.15.3
[0.15.2]: https://github.com/HearthSim/dj-paypal/compare/0.15.1...0.15.2
[0.15.1]: https://github.com/HearthSim/dj-paypal/compare/0.15.0...0.15.1
[0.15.0]: https://github.com/HearthSim/dj-paypal/compare/0.14.0...0.15.0
[0.14.0]: https://github.com/HearthSim/dj-paypal/compare/0.13.0...0.14.0
[0.13.0]: https://github.com/HearthSim/dj-paypal/compare/0.12.1...0.13.0
[0.12.1]: https://github.com/HearthSim/dj-paypal/compare/0.12.0...0.12.1
[0.12.0]: https://github.com/HearthSim/dj-paypal/compare/0.11.2...0.12.0
[0.11.2]: https://github.com/HearthSim/dj-paypal/compare/0.11.1...0.11.2
[0.11.1]: https://github.com/HearthSim/dj-paypal/compare/0.11.0...0.11.1
[0.11.0]: https://github.com/HearthSim/dj-paypal/compare/0.10.1...0.11.0
[0.10.1]: https://github.com/HearthSim/dj-paypal/compare/0.10.0...0.10.1
[0.10.0]: https://github.com/HearthSim/dj-paypal/compare/0.9.1...0.10.0
[0.9.1]: https://github.com/HearthSim/dj-paypal/compare/0.9.0...0.9.1
