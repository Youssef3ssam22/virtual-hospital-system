"""WebSocket routing configuration."""
from django.urls import path
from apps.lab.interfaces.ws.critical import CriticalValueConsumer

websocket_urlpatterns = [
    path("ws/lab/critical/", CriticalValueConsumer.as_asgi()),
]
