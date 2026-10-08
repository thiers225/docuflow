"""Tests unitaires des contrôles métier."""

from decimal import Decimal

from docuflow.services.checks import run_checks


def test_coherent_amounts_pass():
    results = run_checks(
        invoice_number="CIE-2026-08741",
        invoice_date="01/10/2026",
        due_date="31/10/2026",
        total_ht=Decimal("3215000"),
        tax_amount=Decimal("578700"),
        total_ttc=Decimal("3793700"),
    )
    by_rule = {r.rule: r for r in results}
    assert by_rule["amounts_coherent"].passed is True
    assert by_rule["invoice_number_present"].passed is True
    assert by_rule["date_order"].passed is True


def test_incoherent_amounts_fail():
    results = run_checks(
        invoice_number="OCl-2026-004412",
        invoice_date="15/09/2026",
        due_date="15/10/2026",
        total_ht=Decimal("310000"),
        tax_amount=Decimal("55800"),
        total_ttc=Decimal("380000"),  # devrait être 365800
    )
    by_rule = {r.rule: r for r in results}
    assert by_rule["amounts_coherent"].passed is False
    assert by_rule["amounts_coherent"].severity == "error"


def test_missing_invoice_number_fails():
    results = run_checks(
        invoice_number=None,
        invoice_date="20/09/2026",
        due_date=None,
        total_ht=Decimal("2775000"),
        tax_amount=Decimal("499500"),
        total_ttc=Decimal("3274500"),
    )
    by_rule = {r.rule: r for r in results}
    assert by_rule["invoice_number_present"].passed is False


def test_date_order_fail():
    results = run_checks(
        invoice_number="FACT-001",
        invoice_date="31/10/2026",
        due_date="01/10/2026",  # échéance avant la date de facture
        total_ht=None,
        tax_amount=None,
        total_ttc=None,
    )
    by_rule = {r.rule: r for r in results}
    assert by_rule["date_order"].passed is False
