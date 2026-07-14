# Deterministic routing

`ControllerRouter` classifies normalized request text using an explicit keyword map. It supports `general_policy`, `leave_and_attendance`, `benefits`, `onboarding`, `learning_and_development`, `hr_service`, and `unsupported`.

Every match is retained in `detected_domains`; the highest-scoring domain is primary, and more than one detected domain marks a multi-intent request. Employee-specific phrases such as “my leave balance” require a synthetic `employee_id`. An unmatched question routes to `unsupported` and is never answered from guesswork.

The routing summary is an audit explanation of rule matches, not hidden model reasoning. This deterministic approach is intentionally limited but stable and testable.
