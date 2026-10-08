"""Script de génération de factures fictives pour les tests DocuFlow."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
)

OUTPUT_DIR = Path(__file__).parent / "invoices"
OUTPUT_DIR.mkdir(exist_ok=True)

# Couleurs
DARK = colors.HexColor("#1A252F")
ACCENT = colors.HexColor("#E67E22")
LIGHT_GRAY = colors.HexColor("#F4F6F7")
MID_GRAY = colors.HexColor("#BDC3C7")
WHITE = colors.white


def build_invoice(filename: str, data: dict) -> None:
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    s_supplier_name = ParagraphStyle(
        "supplier_name",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=DARK,
        spaceAfter=2,
        leading=16,
    )
    s_supplier_info = ParagraphStyle(
        "supplier_info",
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
    )
    s_invoice_title = ParagraphStyle(
        "invoice_title",
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=ACCENT,
        spaceAfter=4,
    )
    s_label = ParagraphStyle(
        "label",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.HexColor("#7F8C8D"),
        spaceAfter=2,
    )
    s_value = ParagraphStyle(
        "value",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK,
        spaceAfter=2,
    )
    s_value_bold = ParagraphStyle(
        "value_bold",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=DARK,
        spaceAfter=2,
    )

    story = []

    # ── Bandeau en-tête : fournisseur + titre facture côte à côte ────────────
    header_data = [
        [
            Paragraph(data["supplier"], s_supplier_name),
            Paragraph(data["invoice_label"], s_invoice_title),
        ],
        [
            Paragraph(data["supplier_address"], s_supplier_info),
            Paragraph(f"N° {data['invoice_number']}" if data["invoice_number"] else "N° —", s_value_bold),
        ],
        [
            Paragraph(f"RCCM : {data['supplier_rccm']}", s_supplier_info),
            Paragraph(f"Date : {data['invoice_date']}", s_value),
        ],
        [
            Paragraph(f"Tél : {data['supplier_phone']}", s_supplier_info),
            Paragraph(f"Échéance : {data['due_date'] if data.get('due_date') else 'Non précisée'}", s_value),
        ],
    ]
    header_table = Table(header_data, colWidths=[9.5 * cm, 7.5 * cm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("WORDWRAP", (0, 0), (-1, -1), True),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    story.append(Spacer(1, 0.5 * cm))

    # ── Bloc client ──────────────────────────────────────────────────────────
    client_data = [
        [Paragraph("FACTURER À", s_label)],
        [Paragraph(data["client"], s_value_bold)],
        [Paragraph(data["client_address"], s_value)],
        [Paragraph(f"Tél : {data['client_phone']}", s_value)],
    ]
    client_table = Table(client_data, colWidths=[17 * cm])
    client_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.8 * cm))

    # ── Tableau des lignes ───────────────────────────────────────────────────
    col_headers = ["Description", "Qté", "Prix unitaire (FCFA)", "Montant (FCFA)"]
    table_data = [col_headers]
    for line in data["lines"]:
        table_data.append([
            line["description"],
            str(line["qty"]),
            f"{line['unit_price']:,.0f}",
            f"{line['amount']:,.0f}",
        ])

    lines_table = Table(
        table_data,
        colWidths=[8.5 * cm, 1.5 * cm, 3.5 * cm, 3.5 * cm],
    )
    lines_table.setStyle(TableStyle([
        # En-tête
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        # Corps
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
        # Alignement
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        # Bordures
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, MID_GRAY),
    ]))
    story.append(lines_table)
    story.append(Spacer(1, 0.8 * cm))

    # ── Bloc totaux ──────────────────────────────────────────────────────────
    totals_data = [
        ["Total HT", f"{data['total_ht']:,.0f} FCFA"],
        [f"TVA {data['tax_rate']} %", f"{data['tax_amount']:,.0f} FCFA"],
        ["Total TTC", f"{data['total_ttc']:,.0f} FCFA"],
    ]
    totals_table = Table(totals_data, colWidths=[11 * cm, 6 * cm])
    totals_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEABOVE", (0, 2), (-1, 2), 1.5, ACCENT),
        ("BACKGROUND", (0, 2), (-1, 2), LIGHT_GRAY),
        ("TEXTCOLOR", (0, 2), (-1, 2), DARK),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 1 * cm))

    # ── Pied de page ─────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 0.3 * cm))
    footer_note = data.get("note", "Merci de votre confiance.")
    story.append(Paragraph(footer_note, s_supplier_info))

    doc.build(story)
    print(f"✓  {path.name}")


# ── Facture 1 : Cohérente ─────────────────────────────────────────────────────
build_invoice("facture_001_cie.pdf", {
    "supplier": "CIE — COMPAGNIE IVOIRIENNE D'ÉLECTRICITÉ",
    "supplier_address": "Avenue Christiani, Plateau, Abidjan, Côte d'Ivoire",
    "supplier_rccm": "CI-ABJ-2001-B-12345",
    "supplier_phone": "+225 27 20 23 30 00",
    "invoice_label": "FACTURE",
    "invoice_number": "CIE-2026-08741",
    "invoice_date": "01/10/2026",
    "due_date": "31/10/2026",
    "client": "BRASSERIES IVOIRIENNES RÉUNIES SARL",
    "client_address": "Zone Industrielle de Yopougon, Abidjan",
    "client_phone": "+225 27 23 45 67 89",
    "lines": [
        {"description": "Fourniture électricité — septembre 2026 (HTA)", "qty": 1, "unit_price": 2850000, "amount": 2850000},
        {"description": "Frais de puissance souscrite (500 kVA)", "qty": 1, "unit_price": 320000, "amount": 320000},
        {"description": "Location compteur industriel", "qty": 1, "unit_price": 45000, "amount": 45000},
    ],
    "total_ht": 3215000,
    "tax_amount": 578700,
    "tax_rate": "18",
    "total_ttc": 3793700,
    "note": "Règlement par virement bancaire — IBAN CI 93 0100 1234 5678 9012 3456 — Réf : CIE-2026-08741",
})

# ── Facture 2 : Incohérence montants ─────────────────────────────────────────
build_invoice("facture_002_orange_ci.pdf", {
    "supplier": "ORANGE CÔTE D'IVOIRE SA",
    "supplier_address": "Immeuble ORANGE, Rue du Commerce, Plateau, Abidjan",
    "supplier_rccm": "CI-ABJ-1996-B-00456",
    "supplier_phone": "+225 27 20 25 00 00",
    "invoice_label": "FACTURE",
    "invoice_number": "OCl-2026-004412",
    "invoice_date": "15/09/2026",
    "due_date": "15/10/2026",
    "client": "CABINET KOUASSI & PARTENAIRES",
    "client_address": "Cocody Riviera 2, Rue des Jardins, Abidjan",
    "client_phone": "+225 07 08 09 10 11",
    "lines": [
        {"description": "Abonnement fibre optique Pro 200 Mbps — sept. 2026", "qty": 1, "unit_price": 185000, "amount": 185000},
        {"description": "Lignes mobiles entreprise (x5)", "qty": 5, "unit_price": 18000, "amount": 90000},
        {"description": "Frais d'installation routeur pro", "qty": 1, "unit_price": 35000, "amount": 35000},
    ],
    "total_ht": 310000,
    "tax_amount": 55800,
    "tax_rate": "18",
    "total_ttc": 380000,  # Incohérent : devrait être 365800
    "note": "En cas de litige, contacter votre gestionnaire de compte Orange Business.",
})

# ── Facture 3 : Numéro absent ─────────────────────────────────────────────────
build_invoice("facture_003_saf_logistics.pdf", {
    "supplier": "SAF LOGISTICS CÔTE D'IVOIRE",
    "supplier_address": "Port d'Abidjan, Zone Portuaire, Treichville, Abidjan",
    "supplier_rccm": "CI-ABJ-2012-B-07890",
    "supplier_phone": "+225 27 21 30 40 50",
    "invoice_label": "FACTURE",
    "invoice_number": "",  # Absent intentionnellement
    "invoice_date": "20/09/2026",
    "due_date": None,
    "client": "NESTLÉ CÔTE D'IVOIRE SA",
    "client_address": "Boulevard de Marseille, Zone Industrielle, Abidjan",
    "client_phone": "+225 27 20 30 40 50",
    "lines": [
        {"description": "Transport maritime conteneur 40' — Abidjan / Dakar", "qty": 2, "unit_price": 1250000, "amount": 2500000},
        {"description": "Frais de manutention et levage", "qty": 1, "unit_price": 180000, "amount": 180000},
        {"description": "Assurance marchandises tous risques", "qty": 1, "unit_price": 95000, "amount": 95000},
    ],
    "total_ht": 2775000,
    "tax_amount": 499500,
    "tax_rate": "18",
    "total_ttc": 3274500,
    "note": "Documents douaniers et connaissement disponibles sur demande.",
})

print("\nFactures générées dans examples/invoices/")
