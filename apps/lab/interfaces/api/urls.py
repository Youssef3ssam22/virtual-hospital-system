"""Lab API routes."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LabOrderDetailView, LabOrderListCreateView
from .views_extended import (
    SpecimenViewSet, LabResultViewSet, CriticalValueViewSet,
    LabReportViewSet, AnalyzerQueueViewSet, WorklistView,
    AccessionsViewSet, PanelViewSet
)

# Create router for auto-generated endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r'specimens', SpecimenViewSet, basename='specimen')
router.register(r'results', LabResultViewSet, basename='result')
router.register(r'critical-values', CriticalValueViewSet, basename='critical-value')
router.register(r'reports', LabReportViewSet, basename='report')
router.register(r'analyzer-queue', AnalyzerQueueViewSet, basename='analyzer-queue')
router.register(r'accessions', AccessionsViewSet, basename='accession')
router.register(r'panels', PanelViewSet, basename='panel')

urlpatterns = [
    path("worklist/", WorklistView.as_view(), name="lab-worklist"),
    path("orders/", LabOrderListCreateView.as_view(), name="lab-orders-list-create"),
    path("orders/<uuid:order_id>/", LabOrderDetailView.as_view(), name="lab-orders-detail"),
    path("analyzers/queue/", AnalyzerQueueViewSet.as_view({'get': 'list'}), name="analyzer-queue-alias"),
    path("analyzers/queue/<uuid:pk>/status/", AnalyzerQueueViewSet.as_view({'put': 'status'}), name="analyzer-queue-status"),
    path("critical/", CriticalValueViewSet.as_view({'get': 'list'}), name="critical-values-alias"),
    path("critical/<uuid:pk>/notify/", CriticalValueViewSet.as_view({'post': 'notify'}), name="critical-values-notify"),
    path("critical/<uuid:pk>/acknowledge/", CriticalValueViewSet.as_view({'post': 'acknowledge'}), name="critical-values-acknowledge"),
    path("", include(router.urls)),
]
