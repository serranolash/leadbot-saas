from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Tenant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Credentials(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(index=True)
    provider: str
    enc_payload: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JobConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(index=True)
    query: str
    target_count: int = 30
    min_score: int = 6
    min_groups: int = 2
    min_years: int = 0
    sources_csv: str = "linkedin,computrabajo"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Run(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(index=True)
    job_id: int = Field(index=True)
    status: str = "queued"
    logs: Optional[str] = None
    output_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
