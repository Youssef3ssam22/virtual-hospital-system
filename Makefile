.PHONY: build up down dev dev-build dev-down migrate makemigrations \
        shell seed test test-v test-cov lint typecheck \
        celery celery-logs logs local-install local-run local-test local-celery

# ── Production ────────────────────────────────────────────────────────────────
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f web celery nginx

# ── Development ───────────────────────────────────────────────────────────────
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml build

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# ── Database ──────────────────────────────────────────────────────────────────
migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

shell:
	docker compose exec web python manage.py shell

seed:
	docker compose exec web python manage.py seed_data

# ── Testing ───────────────────────────────────────────────────────────────────
test:
	docker compose exec web pytest --tb=short -q

test-v:
	docker compose exec web pytest --tb=short -v

test-cov:
	docker compose exec web pytest --cov=apps --cov=shared \
		--cov-report=term-missing --cov-report=html -q

# ── Code quality ──────────────────────────────────────────────────────────────
lint:
	docker compose exec web python -m flake8 apps/ shared/ \
		--max-line-length=120 --exclude=migrations

typecheck:
	docker compose exec web python -m mypy apps/ shared/ \
		--ignore-missing-imports --no-strict-optional

# ── Celery ────────────────────────────────────────────────────────────────────
celery:
	docker compose up -d celery celery-beat

celery-logs:
	docker compose logs -f celery celery-beat

# ── Local (no Docker) ─────────────────────────────────────────────────────────
local-install:
	pip install -r requirements.txt

local-run:
	DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py runserver

local-test:
	DJANGO_SETTINGS_MODULE=config.settings.dev pytest --tb=short -q

local-celery:
	DJANGO_SETTINGS_MODULE=config.settings.dev \
	celery -A config worker -l info -Q default,notifications,cdss