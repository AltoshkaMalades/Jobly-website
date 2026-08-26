# Jobly backend

Django backend for the Jobly student and employer platform.

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create the local environment file:

```powershell
Copy-Item .env.example .env
```

Set a random `SECRET_KEY`, keep `DEBUG=True` for local development, and provide PostgreSQL `DATABASE_URL` when using PostgreSQL. Google OAuth is optional; set `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` to enable it.

4. Apply migrations and start Django:

```powershell
python manage.py migrate
python manage.py runserver
```

The local server is available at http://127.0.0.1:8000/.

## Docker Compose

```powershell
docker compose --env-file .env up --build
```

Compose starts Django, PostgreSQL, Redis, Prometheus, and Grafana. PostgreSQL data is stored in the `postgres_data` volume.

## Production checks

Production requires an explicit `SECRET_KEY`, `DEBUG=False`, a non-wildcard `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS` with HTTPS origins:

```powershell
$env:SECRET_KEY = 'generate-a-random-secret-of-at-least-50-characters'
$env:DEBUG = 'False'
python manage.py check --deploy
```

Run tests with:

```powershell
python -m pytest -v
```
