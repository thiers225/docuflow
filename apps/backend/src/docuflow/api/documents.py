from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from docuflow.db.database import get_db
from docuflow.db.models import Document, Extraction, ExtractionCheck
from docuflow.extractors.rules import RulesExtractor
from docuflow.schemas.document import DocumentDetail, DocumentRead
from docuflow.schemas.extraction import ExtractionRead
from docuflow.services.document import save_document
from docuflow.services.extraction import run_extraction

router = APIRouter(prefix="/documents", tags=["documents"])


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
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} introuvable.",
        )

    try:
        extraction = await run_extraction(document, RulesExtractor(), db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'extraction : {str(e)}",
        )

    return extraction
