"""Model registry for the lab app."""
from apps.lab.infrastructure.orm_models import (
    LabOrder, Specimen, LabResult, CriticalValue, LabReport, AnalyzerQueue, RecollectionRequest
)

__all__ = [
    'LabOrder', 'Specimen', 'LabResult', 'CriticalValue',
    'LabReport', 'AnalyzerQueue', 'RecollectionRequest',
]
