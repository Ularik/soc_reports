# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Django 5.2 app for a SOC team: analysts file incident reports (threats detected by WAF/IPS/EDR/SIEM), which are rendered to PDF, listed/exported monthly, and aggregated into analytics charts and a statistical Excel form. UI text and model labels are in Russian.

## Commands

```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test reports                                   # all tests
python manage.py test reports.tests.ReportPdfGenerationTests    # one class (append .method for one test)
```

No linter is configured.

## Setup gotchas

- Settings read environment variables from `.env` in the repo root (loaded via python-dotenv in `project/settings.py`). `.env` is untracked; copy `.env.example` to `.env` and fill it in. `SECRET_KEY`, `DB_NAME`, `DB_USER` and `DB_PASSWORD` are required; the database is PostgreSQL.
- `CACHES` uses Redis at `127.0.0.1:6379`; a Redis server is needed wherever the cache is used.
- `AUTH_USER_MODEL = 'user.CustomUser'` (custom model with `username` and `username_ru`, no email).
- `reports/services/stat_report.py` opens `reports/stat_rep_template/pattern.xlsx` via `BASE_DIR`.

## Architecture

- `reports` app is the core. `Report` (an incident) has FKs to `Organization`, `Pattern` and `User`. `Pattern` is a template of attack data (description, methods, risk, response actions). `report_waf_form.html` receives all patterns as JSON (`report_create_view` in `views.py`) and autofills the form client-side when a pattern is picked.
- `reports/views.py` is thin (HTTP, forms, auth); logic lives in `reports/services/`:
  - `pdf.py` — `build_report_pdf` (reportlab; looks for a Cyrillic TTF in OS-specific paths, falls back to Times-Roman).
  - `cert_gov.py` — `send_report_pdf` posts the PDF to cert.gov.kg; configured by `CERT_GOV_API_URL/USERNAME/PASSWORD` in `.env` (empty URL disables sending). Errors are logged, never raised.
  - `analytics.py` — `parse_period` (no dates = today; date-only `end` = end of day; bad input raises `ValueError` -> views return 400), `count_by`, `split_top`, `stats_by_user`.
  - `monthly.py` — `build_monthly_rows` (per source IP, picks the highest-risk record by `RISK_LEVELS` order).
  - `stat_report.py` — `create_stat_report` fills `stat_rep_template/pattern.xlsx` (FIN/GTS/GNS/ADM map to fixed columns; Critical+High = "high", Medium+Low = "low").
- Report creation redirects to `report_new?download=<pk>`, which triggers the PDF download. The attack-types chart returns "Прочие" as a percentage while other values are counts; the front end (`static/js/analytics/`) depends on that.
- `user` app: `CustomUser`, login forms and an API. `project/urls.py` mounts a django-ninja API at `/api/`, with `/api/events/user-create` creating users.
- `db_logger` app: a custom logging handler that writes log records to the DB (`StatusLog`); wired up via `LOGGING` in settings.
- Shared templates are in `templates/` (`base.html`); app templates are in `reports/templates/reports/`.
