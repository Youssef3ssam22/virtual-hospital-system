"""config/wsgi.py — WSGI entry point for gunicorn."""
import os
from django.core.wsgi import get_wsgi_application

# Default to dev. Production sets DJANGO_SETTINGS_MODULE in the container
# environment via docker-compose.yml — this default only applies when running
# locally without setting the variable (e.g. python manage.py runserver).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = get_wsgi_application()