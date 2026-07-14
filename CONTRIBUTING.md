# Contributing

Thank you for improving OpenHR Agent. Open an issue before large changes, keep pull requests focused, add tests, and run the documented checks.

All contributions must be independently authored and suitable for public release. Use only fictional Acme Corporation policies and synthetic people. Never include employer/client code, internal prompts or workflows, real employee data, private URLs, screenshots, credentials, or secrets. By contributing, you agree that your work is provided under Apache-2.0.

Follow the Code of Conduct and report security or privacy concerns privately as described in `SECURITY.md`.

Before opening a pull request, run `ruff check .`, `mypy apps packages`, `pytest`,
`python -m packages.agent_core.evaluation`, and the frontend lint, typecheck, test, and build
commands from the README. New evaluation cases must use the strict schema, reference only known
fictional source IDs, explain their expectation, and remain deterministic.
