"""
PRIORITY 1: RBAC ENFORCEMENT FIXES
All viewsets need explicit permission_classes replacing IsAuthenticated-only
"""

# ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
# LAB ENDPOINTS
# ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔

# FILE: apps/lab/interfaces/api/views.py
# CHANGE: Add IsLabTechnician | IsDoctor to all endpoints

OLD:
    class LabOrderListCreateView(APIView):
        permission_classes = [IsAuthenticated]

NEW:
    from shared.permissions import IsLabTechnician, IsDoctor
    from rest_framework.permissions import IsAuthenticated
    
    class IsLabOrDoctor(BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            return getattr(request.user, 'role') in ['LAB_TECHNICIAN', 'DOCTOR']
    
    class LabOrderListCreateView(APIView):
        permission_classes = [IsLabTechnician | IsDoctor]  # Either role allowed

---

# FILE: apps/lab/interfaces/api/views_extended.py
# CHANGE: Add IsLabTechnician to all Lab ViewSets

OLD:
    class SpecimenViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated]
        
    class LabResultViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated]
        
    class LabReportViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated]

NEW:
    from shared.permissions import IsLabTechnician, IsDoctor
    
    class SpecimenViewSet(viewsets.ModelViewSet):
        permission_classes = [IsLabTechnician]  # Only lab techs create/update specimens
        
    class LabResultViewSet(viewsets.ModelViewSet):
        permission_classes = [IsLabTechnician]  # Lab techs enter results
        
    class LabReportViewSet(viewsets.ModelViewSet):
        permission_classes = [IsDoctor]  # Doctors only release reports

# ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
# BILLING ENDPOINTS
# ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔

# FILE: apps/billing/interfaces/api/views.py
# CHANGE: Add IsAccountant | IsAdmin to all ViewSets

OLD:
    class InvoiceViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated]
        
    class PaymentViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated]

NEW:
    from shared.permissions import IsAccountant, IsAdmin
    
    # Create combined permission for billing staff
    class IsBillingStaff(BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            return getattr(request.user, 'role') in ['ACCOUNTANT', 'ADMIN']
    
    class InvoiceViewSet(viewsets.ModelViewSet):
        permission_classes = [IsBillingStaff]
        
        def get_queryset(self):
            # Accountants only see their assigned accounts
            if getattr(self.request.user, 'role') == 'ACCOUNTANT':
                return Invoice.objects.filter(account_id__in=self.request.user.assigned_accounts)
            # Admins see all
            return Invoice.objects.all()
    
    class PaymentViewSet(viewsets.ModelViewSet):
        permission_classes = [IsBillingStaff]
        
    class BillingStatsViewSet(viewsets.ReadOnlyModelViewSet):
        permission_classes = [IsAdmin]  # Admin only for statistics

# ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
# ADMIN ENDPOINTS
# ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔

# FILE: apps/admin/interfaces/api/views.py
# CHANGE: Replace manual IsAdmin checks with decorator-based permission_classes

OLD:
    class AdminListCreateView(APIView):
        permission_classes = [IsAuthenticated]
        
        def get(self, request):
            if not IsAdmin().has_permission(request, self):
                return Response({"detail": "You do not have permission..."}, status=403)

NEW:
    from shared.permissions import IsAdmin
    
    class AdminListCreateView(APIView):
        permission_classes = [IsAdmin]  # DRF handles permission check automatically
        
        def get(self, request):
            # IsAdmin permission already enforced by DRF
            # No need for manual check

# FILE: apps/admin/interfaces/api/views_extended.py
# CHANGE: Add IsAdmin to admin ViewSets

OLD:
    class DepartmentViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated]
        
    class SystemSettingsViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated]

NEW:
    from shared.permissions import IsAdmin
    
    class DepartmentViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAdmin]  # Only admins manage departments
        
    class SystemSettingsViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAdmin]  # Only admins manage settings

---

TESTING RBAC:

# Before fix (should work but shouldn't):
GET /api/v1/lab/orders/
Header: Authorization: Bearer <accountant_token>
Status: 200 OK (WRONG ❌)

# After fix (should deny):
GET /api/v1/lab/orders/
Header: Authorization: Bearer <accountant_token>
Status: 403 Forbidden (CORRECT ✅)

# After fix (should allow):
GET /api/v1/lab/orders/
Header: Authorization: Bearer <doctor_token>
Status: 200 OK (CORRECT ✅)

"""
