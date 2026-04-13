"""Auth domain repository contracts (ports)."""
from abc import ABC, abstractmethod
from uuid import UUID

from apps.auth.domain.entities import User, AuthToken


class UserRepository(ABC):
    """Abstract repository for User aggregate."""
    
    @abstractmethod
    def add(self, user: User) -> User:
        """Add a new user."""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Update user."""
        pass


class TokenRepository(ABC):
    """Abstract repository for AuthToken aggregate."""
    
    @abstractmethod
    def add(self, token: AuthToken) -> AuthToken:
        """Add a new token."""
        pass
    
    @abstractmethod
    def get_by_access_token(self, access_token: str) -> AuthToken | None:
        """Get token by access token string."""
        pass
    
    @abstractmethod
    def get_by_refresh_token(self, refresh_token: str) -> AuthToken | None:
        """Get token by refresh token string."""
        pass
    
    @abstractmethod
    def revoke_by_user(self, user_id: UUID) -> None:
        """Revoke all tokens for a user."""
        pass
    
    @abstractmethod
    def get_active_token_for_user(self, user_id: UUID) -> AuthToken | None:
        """Get the currently active token for a user."""
        pass
