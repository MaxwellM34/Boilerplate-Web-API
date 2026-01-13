# Boilerplate Web + API

This repo is a starter layout with a Next.js webapp and a FastAPI backend wired to Postgres via Tortoise ORM. Use it as a clean base and replace the placeholder endpoints and styles with your own app logic.

## Structure

- `webapp/` - Next.js (App Router) frontend
- `api/` - FastAPI backend with Tortoise ORM
- `api/docker-compose.yml` - local Postgres container
- `api/.env` and `api/.env.cloud` - local/cloud config

## Prerequisites

- Node.js LTS (includes `npm`): https://nodejs.org
- Python 3.11+
- Docker Desktop (optional, for local Postgres)
- `uv` (optional): `pip install uv`

## Quick start (local)

Webapp:
- `cd webapp`
- `npm install`
- `npm run dev`

API:
- `cd api`
- `uv venv` (or `python -m venv .venv`)
- `.venv\Scripts\Activate.ps1`
- `uv pip install -r requirements.txt` (or `pip install -r requirements.txt`)
- `.\run_dev.ps1` (reload ignores `.venv`) or `uvicorn main:app --reload`

Database (local Postgres):
- `cd api`
- `docker compose up -d`
- Update `api/.env` if you want different DB creds.

Tables are created automatically on API startup because Tortoise is registered with `generate_schemas=True`. Run the API once to create the `users` table.

## Environment config (local vs cloud)

Set `ENV=local` or `ENV=cloud` in your environment or in the `.env` files.

- Local: uses `api/.env` and `config.LocalConfig` (PG_* values)
- Cloud: uses `api/.env.cloud` and `config.CloudConfig` (DATABASE_URL or Cloud SQL vars)

## Building your app on top

- Add API routes in `api/routers/` and register them in `api/main.py`.
- Add database models in `api/models/`. Update auth logic in `api/auth/` as needed.
- Add frontend pages in `webapp/src/app/` and shared styles in `webapp/src/app/globals.css`.
- Set any required secrets in `api/.env` (local) or `api/.env.cloud` (cloud).

