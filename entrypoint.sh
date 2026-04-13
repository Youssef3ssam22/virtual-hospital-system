#!/bin/sh
set -e

echo "Waiting for database..."
while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
  echo "DB not ready, retrying..."
  sleep 2
done
echo "Database is ready."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating admin account..."
python manage.py create_admin || echo "Admin already exists, skipping."

echo "Seeding data..."
python manage.py seed_data || echo "Seed already done, skipping."

echo "Starting server..."
exec "$@"
