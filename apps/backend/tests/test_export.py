"""Tests unitaires des fonctions d'export."""

import json
from decimal import Decimal
from unittest.mock import MagicMock


def _make_extraction(
    invoice_number: str | None = "CIE-2026-08741",
    total_ht: str = "3215000",
    total_ttc: str = "3793700",
    corrected_ttc: str | None = None,
) -> MagicMock:
    extraction = MagicMock()
    extraction.id = 1
    extraction.engine = "rules"
    extraction.engine_version = "0.1.0"
    extraction.created_at.isoformat.return_value = "2026-10-08T10:00:00+00:00"
    extraction.invoice_number = invoice_number
    extraction.invoice_date = "01/10/2026"
    extraction.supplier = "CIE — COMPAGNIE IVOIRIENNE D'ÉLECTRICITÉ"
    extraction.client = "BRASSERIES IVOIRIENNES RÉUNIES SARL"
    extraction.total_ht = Decimal(total_ht)
    extraction.tax_amount = Decimal("578700")
    extraction.total_ttc = Decimal(total_ttc)
    extraction.currency = "FCFA"
    extraction.due_date = "31/10/2026"
    extraction.prompt_config = None

    field = MagicMock()
    field.field_name = "total_ttc"
    field.raw_value = total_ttc
    field.corrected_value = corrected_ttc
    field.source = "corrected" if corrected_ttc else "extracted"
    field.page = 1
    field.location = None
    extraction.fields = [field]
    extraction.checks = []
    return extraction


def _make_document(extraction: MagicMock | None = None) -> MagicMock:
    document = MagicMock()
    document.id = 1
    document.filename = "facture_001_cie.pdf"
    document.status = "done"
    document.created_at.isoformat.return_value = "2026-10-08T09:00:00+00:00"
    document.extractions = [extraction] if extraction else []
    return document


def test_export_json_structure() -> None:
    from docuflow.services.export import export_json

    doc = _make_document(_make_extraction())
    output = json.loads(export_json(doc))

    assert "export_date" in output
    assert output["document"]["filename"] == "facture_001_cie.pdf"
    assert len(output["extractions"]) == 1
    ext = output["extractions"][0]
    assert ext["fields"]["invoice_number"] == "CIE-2026-08741"
    assert ext["fields"]["total_ht"] == "3215000"


def test_export_json_no_scientific_notation() -> None:
    from docuflow.services.export import export_json

    doc = _make_document(_make_extraction(total_ht="3215000", total_ttc="3793700"))
    output = json.loads(export_json(doc))
    ext = output["extractions"][0]

    assert "E" not in ext["fields"]["total_ht"]
    assert "E" not in ext["fields"]["total_ttc"]


def test_export_csv_uses_corrected_value() -> None:
    from docuflow.services.export import export_csv

    extraction = _make_extraction(total_ttc="380000", corrected_ttc="365800")
    doc = _make_document(extraction)
    csv_bytes = export_csv(doc)
    csv_text = csv_bytes.decode("utf-8-sig")

    assert "365800" in csv_text
    assert "380000" not in csv_text.split("\n")[1]  # ligne de données, pas l'en-tête


def test_export_csv_header() -> None:
    from docuflow.services.export import export_csv

    doc = _make_document(_make_extraction())
    csv_text = export_csv(doc).decode("utf-8-sig")
    header = csv_text.split("\n")[0]

    assert "invoice_number" in header
    assert "total_ttc" in header
    assert "currency" in header
