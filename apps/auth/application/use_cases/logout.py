"""Logout use case with token revocation."""
from dataclasses import dataclass
from uuid import UUID

from apps.auth.domain.events import UserLoggedOut
from apps.auth.domain.repositories import TokenRepository, UserRepository
from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.exceptions import EntityNotFound


@dataclass
class LogoutCommand:
    """Command to logout user."""
    user_id: UUID
    access_token: str


class LogoutUseCase:
    """Use case for user logout and token revocation."""
    
    def __init__(
        self,
        token_repo: TokenRepository,
        user_repo: UserRepository,
        unit_of_work: UnitOfWork,
    ):
        self.token_repo = token_repo
        self.user_repo = user_repo
        self.unit_of_work = unit_of_work
    
    def execute(self, command: LogoutCommand) -> dict:
        """
        Execute logout.
        
        Returns:
            dict with success status
        
        Raises:
            EntityNotFound: If user doesn't exist
        """
        # Verify user exists
        user = self.user_repo.get_by_id(command.user_id)
        if user is None:
            raise EntityNotFound(f"User with id {command.user_id} not found")
        
        # Get token and revoke it
        token = self.token_repo.get_by_access_token(command.access_token)
        if token:
            token.revoke()
            # Optionally: could also revoke all tokens for the user
            # self.token_repo.revoke_by_user(user.id)
        
        # Publish event
        event = UserLoggedOut(user_id=user.id, email=user.email)
        self.unit_of_work.collect(event)
        
        return {
            "status": "success",
            "message": "User logged out successfully",
        }
