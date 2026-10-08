from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from docuflow.db.models import FieldSource
from docuflow.schemas.check import ExtractionCheckRead


class ExtractionFieldRead(BaseModel):
    id: int
    field_name: str
    raw_value: str | None
    corrected_value: str | None
    source: FieldSource
    page: int | None
    location: str | None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "field_name": "invoice_number",
                    "raw_value": "FACT-2026-00142",
                    "corrected_value": None,
                    "source": "extracted",
                    "page": 1,
                    "location": "x1=52, y1=120, x2=210, y2=135",
                }
            ]
        },
    }


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
    checks: list[ExtractionCheckRead] = []

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "document_id": 1,
                    "engine": "rules",
                    "engine_version": "0.1.0",
                    "prompt_config": None,
                    "invoice_number": "FACT-2026-00142",
                    "invoice_date": "2026-09-15",
                    "supplier": "CIE — COMPAGNIE IVOIRIENNE D'ÉLECTRICITÉ",
                    "client": "BRASSERIES IVOIRIENNES RÉUNIES SARL",
                    "total_ht": "185000.00",
                    "tax_amount": "33300.00",
                    "total_ttc": "218300.00",
                    "currency": "FCFA",
                    "due_date": "2026-10-15",
                    "created_at": "2026-10-05T08:30:00Z",
                    "fields": [
                        {
                            "id": 1,
                            "field_name": "invoice_number",
                            "raw_value": "FACT-2026-00142",
                            "corrected_value": None,
                            "source": "extracted",
                            "page": 1,
                            "location": "x1=52, y1=120, x2=210, y2=135",
                        },
                        {
                            "id": 2,
                            "field_name": "total_ttc",
                            "raw_value": "218 300 FCFA",
                            "corrected_value": None,
                            "source": "extracted",
                            "page": 1,
                            "location": "x1=400, y1=520, x2=550, y2=535",
                        },
                    ],
                }
            ]
        },
    }
