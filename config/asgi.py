"""config/asgi.py — ASGI entry point.

The project currently uses only synchronous Django views. ASGI is included
for future WebSocket support (real-time notifications to ward dashboards).
Until then this file is unused but kept ready.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from config.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
	"http": django_asgi_app,
	"websocket": URLRouter(websocket_urlpatterns),
})