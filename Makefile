# DVD Rental API — Developer Makefile
# Usage: make <target>

.PHONY: help install install-dev lint format type-check test clean \
        build docker-build docker-up docker-down run

# ── Defaults ─────────────────────────────────────────────────────────────────
PYTHON      ?= python3
PIP         ?= pip
IMAGE_NAME  ?= dvdrental-api
IMAGE_TAG   ?= latest

help:                ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Installation ──────────────────────────────────────────────────────────────
install:             ## Install runtime dependencies only
	$(PIP) install -r requirements.txt

install-dev:         ## Install all deps including dev/test tools (editable)
	$(PIP) install -e ".[dev]"

# ── Code quality ──────────────────────────────────────────────────────────────
lint:                ## Run ruff linter
	ruff check app tests

format:              ## Auto-format code with ruff
	ruff format app tests
	ruff check --fix app tests

type-check:          ## Run mypy type checker
	mypy app

# ── Testing ───────────────────────────────────────────────────────────────────
test:                ## Run test suite
	pytest -v

test-cov:            ## Run tests with coverage report
	pytest --cov=app --cov-report=term-missing -v

# ── Local development ─────────────────────────────────────────────────────────
run:                 ## Start API server with hot-reload (requires .env)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ── Build ─────────────────────────────────────────────────────────────────────
build:               ## Build Python wheel (output in dist/)
	$(PIP) install hatchling
	$(PYTHON) -m hatchling build --target wheel

docker-build:        ## Build Docker image
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# ── Docker Compose ────────────────────────────────────────────────────────────
docker-up:           ## Start all services (docker compose up -d)
	docker compose up -d

docker-up-build:     ## Rebuild images and start all services
	docker compose up -d --build

docker-down:         ## Stop all services
	docker compose down

docker-logs:         ## Follow logs for all services
	docker compose logs -f

# ── Cleanup ───────────────────────────────────────────────────────────────────
clean:               ## Remove build artifacts and caches
	rm -rf dist/ build/ *.egg-info .mypy_cache .ruff_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
