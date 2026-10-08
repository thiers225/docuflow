from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from docuflow.db.models import FieldSource


class ExtractionFieldRead(BaseModel):
    id: int
    field_name: str
    raw_value: str | None
    corrected_value: str | None
    source: FieldSource
    page: int | None
    location: str | None

    model_config = {"from_attributes": True}


class ExtractionRead(BaseModel):
    id: int
    document_id: int
    engine: str
    engine_version: str | None
    prompt_config: str | None

    # Identification
    invoice_number: str | None
    invoice_date: str | None
    supplier: str | None
    client: str | None

    # Montants
    total_ht: Decimal | None
    tax_amount: Decimal | None
    total_ttc: Decimal | None
    currency: str | None
    due_date: str | None

    created_at: datetime
    fields: list[ExtractionFieldRead] = []

    model_config = {"from_attributes": True}
