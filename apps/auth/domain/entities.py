"""Auth domain entities."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from shared.domain.base_entity import BaseEntity


@dataclass
class User(BaseEntity):
    """User domain entity for authentication."""
    
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    is_active: bool = True
    last_login: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
    
    def is_login_allowed(self) -> bool:
        """Check if user is allowed to login."""
        return self.is_active


@dataclass
class AuthToken(BaseEntity):
    """Auth token domain entity."""
    
    user_id: UUID = field(default_factory=lambda: UUID("00000000-0000-0000-0000-000000000000"))
    access_token: str = ""
    refresh_token: str | None = None
    token_type: str = "Bearer"
    expires_at: datetime | None = None
    is_valid: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def has_expired(self) -> bool:
        """Check if token has expired or is invalid."""
        return self.is_expired() or not self.is_valid
    
    def revoke(self) -> None:
        """Revoke the token."""
        self.is_valid = False
