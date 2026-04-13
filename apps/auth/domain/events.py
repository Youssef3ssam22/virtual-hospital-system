"""Auth domain events."""
from dataclasses import dataclass
from uuid import UUID

from shared.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class UserLoggedIn(DomainEvent):
    """Event fired when user logs in."""
    
    user_id: UUID = None
    email: str = ""


@dataclass(frozen=True)
class UserLoggedOut(DomainEvent):
    """Event fired when user logs out."""
    
    user_id: UUID = None
    email: str = ""


@dataclass(frozen=True)
class UserCreated(DomainEvent):
    """Event fired when new user is created."""
    
    user_id: UUID = None
    email: str = ""
    full_name: str = ""
