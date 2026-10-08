import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from docuflow.db.base import Base


class DocumentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"


class FieldSource(str, enum.Enum):
    extracted = "extracted"
    deduced = "deduced"
    corrected = "corrected"


class CheckSeverity(str, enum.Enum):
    error = "error"       # Incohérence bloquante
    warning = "warning"   # Anomalie non bloquante


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_path: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    extractions: Mapped[list["Extraction"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class Extraction(Base):
    __tablename__ = "extractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    engine: Mapped[str] = mapped_column(String(100), nullable=False)
    engine_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prompt_config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Identification
    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    invoice_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Montants
    total_ht: Mapped[str | None] = mapped_column(Numeric(15, 2), nullable=True)
    tax_amount: Mapped[str | None] = mapped_column(Numeric(15, 2), nullable=True)
    total_ttc: Mapped[str | None] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    document: Mapped["Document"] = relationship(back_populates="extractions")
    fields: Mapped[list["ExtractionField"]] = relationship(
        back_populates="extraction", cascade="all, delete-orphan"
    )
    checks: Mapped[list["ExtractionCheck"]] = relationship(
        back_populates="extraction", cascade="all, delete-orphan"
    )


class ExtractionField(Base):
    __tablename__ = "extraction_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    extraction_id: Mapped[int] = mapped_column(
        ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[FieldSource] = mapped_column(
        Enum(FieldSource), default=FieldSource.extracted, nullable=False
    )

    # Provenance dans le document
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)

    extraction: Mapped["Extraction"] = relationship(back_populates="fields")


class ExtractionCheck(Base):
    __tablename__ = "extraction_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    extraction_id: Mapped[int] = mapped_column(
        ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False
    )
    rule: Mapped[str] = mapped_column(String(100), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    severity: Mapped[CheckSeverity] = mapped_column(
        Enum(CheckSeverity), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)

    extraction: Mapped["Extraction"] = relationship(back_populates="checks")
