"""Login use case with JWT token generation."""
from dataclasses import dataclass
from datetime import datetime, timedelta
import secrets
from uuid import UUID

from apps.auth.domain.entities import User, AuthToken
from apps.auth.domain.events import UserLoggedIn
from apps.auth.domain.repositories import UserRepository, TokenRepository
from apps.auth.infrastructure.password_service import PasswordService
from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.exceptions import EntityNotFound, InvalidOperation


@dataclass
class LoginCommand:
    """Command to login user."""
    email: str
    password: str


class LoginUseCase:
    """Use case for user login with token generation."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: TokenRepository,
        password_service: PasswordService,
        unit_of_work: UnitOfWork,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.password_service = password_service
        self.unit_of_work = unit_of_work
    
    def execute(self, command: LoginCommand) -> dict:
        """
        Execute login.
        
        Returns:
            dict with access_token and user info
        
        Raises:
            EntityNotFound: If user doesn't exist
            InvalidOperation: If credentials are invalid
        """
        # Find user by email
        user = self.user_repo.get_by_email(command.email)
        if user is None:
            raise EntityNotFound(f"User with email {command.email} not found")
        
        # Check if user is active
        if not user.is_login_allowed():
            raise InvalidOperation("User account is inactive")
        
        # Verify password
        if not self.password_service.verify(command.password, user.password_hash):
            raise InvalidOperation("Invalid credentials")
        
        # Update last login
        user.update_last_login()
        self.user_repo.update(user)
        
        # Generate tokens
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        # Create auth token entity
        token = AuthToken(
            id=UUID(int=0),  # Will be replaced by repository
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        
        # Save token
        saved_token = self.token_repo.add(token)
        
        # Publish event
        event = UserLoggedIn(user_id=user.id, email=user.email)
        self.unit_of_work.collect(event)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 86400,  # 24 hours in seconds
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        }
