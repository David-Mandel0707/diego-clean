# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Collect static files (required before deploying or when static files change)
python manage.py collectstatic --noinput

# Run tests
python manage.py test

# Run tests for a single app
python manage.py test accounts
python manage.py test core
```

## Environment variables

The project uses `python-decouple` — create a `.env` file at the root with:

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3   # or a postgres URL
```

Email credentials (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) are currently hardcoded in `Diego_Clean/settings.py` and should be moved to `.env`, but is not a priority.

## Architecture

**Django 6 project** structured as two apps:

- **`accounts`** — authentication. Custom user model (`accounts.CustomUser` extends `AbstractUser` with a `phone` field). Login view at `/login/`, password reset flow wired to Django's built-in auth views.
- **`core`** — business logic. Two models: `Cliente` (customer) and `Servico` (service job), where `Servico` has a FK to `Cliente` and an optional FK to the logged-in user (employee). Payment status choices: `pendente`, `pago`, `cancelado`.

**URL layout:**
- `/login/` → `accounts.views.login`
- `/home/` → `core.views.home` (lists all `Servico` objects)
- `/admin/` → Django admin
- `/password_reset/` and related → Django built-in views

**Templates** live per-app under `<app>/templates/` (Django's `APP_DIRS=True`). Shared base template is at `core/templates/base.html`. Template names use PascalCase (e.g. `Home.html`, `Login.html`).

**Static files** are in `/static/` at the project root (logos as SVG). Served in production via Whitenoise (`CompressedManifestStaticFilesStorage`). `STATICFILES_DIRS` points to `BASE_DIR / 'static'`; `STATIC_ROOT` is `staticfiles/`.

**Database** uses `DATABASE_URL` parsed by `dj-database-url` (PostgreSQL via `psycopg2-binary`).
