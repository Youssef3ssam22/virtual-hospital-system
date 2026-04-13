"""Department domain entity."""
from uuid import UUID
from dataclasses import dataclass


@dataclass
class Department:
    """Department entity."""
    id: UUID
    name: str
    code: str
    department_type: str
    description: str
    head_id: str  # User ID
    manager_name: str
    location: str
    floor: str
    extension_phone: str
    operating_hours: str
    is_clinical: bool
    status: str  # active | inactive
    created_at: str
    
    def is_active(self) -> bool:
        """Check if department is active."""
        return self.status == "active"
    
    def activate(self) -> None:
        """Activate department."""
        self.status = "active"
    
    def deactivate(self) -> None:
        """Deactivate department."""
        self.status = "inactive"


@dataclass
class Ward:
    """Ward entity."""
    id: UUID
    name: str
    code: str
    department_id: UUID
    type: str  # general | icu | pediatric | maternity
    gender_restriction: str
    age_group: str
    specialty: str
    nurse_station: str
    supports_isolation: bool
    total_beds: int
    available_beds: int
    status: str  # active | maintenance | closed
    created_at: str
    
    def is_available(self) -> bool:
        """Check if ward has available beds."""
        return self.available_beds > 0 and self.status == "active"


@dataclass
class Bed:
    """Bed entity."""
    id: UUID
    room_number: str
    bed_number: str
    ward_id: UUID
    type: str  # standard | private | icu | pediatric
    bed_class: str
    features: list  # oxygen | monitor | ventilator
    status: str  # available | occupied | maintenance | cleaning | blocked
    cleaning_status: str
    blocked_reason: str
    patient_id: str  # User ID if occupied
    created_at: str
    
    def is_available(self) -> bool:
        """Check if bed is available."""
        return self.status == "available"
    
    def occupy(self, patient_id: str) -> None:
        """Mark bed as occupied."""
        self.status = "occupied"
        self.patient_id = patient_id
    
    def release(self) -> None:
        """Mark bed as available."""
        self.status = "available"
        self.patient_id = None
