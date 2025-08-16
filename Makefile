RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
CYAN := \033[0;36m
GRAY := \033[0;37m
BOLD := \033[1m
NC := \033[0m

POETRY := poetry
PYTHON := poetry run python
PRE_COMMIT := pre-commit
SRC_DIR := config_wizard

# List all targets when running `make` or `make help`
.PHONY: help
help:
	@echo "${BOLD}Available targets:${NC}"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { printf "  ${CYAN}%-20s${NC} %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install dependencies using Poetry
	@echo "${GREEN}Installing dependencies...${NC}"
	$(POETRY) install

.PHONY: update
update: ## Update dependencies using Poetry
	@echo "${GREEN}Updating dependencies...${NC}"
	$(POETRY) update

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	@echo "${GREEN}Installing pre-commit hooks...${NC}"
	$(PRE_COMMIT) install

.PHONY: format
format: ## Format code using Ruff
	@echo "${GREEN}Formatting code...${NC}"
	@${PRE_COMMIT} run --all-files ruff-format end-of-file-fixer

.PHONY: lint
lint: ## Lint code using Ruff
	@echo "${GREEN}Linting code...${NC}"
	@${PRE_COMMIT} run --all-files ruff-check mypy

.PHONY: test
test: ## Run tests using pytest with coverage
	@echo "${GREEN}Running tests...${NC}"
	$(PYTHON) -m pytest tests/ --tb=short --disable-warnings -p no:warning --cov=${SRC_DIR} --cov-report=term-missing --cov-report=html --cov-branch

.PHONY: docs
docs: ## Build documentation using mkdocs
	@echo "${GREEN}Building documentation...${NC}"
	$(PYTHON) -m mkdocs build

.PHONY: serve-docs
serve-docs: ## Serve documentation locally using mkdocs
	@echo "${GREEN}Serving documentation locally...${NC}"
	$(PYTHON) -m mkdocs serve


.PHONY: clean
clean: ## Clean up Python cache files and directories
	@echo "${YELLOW}Cleaning up...${NC}"
	rm -rf .mypy_cache .pytest_cache .coverage .coverage.* .ruff-cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
