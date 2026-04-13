"""config/urls.py"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView,
)

from shared.views import HealthCheckView, MetaChoicesView, DashboardView

urlpatterns = [
    path("admin/",  admin.site.urls),
    path("health/", HealthCheckView.as_view(), name="health-check"),

    path("api/v1/meta/choices/", MetaChoicesView.as_view(), name="meta-choices"),
    path("api/v1/dashboard/",    DashboardView.as_view(),   name="dashboard"),

    path("api/schema/", SpectacularAPIView.as_view(),                      name="schema"),
    path("api/docs/",   SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/",  SpectacularRedocView.as_view(url_name="schema"),   name="redoc"),

    # Implemented modules
    path("api/v1/auth/",      include("apps.auth.interfaces.api.urls")),
    path("api/v1/admin/",     include("apps.admin.interfaces.api.urls")),
    path("api/v1/patients/",  include("apps.patients.interfaces.api.urls")),
    path("api/v1/lab/",       include("apps.lab.interfaces.api.urls")),
    path("api/v1/billing/",   include("apps.billing.interfaces.api.urls")),
    
    # Skeleton modules (URLs not yet implemented)
    # path("api/v1/radiology/",   include("apps.radiology.interfaces.api.urls")),
    # path("api/v1/pharmacy/",    include("apps.pharmacy.interfaces.api.urls")),
    # path("api/v1/cdss/",        include("apps.cdss.interfaces.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
