from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from docuflow.db.models import DocumentStatus
from docuflow.schemas.extraction import ExtractionRead


class DocumentBase(BaseModel):
    filename: str


class DocumentRead(DocumentBase):
    id: int
    status: DocumentStatus
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "filename": "facture_001_cie.pdf",
                    "status": "pending",
                    "created_at": "2026-10-05T08:30:00Z",
                }
            ]
        },
    }


class DocumentDetail(DocumentRead):
    """Document avec ses extractions et le détail des champs."""

    extractions: list[ExtractionRead] = []

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "filename": "facture_001_cie.pdf",
                    "status": "done",
                    "created_at": "2026-10-05T08:30:00Z",
                    "extractions": [
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
                            "created_at": "2026-10-05T08:31:00Z",
                            "fields": [
                                {
                                    "id": 1,
                                    "field_name": "invoice_number",
                                    "raw_value": "FACT-2026-00142",
                                    "corrected_value": None,
                                    "source": "extracted",
                                    "page": 1,
                                    "location": None,
                                }
                            ],
                        }
                    ],
                }
            ]
        },
    }
