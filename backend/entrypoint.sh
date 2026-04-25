#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -U "${POSTGRES_USER:-appuser}" -d "${POSTGRES_DB:-appdb}"; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Running DB migrations..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Tables created.')
"

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app
