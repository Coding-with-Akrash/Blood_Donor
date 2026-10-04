# Database Migrations

This project uses Flask-Migrate for database migrations.

## Setup

Flask-Migrate is already configured in `app/__init__.py`.

## Commands

Initialize migrations (run once):
```bash
flask db init
```

Generate a migration:
```bash
flask db migrate -m "description"
```

Apply migrations:
```bash
flask db upgrade
```

Downgrade:
```bash
flask db downgrade
```

## Production Deployment

On production (Render, Railway, etc.):
1. Set `DATABASE_URL` environment variable
2. Run `flask db upgrade` as a one-time setup command
3. The app will automatically use the production database
