"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2, XCircle, AlertTriangle,
  Loader2, Zap, RotateCcw, Check, X,
} from "lucide-react";
import { api, type DocumentDetail, type Extraction, type ExtractionField } from "@/lib/api";

// ── Sections de champs ────────────────────────────────────────────────────────

const SECTIONS: { title: string; fields: string[] }[] = [
  { title: "Identification", fields: ["invoice_number", "invoice_date", "due_date"] },
  { title: "Parties", fields: ["supplier", "client"] },
  { title: "Montants", fields: ["total_ht", "tax_amount", "total_ttc", "currency"] },
];

const FIELD_LABELS: Record<string, string> = {
  invoice_number: "Numéro de facture",
  invoice_date:   "Date de facture",
  due_date:       "Échéance",
  supplier:       "Fournisseur",
  client:         "Client",
  total_ht:       "Total HT",
  tax_amount:     "TVA",
  total_ttc:      "Total TTC",
  currency:       "Devise",
};

// ── Ligne de champ éditable ───────────────────────────────────────────────────

function FieldRow({
  field,
  documentId,
  extractionId,
}: {
  field: ExtractionField;
  documentId: number;
  extractionId: number;
}) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(field.corrected_value ?? field.raw_value ?? "");
  const [saved, setSaved] = useState(false);
  const queryClient = useQueryClient();

  const { mutate, isPending, error } = useMutation({
    mutationFn: (v: string | null) =>
      api.correctField(documentId, extractionId, field.id, v),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["document", documentId] });
      setEditing(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  const displayValue = field.corrected_value ?? field.raw_value;
  const isCorrected = field.source === "corrected";
  const label = FIELD_LABELS[field.field_name] ?? field.field_name;

  return (
    <div className="py-2.5">
      <div className="flex items-baseline justify-between gap-2 mb-0.5">
        <span className="text-xs text-[#999]">{label}</span>
        {isCorrected && (
          <span className="text-[10px] text-blue-500 font-medium">Modifié</span>
        )}
        {saved && (
          <span className="text-[10px] text-green-600 font-medium flex items-center gap-0.5">
            <Check className="h-3 w-3" /> Enregistré
          </span>
        )}
      </div>

      {editing ? (
        <div className="space-y-1.5">
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            autoFocus
            onKeyDown={(e) => {
              if (e.key === "Enter") mutate(value || null);
              if (e.key === "Escape") { setEditing(false); setValue(field.corrected_value ?? field.raw_value ?? ""); }
            }}
            className="w-full text-sm px-3 py-1.5 border border-[#d0d0d0] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#e8473f]/30 focus:border-[#e8473f] bg-white"
          />
          {error && (
            <p className="text-xs text-red-600">{(error as Error).message}</p>
          )}
          <div className="flex items-center gap-2">
            <button
              onClick={() => mutate(value || null)}
              disabled={isPending}
              className="flex items-center gap-1 text-xs font-medium text-white bg-[#1a1a1a] hover:bg-[#333] px-3 py-1.5 rounded-lg disabled:opacity-50 transition-colors"
            >
              {isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Check className="h-3 w-3" />}
              Enregistrer
            </button>
            <button
              onClick={() => { setEditing(false); setValue(field.corrected_value ?? field.raw_value ?? ""); }}
              className="flex items-center gap-1 text-xs text-[#666] hover:text-[#333] px-3 py-1.5 rounded-lg hover:bg-[#f0f0f0] transition-colors"
            >
              <X className="h-3 w-3" />
              Annuler
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between group/field">
          <span className={`text-sm ${displayValue ? "text-[#1a1a1a] font-medium" : "text-[#bbb] italic"}`}>
            {displayValue ?? "Non renseigné"}
          </span>
          <button
            onClick={() => { setValue(displayValue ?? ""); setEditing(true); }}
            className="text-xs text-[#999] hover:text-[#e8473f] opacity-0 group-hover/field:opacity-100 transition-all px-2 py-0.5 rounded hover:bg-[#fff5f5]"
          >
            Modifier
          </button>
        </div>
      )}

      {isCorrected && field.raw_value && field.raw_value !== field.corrected_value && (
        <p className="text-[11px] text-[#bbb] mt-0.5">
          Valeur initiale : {field.raw_value}
        </p>
      )}
    </div>
  );
}

// ── Panneau principal ─────────────────────────────────────────────────────────

interface ExtractionPanelProps {
  document: DocumentDetail;
  extraction: Extraction | null;
  onExtract: () => void;
  isExtracting: boolean;
}

export function ExtractionPanel({
  document,
  extraction,
  onExtract,
  isExtracting,
}: ExtractionPanelProps) {
  // ── État : en cours d'extraction ────────────────────────────────────────────
  if (isExtracting) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-4 bg-white px-8">
        <div className="w-12 h-12 rounded-full bg-[#fff5f5] flex items-center justify-center">
          <Loader2 className="h-6 w-6 text-[#e8473f] animate-spin" />
        </div>
        <div className="text-center">
          <p className="font-medium text-[#1a1a1a]">Extraction en cours</p>
          <p className="text-sm text-[#888] mt-1">
            Analyse du document et extraction des données…
          </p>
        </div>
      </div>
    );
  }

  // ── État : pas encore d'extraction ──────────────────────────────────────────
  if (!extraction) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-5 bg-white px-8">
        <div className="w-14 h-14 rounded-2xl bg-[#fff5f5] flex items-center justify-center">
          <Zap className="h-7 w-7 text-[#e8473f]" />
        </div>
        <div className="text-center max-w-xs">
          <p className="font-semibold text-[#1a1a1a] text-lg">Prêt à extraire les données</p>
          <p className="text-sm text-[#888] mt-2 leading-relaxed">
            Les champs de la facture seront extraits et présentés ici pour vérification et correction.
          </p>
        </div>
        <button
          onClick={onExtract}
          className="flex items-center gap-2 px-6 py-3 bg-[#e8473f] hover:bg-[#d13f38] text-white text-sm font-semibold rounded-xl transition-colors shadow-sm"
        >
          <Zap className="h-4 w-4" />
          Extraire les données
        </button>
      </div>
    );
  }

  // ── État : extraction disponible ─────────────────────────────────────────────

  const errors   = extraction.checks.filter((c) => !c.passed && c.severity === "error");
  const warnings = extraction.checks.filter((c) => !c.passed && c.severity === "warning");

  // Construire une map field_name → field pour lookup rapide
  const fieldMap = Object.fromEntries(extraction.fields.map((f) => [f.field_name, f]));

  return (
    <div className="h-full flex flex-col bg-white">
      {/* En-tête panneau */}
      <div className="px-5 py-3.5 border-b border-[#f0f0f0] flex items-center justify-between shrink-0">
        <span className="text-sm font-semibold text-[#1a1a1a]">Données extraites</span>
        <div className="flex items-center gap-2">
          {errors.length === 0 && warnings.length === 0 ? (
            <span className="flex items-center gap-1 text-xs text-green-700 bg-green-50 px-2.5 py-1 rounded-full font-medium">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Données conformes
            </span>
          ) : (
            <>
              {errors.length > 0 && (
                <span className="flex items-center gap-1 text-xs text-red-600 bg-red-50 px-2.5 py-1 rounded-full font-medium">
                  <XCircle className="h-3.5 w-3.5" />
                  {errors.length} anomalie{errors.length > 1 ? "s" : ""}
                </span>
              )}
              {warnings.length > 0 && (
                <span className="flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full font-medium">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  {warnings.length} avertissement{warnings.length > 1 ? "s" : ""}
                </span>
              )}
            </>
          )}
        </div>
      </div>

      {/* Corps scrollable */}
      <div className="flex-1 overflow-y-auto">

        {/* Sections de champs */}
        {SECTIONS.map((section) => {
          const sectionFields = section.fields
            .map((name) => fieldMap[name])
            .filter(Boolean) as ExtractionField[];

          if (sectionFields.length === 0) return null;

          return (
            <div key={section.title} className="px-5 pt-4 pb-2">
              <h3 className="text-[10px] font-semibold uppercase tracking-widest text-[#bbb] mb-1">
                {section.title}
              </h3>
              <div className="divide-y divide-[#f5f5f5]">
                {sectionFields.map((field) => (
                  <FieldRow
                    key={field.id}
                    field={field}
                    documentId={document.id}
                    extractionId={extraction.id}
                  />
                ))}
              </div>
            </div>
          );
        })}

        {/* Contrôles métier */}
        {extraction.checks.length > 0 && (
          <div className="px-5 pt-4 pb-5 border-t border-[#f5f5f5] mt-2">
            <h3 className="text-[10px] font-semibold uppercase tracking-widest text-[#bbb] mb-3">
              Contrôles
            </h3>
            <div className="space-y-2.5">
              {extraction.checks.map((check) => (
                <div key={check.rule} className="flex items-start gap-2.5">
                  {check.passed ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                  ) : check.severity === "error" ? (
                    <XCircle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
                  )}
                  <p className="text-xs text-[#555] leading-relaxed">{check.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Détails du traitement */}
        <div className="px-5 py-4 border-t border-[#f5f5f5]">
          <details className="group">
            <summary className="text-[11px] text-[#bbb] cursor-pointer hover:text-[#888] list-none flex items-center gap-1">
              <span className="group-open:hidden">▶</span>
              <span className="hidden group-open:inline">▼</span>
              Détails du traitement
            </summary>
            <div className="mt-2 space-y-1 text-[11px] text-[#999]">
              <p>Méthode : Extraction par règles</p>
              <p>Version : {extraction.engine_version ?? "—"}</p>
              <p>Extrait le : {new Date(extraction.created_at).toLocaleString("fr-FR")}</p>
            </div>
          </details>
        </div>
      </div>
    </div>
  );
}
