"""Django repository implementations for auth domain contracts."""
from uuid import UUID

from infrastructure.database.base_repository import BaseRepository
from apps.auth.domain.entities import User as DomainUser, AuthToken as DomainAuthToken
from apps.auth.domain.repositories import UserRepository, TokenRepository
from apps.auth.infrastructure.orm_models import User, AuthToken


class DjangoUserRepository(BaseRepository, UserRepository):
    """Django implementation of UserRepository."""
    
    model_class = User
    
    @staticmethod
    def _to_domain(model: User) -> DomainUser:
        """Map ORM model to domain entity."""
        return DomainUser(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            is_active=model.is_active,
            last_login=model.last_login,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def add(self, user: DomainUser) -> DomainUser:
        """Add a new user."""
        model = User.objects.create(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            is_active=user.is_active,
            last_login=user.last_login,
        )
        return self._to_domain(model)
    
    def get_by_id(self, user_id: UUID) -> DomainUser | None:
        """Get user by ID."""
        model = super().get_by_id(user_id)
        return self._to_domain(model) if model else None
    
    def get_by_email(self, email: str) -> DomainUser | None:
        """Get user by email."""
        try:
            model = User.objects.get(email=email)
            return self._to_domain(model)
        except User.DoesNotExist:
            return None
    
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return User.objects.filter(email=email).exists()
    
    def update(self, user: DomainUser) -> DomainUser:
        """Update user."""
        model = User.objects.get(id=user.id)
        model.email = user.email
        model.password_hash = user.password_hash
        model.full_name = user.full_name
        model.is_active = user.is_active
        model.last_login = user.last_login
        model.save(
            update_fields=[
                "email",
                "password_hash",
                "full_name",
                "is_active",
                "last_login",
                "updated_at",
            ]
        )
        return self._to_domain(model)


class DjangoTokenRepository(BaseRepository, TokenRepository):
    """Django implementation of TokenRepository."""
    
    model_class = AuthToken
    
    @staticmethod
    def _to_domain(model: AuthToken) -> DomainAuthToken:
        """Map ORM model to domain entity."""
        return DomainAuthToken(
            id=model.id,
            user_id=model.user_id,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
            token_type=model.token_type,
            expires_at=model.expires_at,
            is_valid=model.is_valid,
            created_at=model.created_at,
        )
    
    def add(self, token: DomainAuthToken) -> DomainAuthToken:
        """Add a new token."""
        model = AuthToken.objects.create(
            user_id=token.user_id,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            expires_at=token.expires_at,
            is_valid=token.is_valid,
        )
        return self._to_domain(model)
    
    def get_by_access_token(self, access_token: str) -> DomainAuthToken | None:
        """Get token by access token string."""
        try:
            model = AuthToken.objects.get(access_token=access_token)
            return self._to_domain(model)
        except AuthToken.DoesNotExist:
            return None
    
    def get_by_refresh_token(self, refresh_token: str) -> DomainAuthToken | None:
        """Get token by refresh token string."""
        try:
            model = AuthToken.objects.get(refresh_token=refresh_token)
            return self._to_domain(model)
        except AuthToken.DoesNotExist:
            return None
    
    def revoke_by_user(self, user_id: UUID) -> None:
        """Revoke all tokens for a user."""
        AuthToken.objects.filter(user_id=user_id).update(is_valid=False)
    
    def get_active_token_for_user(self, user_id: UUID) -> DomainAuthToken | None:
        """Get the currently active token for a user."""
        try:
            model = AuthToken.objects.filter(user_id=user_id, is_valid=True).latest("created_at")
            return self._to_domain(model)
        except AuthToken.DoesNotExist:
            return None
