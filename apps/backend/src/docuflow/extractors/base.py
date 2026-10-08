from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class FieldResult:
    """Résultat d'extraction pour un champ."""
    field_name: str
    raw_value: str | None
    source: str = "extracted"  # extracted | deduced
    page: int | None = None
    location: str | None = None


@dataclass
class ExtractionResult:
    """Résultat complet d'une extraction."""
    engine: str
    engine_version: str | None = None
    prompt_config: str | None = None

    # Champs de la facture
    invoice_number: str | None = None
    invoice_date: str | None = None
    supplier: str | None = None
    client: str | None = None
    total_ht: str | None = None
    tax_amount: str | None = None
    total_ttc: str | None = None
    currency: str | None = None
    due_date: str | None = None

    # Détail champ par champ (provenance, localisation)
    fields: list[FieldResult] = field(default_factory=list)


class BaseExtractor(ABC):
    """Interface commune pour tous les moteurs d'extraction."""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Identifiant du moteur."""
        ...

    @property
    @abstractmethod
    def engine_version(self) -> str:
        """Version du moteur."""
        ...

    @abstractmethod
    def extract(self, file_path: str) -> ExtractionResult:
        """Extrait les champs d'un document.

        Args:
            file_path: Chemin absolu vers le fichier (PDF ou image).

        Returns:
            ExtractionResult avec les champs extraits.
        """
        ...
