"""Register use case for creating new users."""
from dataclasses import dataclass
from uuid import UUID

from apps.auth.domain.entities import User
from apps.auth.domain.events import UserCreated
from apps.auth.domain.repositories import UserRepository
from apps.auth.infrastructure.password_service import PasswordService
from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.exceptions import DuplicateEntity


@dataclass
class RegisterCommand:
    """Command to register new user."""
    email: str
    password: str
    full_name: str


class RegisterUseCase:
    """Use case for user registration."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordService,
        unit_of_work: UnitOfWork,
    ):
        self.user_repo = user_repo
        self.password_service = password_service
        self.unit_of_work = unit_of_work
    
    def execute(self, command: RegisterCommand) -> dict:
        """
        Execute user registration.
        
        Returns:
            dict with user info
        
        Raises:
            DuplicateEntity: If email already exists
        """
        # Check if user already exists
        if self.user_repo.exists_by_email(command.email):
            raise DuplicateEntity("User", command.email)
        
        # Hash password
        password_hash = self.password_service.hash(command.password)
        
        # Create user entity
        user = User(
            id=UUID(int=0),  # Will be replaced by repository
            email=command.email,
            password_hash=password_hash,
            full_name=command.full_name,
            is_active=True,
        )
        
        # Save user
        saved_user = self.user_repo.add(user)
        
        # Publish event
        event = UserCreated(user_id=saved_user.id, email=saved_user.email, full_name=saved_user.full_name)
        self.unit_of_work.collect(event)
        
        return {
            "user_id": str(saved_user.id),
            "email": saved_user.email,
            "full_name": saved_user.full_name,
            "message": "User registered successfully",
        }
