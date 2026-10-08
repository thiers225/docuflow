import shutil
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from docuflow.core.config import settings
from docuflow.db.models import Document, DocumentStatus

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


async def save_document(file: UploadFile, db: AsyncSession) -> Document:
    """Sauvegarde le fichier uploadé et crée l'entrée en base."""

    # Vérifier l'extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Format non supporté : {suffix}. "
            f"Formats acceptés : {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Créer le dossier de stockage si nécessaire
    storage_path = Path(settings.storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)

    # Construire un nom de fichier unique pour éviter les collisions
    destination = storage_path / file.filename

    # Sauvegarder le fichier sur le disque
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Créer l'entrée en base
    document = Document(
        filename=file.filename,
        original_path=str(destination),
        status=DocumentStatus.pending,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document
