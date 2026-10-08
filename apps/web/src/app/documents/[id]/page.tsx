"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, RotateCcw, Download, ChevronDown } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { PdfViewer } from "@/components/pdf-viewer";
import { ExtractionPanel } from "@/components/extraction-panel";
import { StatusPill } from "@/components/status-pill";

export const dynamic = "force-dynamic";

export default function DocumentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const documentId = parseInt(id);
  const queryClient = useQueryClient();
  const [exportOpen, setExportOpen] = useState(false);

  const { data: document, isPending, error } = useQuery({
    queryKey: ["document", documentId],
    queryFn: () => api.getDocument(documentId),
  });

  const { mutate: extract, isPending: isExtracting } = useMutation({
    mutationFn: () => api.extractDocument(documentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["document", documentId] }),
  });

  const { mutate: reExtract, isPending: isReExtracting } = useMutation({
    mutationFn: () => api.extractDocument(documentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["document", documentId] }),
  });

  // ── Chargement ───────────────────────────────────────────────────────────────
  if (isPending) {
    return (
      <div className="flex items-center justify-center h-full text-[#888] gap-2">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="text-sm">Chargement…</span>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 text-[#888]">
        <p className="text-sm">Document introuvable.</p>
        <Link href="/" className="text-sm text-[#e8473f] hover:underline">
          ← Retour aux documents
        </Link>
      </div>
    );
  }

  const latestExtraction = document.extractions.at(-1);
  const hasExtraction = latestExtraction !== undefined;
  const shortName = document.filename.length > 45
    ? document.filename.slice(0, 42) + "…"
    : document.filename;

  return (
    <div className="flex flex-col h-full">

      {/* ── Barre supérieure ─────────────────────────────────────────────────── */}
      <div className="h-12 bg-white border-b border-[#e5e5e5] flex items-center px-4 gap-3 shrink-0">
        <Link
          href="/"
          className="flex items-center gap-1.5 text-sm text-[#666] hover:text-[#1a1a1a] transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span className="hidden sm:inline">Documents</span>
        </Link>

        <div className="w-px h-4 bg-[#e5e5e5]" />

        <span className="text-sm font-medium text-[#1a1a1a] truncate flex-1 min-w-0">
          {shortName}
        </span>

        <StatusPill status={document.status} />

        <div className="flex items-center gap-2 shrink-0 ml-2">
          {/* Relancer l'extraction */}
          {hasExtraction && (
            <button
              onClick={() => reExtract()}
              disabled={isReExtracting}
              title="Relancer l'extraction"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[#555] border border-[#e0e0e0] rounded-lg hover:bg-[#f5f5f5] disabled:opacity-50 transition-colors"
            >
              {isReExtracting ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <RotateCcw className="h-3.5 w-3.5" />
              )}
              <span className="hidden sm:inline">Relancer</span>
            </button>
          )}

          {/* Export */}
          {hasExtraction && (
            <div className="relative">
              <button
                onClick={() => setExportOpen((o) => !o)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[#555] border border-[#e0e0e0] rounded-lg hover:bg-[#f5f5f5] transition-colors"
              >
                <Download className="h-3.5 w-3.5" />
                Exporter
                <ChevronDown className="h-3 w-3" />
              </button>
              {exportOpen && (
                <div
                  className="absolute right-0 top-full mt-1 bg-white border border-[#e5e5e5] rounded-xl shadow-lg py-1 z-20 min-w-[130px]"
                  onMouseLeave={() => setExportOpen(false)}
                >
                  <a
                    href={api.exportJsonUrl(documentId)}
                    download
                    className="flex items-center gap-2 px-4 py-2 text-sm text-[#333] hover:bg-[#f5f5f5] transition-colors"
                    onClick={() => setExportOpen(false)}
                  >
                    <span className="font-mono text-xs bg-[#f0f0f0] px-1.5 py-0.5 rounded">JSON</span>
                    Exporter en JSON
                  </a>
                  <a
                    href={api.exportCsvUrl(documentId)}
                    download
                    className="flex items-center gap-2 px-4 py-2 text-sm text-[#333] hover:bg-[#f5f5f5] transition-colors"
                    onClick={() => setExportOpen(false)}
                  >
                    <span className="font-mono text-xs bg-[#f0f0f0] px-1.5 py-0.5 rounded">CSV</span>
                    Exporter en CSV
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── Espace de travail ─────────────────────────────────────────────────── */}
      {/* Desktop : deux panneaux côte à côte */}
      <div className="flex-1 min-h-0 hidden lg:grid lg:grid-cols-[55fr_45fr]">
        <div className="border-r border-[#e5e5e5] overflow-hidden">
          <PdfViewer filename={document.filename} />
        </div>
        <div className="overflow-hidden">
          <ExtractionPanel
            document={document}
            extraction={latestExtraction ?? null}
            onExtract={() => extract()}
            isExtracting={isExtracting}
          />
        </div>
      </div>

      {/* Mobile : onglets */}
      <MobileView
        document={document}
        extraction={latestExtraction ?? null}
        onExtract={() => extract()}
        isExtracting={isExtracting}
      />
    </div>
  );
}

// ── Vue mobile avec onglets ───────────────────────────────────────────────────

function MobileView({
  document,
  extraction,
  onExtract,
  isExtracting,
}: {
  document: import("@/lib/api").DocumentDetail;
  extraction: import("@/lib/api").Extraction | null;
  onExtract: () => void;
  isExtracting: boolean;
}) {
  const [tab, setTab] = useState<"doc" | "data">("doc");

  return (
    <div className="flex-1 min-h-0 flex flex-col lg:hidden">
      <div className="flex border-b border-[#e5e5e5] bg-white shrink-0">
        {(["doc", "data"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
              tab === t
                ? "text-[#e8473f] border-b-2 border-[#e8473f]"
                : "text-[#888] hover:text-[#555]"
            }`}
          >
            {t === "doc" ? "Document" : "Données"}
          </button>
        ))}
      </div>
      <div className="flex-1 min-h-0 overflow-hidden">
        {tab === "doc" ? (
          <PdfViewer filename={document.filename} />
        ) : (
          <ExtractionPanel
            document={document}
            extraction={extraction}
            onExtract={onExtract}
            isExtracting={isExtracting}
          />
        )}
      </div>
    </div>
  );
}
