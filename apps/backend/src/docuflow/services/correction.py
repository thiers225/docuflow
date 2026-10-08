from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from docuflow.db.models import (
    Extraction,
    ExtractionCheck,
    ExtractionField,
    FieldSource,
)
from docuflow.services.checks import run_checks


async def correct_field(
    field: ExtractionField,
    corrected_value: str | None,
    db: AsyncSession,
) -> ExtractionField:
    """Applique une correction sur un champ et réexécute les checks."""

    field.corrected_value = corrected_value
    field.source = FieldSource.corrected
    await db.flush()

    # Recharger l'extraction avec tous ses champs pour les checks
    result = await db.execute(
        select(Extraction)
        .where(Extraction.id == field.extraction_id)
        .options(
            selectinload(Extraction.fields),
            selectinload(Extraction.checks),
        )
    )
    extraction = result.scalar_one()

    # Construire les valeurs actuelles (corrigées si disponibles)
    def current(field_name: str, fallback: str | None) -> str | None:
        for f in extraction.fields:
            if f.field_name == field_name:
                return f.corrected_value if f.corrected_value is not None else f.raw_value
        return fallback

    invoice_number = current("invoice_number", extraction.invoice_number)
    invoice_date = current("invoice_date", extraction.invoice_date)
    due_date = current("due_date", extraction.due_date)

    def to_decimal(val: object) -> Decimal | None:
        if val is None:
            return None
        try:
            return Decimal(str(val))
        except Exception:
            return None

    def _str_or_none(val: object) -> str | None:
        return str(val) if val is not None else None

    total_ht = to_decimal(current("total_ht", _str_or_none(extraction.total_ht)))
    tax_amount = to_decimal(current("tax_amount", _str_or_none(extraction.tax_amount)))
    total_ttc = to_decimal(current("total_ttc", _str_or_none(extraction.total_ttc)))

    # Supprimer les anciens checks et en créer de nouveaux
    for check in extraction.checks:
        await db.delete(check)
    await db.flush()

    check_results = run_checks(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        total_ht=total_ht,
        tax_amount=tax_amount,
        total_ttc=total_ttc,
    )

    for check in check_results:
        db.add(
            ExtractionCheck(
                extraction_id=extraction.id,
                rule=check.rule,
                passed=check.passed,
                severity=check.severity,
                message=check.message,
            )
        )

    await db.commit()
    await db.refresh(field)
    return field
