"""Tests unitaires de l'extracteur par règles."""

from pathlib import Path

import pytest

from docuflow.extractors.rules import RulesExtractor

INVOICES = Path(__file__).parent.parent.parent.parent / "examples" / "invoices"


def invoice(name: str) -> str:
    path = INVOICES / name
    if not path.exists():
        pytest.skip(f"Facture de test absente : {path}")
    return str(path)


@pytest.fixture
def extractor() -> RulesExtractor:
    return RulesExtractor()


def test_engine_metadata(extractor: RulesExtractor) -> None:
    assert extractor.engine_name == "rules"
    assert extractor.engine_version == "0.1.0"


def test_facture_cie(extractor: RulesExtractor) -> None:
    result = extractor.extract(invoice("facture_001_cie.pdf"))

    assert result.invoice_number == "CIE-2026-08741"
    assert result.invoice_date == "01/10/2026"
    assert result.due_date == "31/10/2026"
    assert result.supplier == "CIE — COMPAGNIE IVOIRIENNE D'ÉLECTRICITÉ"
    assert result.client == "BRASSERIES IVOIRIENNES RÉUNIES SARL"
    assert result.total_ht == "3215000"
    assert result.tax_amount == "578700"
    assert result.total_ttc == "3793700"
    assert result.currency == "FCFA"


def test_facture_orange(extractor: RulesExtractor) -> None:
    result = extractor.extract(invoice("facture_002_orange_ci.pdf"))

    assert result.invoice_number == "OCl-2026-004412"
    assert result.invoice_date == "15/09/2026"
    assert result.due_date == "15/10/2026"
    assert result.supplier == "ORANGE CÔTE D'IVOIRE SA"
    assert result.client == "CABINET KOUASSI & PARTENAIRES"
    assert result.total_ht == "310000"
    assert result.tax_amount == "55800"
    assert result.total_ttc == "380000"
    assert result.currency == "FCFA"


def test_facture_saf_logistics_no_invoice_number(extractor: RulesExtractor) -> None:
    """La facture SAF Logistics n'a pas de numéro — c'est un cas de test intentionnel."""
    result = extractor.extract(invoice("facture_003_saf_logistics.pdf"))

    assert result.invoice_number is None
    assert result.invoice_date == "20/09/2026"
    assert result.due_date is None
    assert result.supplier == "SAF LOGISTICS CÔTE D'IVOIRE"
    assert result.client == "NESTLÉ CÔTE D'IVOIRE SA"
    assert result.currency == "FCFA"


def test_fields_are_recorded(extractor: RulesExtractor) -> None:
    """Chaque champ extrait doit avoir une entrée dans fields."""
    result = extractor.extract(invoice("facture_001_cie.pdf"))

    field_names = {f.field_name for f in result.fields}
    assert "invoice_number" in field_names
    assert "total_ttc" in field_names
    assert all(f.source == "extracted" for f in result.fields)


def test_unsupported_format_raises(extractor: RulesExtractor, tmp_path: Path) -> None:
    fake = tmp_path / "test.docx"
    fake.write_text("fake")
    with pytest.raises(ValueError, match="ne supporte que les PDF"):
        extractor.extract(str(fake))
