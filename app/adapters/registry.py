from typing import Dict
from .base import SourceAdapter
from ..settings import settings
from .computrabajo import ComputrabajoAdapter
try:
    from .linkedin import LinkedInAdapter
except Exception:
    LinkedInAdapter = None

def get_registry() -> Dict[str, type]:
    reg: Dict[str, type] = {}
    if settings.ENABLE_COMPUTRABAJO:
        reg["computrabajo"] = ComputrabajoAdapter
    if settings.ENABLE_LINKEDIN and LinkedInAdapter:
        reg["linkedin"] = LinkedInAdapter
    return reg
