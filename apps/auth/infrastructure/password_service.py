"""Password hashing and verification service."""
from passlib.context import CryptContext

# Configure password hashing - using PBKDF2 which is pure Python and has no external dependencies
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class PasswordService:
    """Service for password hashing and verification."""
    
    @staticmethod
    def hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
