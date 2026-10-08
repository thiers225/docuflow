"""Script de test rapide de l'extracteur par règles."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps/backend/src"))

from docuflow.extractors.rules import RulesExtractor

def test(pdf_path: str) -> None:
    extractor = RulesExtractor()
    result = extractor.extract(pdf_path)

    print(f"\n{'='*50}")
    print(f"Fichier : {Path(pdf_path).name}")
    print('='*50)
    print(f"  Numéro facture : {result.invoice_number}")
    print(f"  Date facture   : {result.invoice_date}")
    print(f"  Échéance       : {result.due_date}")
    print(f"  Fournisseur    : {result.supplier}")
    print(f"  Client         : {result.client}")
    print(f"  Total HT       : {result.total_ht}")
    print(f"  TVA            : {result.tax_amount}")
    print(f"  Total TTC      : {result.total_ttc}")
    print(f"  Devise         : {result.currency}")

invoices_dir = Path(__file__).parent / "invoices"
for pdf in sorted(invoices_dir.glob("*.pdf")):
    test(str(pdf))
