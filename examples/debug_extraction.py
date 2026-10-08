"""Script de debug — affiche le texte brut extrait par PyMuPDF."""

import sys
from pathlib import Path

import fitz

def extract_text(pdf_path: str) -> None:
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        print(f"\n{'='*60}")
        print(f"PAGE {i + 1}")
        print('='*60)
        print(page.get_text())
    doc.close()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "examples/invoices/facture_001_cie.pdf"
    extract_text(path)
