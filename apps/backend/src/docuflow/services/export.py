import csv
import io
import json
from datetime import datetime
from decimal import Decimal

from docuflow.db.models import Document, Extraction


def _decimal_to_str(value: object) -> str | None:
    if value is None:
        return None
    return str(Decimal(str(value)).normalize())


def _extraction_to_dict(extraction: Extraction) -> dict:
    return {
        "id": extraction.id,
        "engine": extraction.engine,
        "engine_version": extraction.engine_version,
        "extracted_at": extraction.created_at.isoformat() if extraction.created_at else None,
        "fields": {
            "invoice_number": extraction.invoice_number,
            "invoice_date": extraction.invoice_date,
            "supplier": extraction.supplier,
            "client": extraction.client,
            "total_ht": _decimal_to_str(extraction.total_ht),
            "tax_amount": _decimal_to_str(extraction.tax_amount),
            "total_ttc": _decimal_to_str(extraction.total_ttc),
            "currency": extraction.currency,
            "due_date": extraction.due_date,
        },
        "corrections": [
            {
                "field_name": f.field_name,
                "raw_value": f.raw_value,
                "corrected_value": f.corrected_value,
                "source": f.source,
                "page": f.page,
                "location": f.location,
            }
            for f in extraction.fields
            if f.corrected_value is not None
        ],
        "checks": [
            {
                "rule": c.rule,
                "passed": c.passed,
                "severity": c.severity,
                "message": c.message,
            }
            for c in extraction.checks
        ],
    }


def export_json(document: Document) -> str:
    """Sérialise un document et ses extractions en JSON."""
    data = {
        "export_date": datetime.utcnow().isoformat() + "Z",
        "document": {
            "id": document.id,
            "filename": document.filename,
            "status": document.status,
            "created_at": document.created_at.isoformat() if document.created_at else None,
        },
        "extractions": [_extraction_to_dict(e) for e in document.extractions],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_csv(document: Document) -> bytes:
    """Sérialise la dernière extraction d'un document en CSV (UTF-8 avec BOM)."""
    output = io.StringIO()

    fieldnames = [
        "document_id",
        "filename",
        "extraction_id",
        "engine",
        "invoice_number",
        "invoice_date",
        "supplier",
        "client",
        "total_ht",
        "tax_amount",
        "total_ttc",
        "currency",
        "due_date",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for extraction in document.extractions:
        writer.writerow({
            "document_id": document.id,
            "filename": document.filename,
            "extraction_id": extraction.id,
            "engine": extraction.engine,
            "invoice_number": extraction.invoice_number or "",
            "invoice_date": extraction.invoice_date or "",
            "supplier": extraction.supplier or "",
            "client": extraction.client or "",
            "total_ht": _decimal_to_str(extraction.total_ht) or "",
            "tax_amount": _decimal_to_str(extraction.tax_amount) or "",
            "total_ttc": _decimal_to_str(extraction.total_ttc) or "",
            "currency": extraction.currency or "",
            "due_date": extraction.due_date or "",
        })

    return output.getvalue().encode("utf-8-sig")
