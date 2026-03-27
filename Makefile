
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
	python esofGroup5/scripts/main.py

# Run the full test suite
test:
	pytest esofGroup5/scripts/test_main.py -v

# Run all formatters then all linters
check: format lint

# Run all linters
lint: lint-python lint-html lint-js

# Python linter
lint-python:
	flake8 esofGroup5/scripts/main.py --config=.flake8

# HTML linter
lint-html:
	htmlhint "esofGroup5/**/*.html" --config .htmlhintrc

# JS linter (skips if no JS files exist yet)
lint-js:
	@if find esofGroup5/js -name "*.js" 2>/dev/null | grep -q .; then \
		eslint "esofGroup5/js/**/*.js"; \
	else \
		echo "No JS files found, skipping."; \
	fi

# Run all formatters
format: format-python format-html format-js

# Python formatter
format-python:
	black esofGroup5/scripts/main.py

# HTML formatter
format-html:
	prettier --write "esofGroup5/**/*.html"

# JS formatter (skips if no JS files exist yet)
format-js:
	@if find esofGroup5/js -name "*.js" 2>/dev/null | grep -q .; then \
		prettier --write "esofGroup5/js/**/*.js"; \
	else \
		echo "No JS files found, skipping."; \
	fi

.PHONY: install run test check lint lint-python lint-html lint-js format format-python format-html format-js