import re
from pathlib import Path

import fitz  # PyMuPDF

from docuflow.extractors.base import BaseExtractor, ExtractionResult, FieldResult


class RulesExtractor(BaseExtractor):
    """Extracteur classique par règles et regex."""

    @property
    def engine_name(self) -> str:
        return "rules"

    @property
    def engine_version(self) -> str:
        return "0.1.0"

    def extract(self, file_path: str) -> ExtractionResult:
        """Extrait le texte du PDF et applique des regex simples."""
        text = self._extract_text(file_path)

        result = ExtractionResult(
            engine=self.engine_name,
            engine_version=self.engine_version,
        )

        # Extraction par regex
        result.invoice_number = self._find_invoice_number(text)
        result.invoice_date = self._find_date(text, r"date[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})")
        result.supplier = self._find_supplier(text)
        result.client = self._find_client(text)
        result.total_ttc = self._find_amount(text, r"total\s*TTC[:\s]*([0-9\s,\.]+)")
        result.currency = self._find_currency(text)
        result.due_date = self._find_date(text, r"échéance[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})")

        # Construire les fields avec provenance
        if result.invoice_number:
            result.fields.append(
                FieldResult(
                    field_name="invoice_number",
                    raw_value=result.invoice_number,
                    source="extracted",
                    page=1,
                )
            )

        if result.total_ttc:
            result.fields.append(
                FieldResult(
                    field_name="total_ttc",
                    raw_value=result.total_ttc,
                    source="extracted",
                    page=1,
                )
            )

        return result

    def _extract_text(self, file_path: str) -> str:
        """Extrait le texte natif d'un PDF avec PyMuPDF."""
        suffix = Path(file_path).suffix.lower()
        if suffix != ".pdf":
            raise ValueError(f"RulesExtractor ne supporte que les PDF, reçu : {suffix}")

        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    def _find_invoice_number(self, text: str) -> str | None:
        """Cherche un numéro de facture."""
        patterns = [
            r"facture\s*n[°o]?\s*[:\s]*([A-Z0-9\-]+)",
            r"invoice\s*[:#]?\s*([A-Z0-9\-]+)",
            r"n[°o]\s*facture[:\s]*([A-Z0-9\-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _find_date(self, text: str, pattern: str) -> str | None:
        """Cherche une date selon un pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _find_supplier(self, text: str) -> str | None:
        """Cherche le nom du fournisseur (première ligne en majuscules)."""
        lines = text.split("\n")
        for line in lines[:10]:  # Chercher dans les 10 premières lignes
            line = line.strip()
            if len(line) > 5 and line.isupper():
                return line
        return None

    def _find_client(self, text: str) -> str | None:
        """Cherche le nom du client après 'Client' ou 'À'."""
        patterns = [
            r"client[:\s]*([^\n]+)",
            r"à[:\s]*([^\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _find_amount(self, text: str, pattern: str) -> str | None:
        """Cherche un montant selon un pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _find_currency(self, text: str) -> str | None:
        """Cherche la devise (FCFA, EUR, USD, etc.)."""
        currencies = ["FCFA", "CFA", "EUR", "USD", "XOF"]
        for currency in currencies:
            if currency in text.upper():
                return currency
        return None
