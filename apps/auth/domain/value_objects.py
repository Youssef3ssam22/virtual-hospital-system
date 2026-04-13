"""Auth domain value objects."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """Email value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid email: {self.value}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Password value object with validation."""
    
    value: str
    
    def __post_init__(self):
        """Validate password strength."""
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in self.value):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.isdigit() for c in self.value):
            raise ValueError("Password must contain at least one digit")
    
    def __str__(self) -> str:
        return "*" * len(self.value)
