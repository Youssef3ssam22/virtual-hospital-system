"""API routing for Billing."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PatientAccountViewSet, InvoiceViewSet, PaymentViewSet,
    InsuranceClaimViewSet, FinancialTimelineViewSet, BillingStatsViewSet,
    ClaimDenialViewSet, AccountByPatientView, AccountTimelineView
)

# Create router for auto-generated endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r'accounts', PatientAccountViewSet, basename='account')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'insurance-claims', InsuranceClaimViewSet, basename='insurance-claim')
router.register(r'claims', InsuranceClaimViewSet, basename='claim')
router.register(r'denials', ClaimDenialViewSet, basename='denial')
router.register(r'timeline', FinancialTimelineViewSet, basename='timeline')
router.register(r'stats', BillingStatsViewSet, basename='stats')

urlpatterns = [
    path("accounts/<str:patient_id>/", AccountByPatientView.as_view(), name="account-by-patient"),
    path("accounts/<str:patient_id>/timeline/", AccountTimelineView.as_view(), name="account-timeline"),
    path("", include(router.urls)),
]
