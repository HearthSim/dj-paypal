# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.11.0] - 2018-12-18
## Added
- Add "admin_url" property in PaypalObject model
- Add link to resource in WebhookEvent admin
- Add event type as filter to WebhookEventAdmin

## Fixed
- Fix dashboard url in Sale model

## [0.10.1] - 2018-11-18
## Fixed
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

[Unreleased]: https://github.com/HearthSim/dj-paypal/compare/0.11.0...HEAD
[0.11.0]: https://github.com/HearthSim/dj-paypal/compare/0.10.1...0.11.0
[0.10.1]: https://github.com/HearthSim/dj-paypal/compare/0.10.0...0.10.1
[0.10.0]: https://github.com/HearthSim/dj-paypal/compare/0.9.1...0.10.0
[0.9.1]: https://github.com/HearthSim/dj-paypal/compare/0.9.0...0.9.1
