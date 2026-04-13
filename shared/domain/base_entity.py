"""shared/domain/base_entity.py — Base class for all domain entities.

Pure Python dataclass — no Django dependency. Persistence fields like
created_at and updated_at belong on ORM models, not domain entities.
"""
import uuid
from dataclasses import dataclass, field


@dataclass
class BaseEntity:
    """All domain entities inherit from this.

    Identity is based solely on the id field — two entities of the same
    class with the same id are considered equal regardless of other attributes.
    This matches the Domain-Driven Design definition of entity identity.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"