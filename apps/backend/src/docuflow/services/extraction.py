from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from docuflow.db.models import (
    Document,
    DocumentStatus,
    Extraction,
    ExtractionCheck,
    ExtractionField,
)
from docuflow.extractors.base import BaseExtractor, ExtractionResult
from docuflow.services.checks import run_checks


def _to_decimal(value: str | None) -> Decimal | None:
    """Convertit une chaîne en Decimal en nettoyant les espaces et virgules."""
    if value is None:
        return None
    cleaned = value.replace(" ", "").replace(",", ".")
    cleaned = "".join(c for c in cleaned if c.isdigit() or c == ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


async def run_extraction(
    document: Document,
    extractor: BaseExtractor,
    db: AsyncSession,
) -> Extraction:
    """Lance l'extraction sur un document et sauvegarde les résultats."""

    # Marquer le document comme en cours
    document.status = DocumentStatus.processing
    await db.commit()

    try:
        result: ExtractionResult = extractor.extract(document.original_path)

        # Créer l'entrée extraction
        extraction = Extraction(
            document_id=document.id,
            engine=result.engine,
            engine_version=result.engine_version,
            prompt_config=result.prompt_config,
            invoice_number=result.invoice_number,
            invoice_date=result.invoice_date,
            supplier=result.supplier,
            client=result.client,
            total_ht=_to_decimal(result.total_ht),
            tax_amount=_to_decimal(result.tax_amount),
            total_ttc=_to_decimal(result.total_ttc),
            currency=result.currency,
            due_date=result.due_date,
        )
        db.add(extraction)
        await db.flush()

        # Sauvegarder les fields avec provenance
        for field in result.fields:
            db.add(
                ExtractionField(
                    extraction_id=extraction.id,
                    field_name=field.field_name,
                    raw_value=field.raw_value,
                    source=field.source,
                    page=field.page,
                    location=field.location,
                )
            )

        # Exécuter les contrôles métier
        check_results = run_checks(
            invoice_number=result.invoice_number,
            invoice_date=result.invoice_date,
            due_date=result.due_date,
            total_ht=_to_decimal(result.total_ht),
            tax_amount=_to_decimal(result.tax_amount),
            total_ttc=_to_decimal(result.total_ttc),
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

        # Marquer le document comme traité
        document.status = DocumentStatus.done
        await db.commit()

        # Recharger avec toutes les relations
        await db.refresh(extraction)
        result_with_relations = await db.execute(
            select(Extraction)
            .where(Extraction.id == extraction.id)
            .options(
                selectinload(Extraction.fields),
                selectinload(Extraction.checks),
            )
        )
        return result_with_relations.scalar_one()

    except Exception:
        document.status = DocumentStatus.error
        await db.commit()
        raise
