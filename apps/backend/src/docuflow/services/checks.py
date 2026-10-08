from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation


@dataclass
class CheckResult:
    rule: str
    passed: bool
    severity: str  # "error" | "warning"
    message: str


AMOUNT_TOLERANCE = Decimal("1.00")  # tolérance d'arrondi en FCFA/unité


def _parse_decimal(value: str | Decimal | None) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def _parse_date(value: str | None) -> datetime | None:
    if value is None:
        return None
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def run_checks(
    invoice_number: str | None,
    invoice_date: str | None,
    due_date: str | None,
    total_ht: object,
    tax_amount: object,
    total_ttc: object,
) -> list[CheckResult]:
    """Exécute tous les contrôles métier et retourne les résultats."""
    results: list[CheckResult] = []

    # ── Contrôle 1 : numéro de facture présent ────────────────────────────────
    results.append(
        CheckResult(
            rule="invoice_number_present",
            passed=bool(invoice_number and invoice_number.strip()),
            severity="error",
            message=(
                "Numéro de facture présent."
                if invoice_number
                else "Numéro de facture absent ou non extrait."
            ),
        )
    )

    # ── Contrôle 2 : date de facture présente ─────────────────────────────────
    results.append(
        CheckResult(
            rule="invoice_date_present",
            passed=bool(invoice_date),
            severity="warning",
            message=(
                "Date de facture présente."
                if invoice_date
                else "Date de facture absente ou non extraite."
            ),
        )
    )

    # ── Contrôle 3 : cohérence des montants (HT + taxe = TTC) ─────────────────
    ht = _parse_decimal(total_ht)
    tax = _parse_decimal(tax_amount)
    ttc = _parse_decimal(total_ttc)

    if ht is not None and tax is not None and ttc is not None:
        expected = ht + tax
        diff = abs(expected - ttc)
        passed = diff <= AMOUNT_TOLERANCE
        results.append(
            CheckResult(
                rule="amounts_coherent",
                passed=passed,
                severity="error",
                message=(
                    f"Cohérence des montants vérifiée (HT {ht} + taxe {tax} = TTC {ttc})."
                    if passed
                    else (
                        f"Incohérence des montants : HT {ht} + taxe {tax} = {expected}, "
                        f"mais TTC extrait = {ttc} (écart : {diff})."
                    )
                ),
            )
        )
    else:
        results.append(
            CheckResult(
                rule="amounts_coherent",
                passed=False,
                severity="warning",
                message="Contrôle des montants impossible : un ou plusieurs montants sont absents.",
            )
        )

    # ── Contrôle 4 : montants positifs ────────────────────────────────────────
    for label, value in [("HT", ht), ("taxe", tax), ("TTC", ttc)]:
        if value is not None:
            results.append(
                CheckResult(
                    rule=f"amount_{label.lower()}_positive",
                    passed=value >= Decimal("0"),
                    severity="error",
                    message=(
                        f"Montant {label} positif ({value})."
                        if value >= Decimal("0")
                        else f"Montant {label} négatif ({value})."
                    ),
                )
            )

    # ── Contrôle 5 : date facture antérieure à l'échéance ────────────────────
    d_invoice = _parse_date(invoice_date)
    d_due = _parse_date(due_date)

    if d_invoice is not None and d_due is not None:
        passed = d_invoice <= d_due
        results.append(
            CheckResult(
                rule="date_order",
                passed=passed,
                severity="error",
                message=(
                    f"Date de facture ({invoice_date}) antérieure à l'échéance ({due_date})."
                    if passed
                    else (
                        f"Date de facture ({invoice_date}) postérieure à l'échéance ({due_date})."
                    )
                ),
            )
        )

    return results
