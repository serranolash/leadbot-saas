from pydantic import BaseModel
from typing import Optional, List

class RunResponse(BaseModel):
    task_id: str

class Lead(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    location: Optional[str]
    years_estimated: Optional[int]
    url: Optional[str]
