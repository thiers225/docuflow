from datetime import datetime

from pydantic import BaseModel

from docuflow.db.models import DocumentStatus


class DocumentBase(BaseModel):
    filename: str


class DocumentCreate(DocumentBase):
    original_path: str


class DocumentRead(DocumentBase):
    id: int
    status: DocumentStatus
    created_at: datetime

    model_config = {"from_attributes": True}
