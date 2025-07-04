# .PHONY specifies names that are to be treated as commands and not files
.PHONY: install-dependencies \
		format-code \
		lint-code \
		check-code-security \
		check-dependencies-vulnerabilities \
		unit-testing

install-dependencies:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

format-code:
	@echo "Formatting code..."
	black src/ tests/

lint-code:
	@echo "Linting code..."
	ruff check src/ tests/

check-code-security:
	@echo "Checking code security..."
	bandit -r src/

check-dependencies-vulnerabilities:
	@echo "Checking dependencies vulnerabilities..."
	pip-audit -r requirements.txt

unit-testing:
	@echo "Running unit tests..."
	pytest tests/ -vv

launch-api:
	@echo "Launching api..."
	uvicorn --app-dir src api.main:run --reload --forwarded-allow-ips "127.0.0.1"

launch-api-ssl:
	@echo "Launching api with SSL..."
	uvicorn --app-dir src api.main:run --reload --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem

setup:	install-dependencies \
		format-code \
		lint-code \
		check-code-security \
		check-dependencies-vulnerabilities \
		unit-testing