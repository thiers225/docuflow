import re
from pathlib import Path

import pymupdf  # PyMuPDF (fitz)

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
        text = self._extract_text(file_path)

        result = ExtractionResult(
            engine=self.engine_name,
            engine_version=self.engine_version,
        )

        result.invoice_number = self._find_invoice_number(text)
        result.invoice_date = self._find_invoice_date(text)
        result.due_date = self._find_due_date(text)
        result.supplier = self._find_supplier(text)
        result.client = self._find_client(text)
        result.total_ht = self._find_total_ht(text)
        result.tax_amount = self._find_tax_amount(text)
        result.total_ttc = self._find_total_ttc(text)
        result.currency = self._find_currency(text)

        # Enregistrer la provenance champ par champ
        for field_name, value in [
            ("invoice_number", result.invoice_number),
            ("invoice_date", result.invoice_date),
            ("due_date", result.due_date),
            ("supplier", result.supplier),
            ("client", result.client),
            ("total_ht", result.total_ht),
            ("tax_amount", result.tax_amount),
            ("total_ttc", result.total_ttc),
            ("currency", result.currency),
        ]:
            result.fields.append(
                FieldResult(
                    field_name=field_name,
                    raw_value=value,
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

        doc = pymupdf.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    def _find_invoice_number(self, text: str) -> str | None:
        """
        Formats observés :
          N° CIE-2026-08741
          N° OCl-2026-004412
        """
        patterns = [
            r"N°\s+([A-Z][A-Za-z0-9\-]+)",
            r"facture\s*n[°o]?\s*[:\s]+([A-Z0-9\-]+)",
            r"invoice\s*[:#]?\s*([A-Z0-9\-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Ignorer les faux positifs trop courts
                if len(value) >= 4:
                    return value
        return None

    def _find_invoice_date(self, text: str) -> str | None:
        """
        Format observé : Date : 01/10/2026
        """
        match = re.search(
            r"Date\s*:\s*(\d{2}[/\-]\d{2}[/\-]\d{4})",
            text,
            re.IGNORECASE,
        )
        return match.group(1).strip() if match else None

    def _find_due_date(self, text: str) -> str | None:
        """
        Format observé : Échéance : 31/10/2026
        """
        match = re.search(
            r"[EÉeé]ch[eé]ance\s*:\s*(\d{2}[/\-]\d{2}[/\-]\d{4})",
            text,
        )
        return match.group(1).strip() if match else None

    def _find_supplier(self, text: str) -> str | None:
        """
        Le fournisseur est la première ligne non vide du document.
        On prend les lignes avant 'FACTURE' ou 'Avenue' ou 'RCCM'.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        # Chercher les lignes avant les infos d'adresse
        supplier_lines = []
        for line in lines[:6]:
            if re.match(r"(Avenue|Rue|Boulevard|RCCM|Tél|N°|FACTURE)", line, re.IGNORECASE):
                break
            supplier_lines.append(line)
        if supplier_lines:
            return " ".join(supplier_lines)
        return None

    def _find_client(self, text: str) -> str | None:
        """
        Format observé :
          FACTURER À
          BRASSERIES IVOIRIENNES RÉUNIES SARL
        """
        match = re.search(
            r"FACTURER\s*[AÀ]\s*\n([^\n]+)",
            text,
            re.IGNORECASE,
        )
        return match.group(1).strip() if match else None

    def _find_total_ht(self, text: str) -> str | None:
        """
        Format observé : Total HT\n3,215,000 FCFA
        ou sur la même ligne : Total HT  3,215,000 FCFA
        """
        match = re.search(
            r"Total\s+HT[\s\n]+([\d,\s\.]+)\s*(?:FCFA|CFA|EUR|USD|XOF)?",
            text,
            re.IGNORECASE,
        )
        return self._clean_amount(match.group(1)) if match else None

    def _find_tax_amount(self, text: str) -> str | None:
        """
        Format observé : TVA 18 %\n578,700 FCFA
        """
        match = re.search(
            r"TVA\s+[\d,\.]+\s*%[\s\n]+([\d,\s\.]+)\s*(?:FCFA|CFA|EUR|USD|XOF)?",
            text,
            re.IGNORECASE,
        )
        return self._clean_amount(match.group(1)) if match else None

    def _find_total_ttc(self, text: str) -> str | None:
        """
        Format observé : Total TTC\n3,793,700 FCFA
        """
        match = re.search(
            r"Total\s+TTC[\s\n]+([\d,\s\.]+)\s*(?:FCFA|CFA|EUR|USD|XOF)?",
            text,
            re.IGNORECASE,
        )
        return self._clean_amount(match.group(1)) if match else None

    def _find_currency(self, text: str) -> str | None:
        """Cherche la devise dans le texte."""
        for currency in ["FCFA", "XOF", "CFA", "EUR", "USD"]:
            if currency in text.upper():
                return currency
        return None

    def _clean_amount(self, value: str) -> str | None:
        """Nettoie un montant : supprime espaces et virgules de séparation."""
        if not value:
            return None
        # Supprimer les virgules et espaces utilisés comme séparateurs de milliers
        cleaned = value.strip().replace(",", "").replace(" ", "")
        return cleaned if cleaned else None
