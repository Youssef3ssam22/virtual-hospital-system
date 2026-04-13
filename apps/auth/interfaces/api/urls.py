"""Auth API URLs."""
from django.urls import path

from apps.auth.interfaces.api.views import RegisterView, LoginView, LogoutView, RefreshTokenView

app_name = "auth"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
]
