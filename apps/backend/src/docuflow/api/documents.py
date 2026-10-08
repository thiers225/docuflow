from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from docuflow.db.database import get_db
from docuflow.db.models import Document, Extraction, ExtractionField
from docuflow.extractors.rules import RulesExtractor
from docuflow.schemas.check import ExtractionCheckRead
from docuflow.schemas.correction import FieldCorrection
from docuflow.schemas.document import DocumentDetail, DocumentRead
from docuflow.schemas.extraction import ExtractionFieldRead, ExtractionRead
from docuflow.services.correction import correct_field
from docuflow.services.document import save_document
from docuflow.services.export import export_csv, export_json
from docuflow.services.extraction import run_extraction

router = APIRouter(prefix="/documents", tags=["documents"])


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_document_or_404(document_id: int, db: AsyncSession) -> Document:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} introuvable.",
        )
    return document


async def _get_extraction_or_404(
    document_id: int, extraction_id: int, db: AsyncSession
) -> Extraction:
    result = await db.execute(
        select(Extraction)
        .where(Extraction.id == extraction_id, Extraction.document_id == document_id)
        .options(selectinload(Extraction.fields), selectinload(Extraction.checks))
    )
    extraction = result.scalar_one_or_none()
    if extraction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction {extraction_id} introuvable pour le document {document_id}.",
        )
    return extraction


# ── Import ────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Importer un document",
    description="Importe un document PDF, JPEG ou PNG et crée une entrée en base.",
)
async def import_document(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
) -> DocumentRead:
    try:
        document = await save_document(file, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    return document


# ── Liste et consultation ─────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[DocumentRead],
    summary="Lister les documents",
    description="Retourne la liste de tous les documents importés, du plus récent au plus ancien.",
)
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> list[DocumentRead]:
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un document",
    description="Supprime un document et toutes ses extractions.",
)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    document = await _get_document_or_404(document_id, db)
    await db.delete(document)
    await db.commit()


@router.get(
    "/{document_id}",
    response_model=DocumentDetail,
    summary="Consulter un document",
    description="Retourne un document avec toutes ses extractions et le détail des champs.",
)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> DocumentDetail:
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id)
        .options(
            selectinload(Document.extractions).selectinload(Extraction.fields),
            selectinload(Document.extractions).selectinload(Extraction.checks),
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} introuvable.",
        )
    return document


# ── Extraction ────────────────────────────────────────────────────────────────

@router.post(
    "/{document_id}/extract",
    response_model=ExtractionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Extraire les données d'un document",
    description=(
        "Lance l'extraction des champs sur un document importé. "
        "Utilise l'extracteur classique par règles (moteur `rules`)."
    ),
)
async def extract_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> ExtractionRead:
    document = await _get_document_or_404(document_id, db)
    try:
        extraction = await run_extraction(document, RulesExtractor(), db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'extraction : {str(e)}",
        )
    return extraction


# ── Correction ────────────────────────────────────────────────────────────────

@router.patch(
    "/{document_id}/extractions/{extraction_id}/fields/{field_id}",
    response_model=ExtractionFieldRead,
    summary="Corriger un champ extrait",
    description=(
        "Applique une correction manuelle sur un champ extrait. "
        "La valeur originale est conservée dans `raw_value`. "
        "Les contrôles métier sont réexécutés après la correction."
    ),
)
async def correct_extraction_field(
    document_id: int,
    extraction_id: int,
    field_id: int,
    body: FieldCorrection,
    db: AsyncSession = Depends(get_db),
) -> ExtractionFieldRead:
    await _get_document_or_404(document_id, db)
    await _get_extraction_or_404(document_id, extraction_id, db)

    result = await db.execute(
        select(ExtractionField).where(
            ExtractionField.id == field_id,
            ExtractionField.extraction_id == extraction_id,
        )
    )
    field = result.scalar_one_or_none()
    if field is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Champ {field_id} introuvable pour l'extraction {extraction_id}.",
        )

    return await correct_field(field, body.corrected_value, db)


@router.get(
    "/{document_id}/extractions/{extraction_id}/checks",
    response_model=list[ExtractionCheckRead],
    summary="Consulter les contrôles d'une extraction",
    description="Retourne les résultats des contrôles métier pour une extraction.",
)
async def get_extraction_checks(
    document_id: int,
    extraction_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[ExtractionCheckRead]:
    extraction = await _get_extraction_or_404(document_id, extraction_id, db)
    return extraction.checks


# ── Export ────────────────────────────────────────────────────────────────────

@router.get(
    "/{document_id}/export.json",
    summary="Exporter en JSON",
    description="Exporte un document et ses extractions au format JSON.",
)
async def export_document_json(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id)
        .options(
            selectinload(Document.extractions).selectinload(Extraction.fields),
            selectinload(Document.extractions).selectinload(Extraction.checks),
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} introuvable.",
        )

    content = export_json(document)
    filename = document.filename.rsplit(".", 1)[0] + ".json"
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{document_id}/export.csv",
    summary="Exporter en CSV",
    description="Exporte les données extraites d'un document au format CSV.",
)
async def export_document_csv(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id)
        .options(
            selectinload(Document.extractions).selectinload(Extraction.fields),
            selectinload(Document.extractions).selectinload(Extraction.checks),
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} introuvable.",
        )

    content = export_csv(document)
    filename = document.filename.rsplit(".", 1)[0] + ".csv"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )