
# -------------------------------------------------------
# Makefile for ESC Dashboard
# Mac: run targets normally with `make <target>`
# Windows: run via Git Bash (`make <target>`) or WSL
# -------------------------------------------------------

# Install all Python and Node dependencies
install:
	pip install -r requirements.txt
	npm install -g htmlhint eslint prettier

# Run the Flask development server
run:
	python backend/main.py

# Run the full test suite
test:
	pytest backend/test_main.py -v

# Run all formatters then all linters
check: format lint

# Run all linters
lint: lint-python lint-html lint-js

# Python linter
lint-python:
	flake8 backend/main.py --config=.flake8

# HTML linter
lint-html:
	htmlhint "frontend/**/*.html" --config .htmlhintrc

# JS linter (skips if no JS files exist yet)
lint-js:
	@if find frontend/js -name "*.js" 2>/dev/null | grep -q .; then \
		eslint "frontend/js/**/*.js"; \
	else \
		echo "No JS files found, skipping."; \
	fi

# Run all formatters
format: format-python format-html format-js

# Python formatter
format-python:
	black backend/main.py

# HTML formatter
format-html:
	prettier --write "frontend/**/*.html"

# JS formatter (skips if no JS files exist yet)
format-js:
	@if find frontend/js -name "*.js" 2>/dev/null | grep -q .; then \
		prettier --write "frontend/js/**/*.js"; \
	else \
		echo "No JS files found, skipping."; \
	fi

.PHONY: install run test check lint lint-python lint-html lint-js format format-python format-html format-js