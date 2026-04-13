"""Django ORM models for auth."""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from uuid import uuid4
from django.utils import timezone
from django.db.models import Q


class UserManager(models.Manager):
    """Custom manager for User model."""
    
    def get_by_natural_key(self, email):
        """Get user by email (natural key)."""
        return self.get(email=email)
    
    def create_user(self, email, password=None, full_name='', **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password) if password else user.set_unusable_password()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, full_name='', **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, full_name, **extra_fields)


class User(models.Model):
    """Django User model for authentication."""
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    password_hash = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = "auth_user"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]
    
    @property
    def is_anonymous(self) -> bool:
        """Return False, as this is an authenticated user."""
        return False
    
    @property
    def is_authenticated(self) -> bool:
        """Return True, as this is an authenticated user."""
        return True
    
    def get_username(self) -> str:
        """Return the email as username."""
        return self.email
    
    def set_password(self, raw_password):
        """Set password using Django's hashing."""
        if raw_password:
            self.password_hash = make_password(raw_password)
        else:
            self.password_hash = None
    
    def set_unusable_password(self):
        """Mark password as unusable."""
        self.password_hash = None
    
    def check_password(self, raw_password):
        """Check if provided password matches stored password using Django's hashing."""
        if self.password_hash is None or not raw_password:
            return False
        return check_password(raw_password, self.password_hash)
    
    def has_perm(self, perm, obj=None):
        """Check if user has a specific permission. Superusers have all permissions."""
        if self.is_superuser:
            return True
        return perm in self.permission_codes
    
    def has_module_perms(self, app_label):
        """Check if user has any permission in an app. Superusers have all permissions."""
        if self.is_superuser:
            return True
        return any(permission.startswith(f"{app_label}.") for permission in self.get_all_permissions())

    def get_all_permissions(self, obj=None):
        """Get Django-style permissions for admin/Jazzmin compatibility."""
        if self.is_superuser:
            try:
                from django.contrib.auth.models import Permission

                return {
                    f"{permission.content_type.app_label}.{permission.codename}"
                    for permission in Permission.objects.select_related("content_type")
                }
            except Exception:
                return set()
        return {code for code in self.permission_codes if code.count(".") == 1}

    @property
    def role(self) -> str | None:
        """Resolve the user's role from UserRole mapping when available."""
        if self.is_superuser or self.is_staff:
            return "ADMIN"
        try:
            from apps.admin.infrastructure.orm_admin_extended import UserRole
            today = timezone.localdate()
            user_role = (
                UserRole.objects
                .select_related("role")
                .filter(
                    user_id=str(self.id),
                    status="active",
                )
                .filter(Q(effective_from__isnull=True) | Q(effective_from__lte=today))
                .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
                .order_by("-is_primary", "-assigned_at")
                .first()
            )
            return user_role.role.code if user_role else None
        except Exception:
            return None

    @property
    def permission_codes(self) -> set[str]:
        if self.is_superuser or self.is_staff:
            try:
                from apps.admin.infrastructure.orm_admin_extended import Permission as AdminPermission
                return set(AdminPermission.objects.values_list("code", flat=True))
            except Exception:
                return set()
        try:
            from apps.admin.infrastructure.orm_admin_extended import UserRole
            today = timezone.localdate()
            user_roles = (
                UserRole.objects
                .select_related("role")
                .prefetch_related("role__permissions")
                .filter(
                    user_id=str(self.id),
                    status="active",
                )
                .filter(Q(effective_from__isnull=True) | Q(effective_from__lte=today))
                .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
            )
            codes: set[str] = set()
            for user_role in user_roles:
                codes.update(user_role.role.permissions.values_list("code", flat=True))
            return codes
        except Exception:
            return set()
    
    def __str__(self) -> str:
        return self.email


class AuthToken(models.Model):
    """Django model for auth tokens."""
    
    TOKEN_TYPE_CHOICES = [
        ("Bearer", "Bearer"),
        ("Basic", "Basic"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    access_token = models.CharField(max_length=255, unique=True, db_index=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True, unique=True, db_index=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES, default="Bearer")
    expires_at = models.DateTimeField(null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "auth_token"
        indexes = [
            models.Index(fields=["access_token"]),
            models.Index(fields=["user", "is_valid"]),
            models.Index(fields=["expires_at"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.token_type}"
