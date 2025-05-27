lint-dir ?= .


.PHONY: help
help: ## Generates a help README
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: lint
lint: ## lint and format code (Ruff)
	ruff check $(lint-dir) --fix ; ruff format $(lint-dir)


.PHONY: test
test: ## run tests (Pytest)
	pytest $(lint-dir) -v


.PHONY: run
run: ## run script
	python main.py