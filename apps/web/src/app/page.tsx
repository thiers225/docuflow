"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import {
  FileText, CheckCircle2, AlertCircle, Clock,
  Loader2, Trash2, ChevronLeft, ChevronRight,
  ArrowRight, Upload,
} from "lucide-react";
import { api, type Document } from "@/lib/api";
import { ImportButton } from "@/components/import-button";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 15;

// ── Statut ────────────────────────────────────────────────────────────────────

const STATUS: Record<Document["status"], { label: string; color: string; dot: string }> = {
  pending:    { label: "En attente",  color: "text-amber-600",  dot: "bg-amber-400" },
  processing: { label: "En cours",    color: "text-blue-600",   dot: "bg-blue-400"  },
  done:       { label: "Traité",      color: "text-green-700",  dot: "bg-green-500" },
  error:      { label: "Erreur",      color: "text-red-600",    dot: "bg-red-400"   },
};

function StatusPill({ status }: { status: Document["status"] }) {
  const s = STATUS[status];
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${s.color}`}>
      {status === "processing" ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : (
        <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      )}
      {s.label}
    </span>
  );
}

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  }).format(new Date(iso));
}

// ── Suppression ───────────────────────────────────────────────────────────────

function DeleteButton({ doc }: { doc: Document }) {
  const [confirm, setConfirm] = useState(false);
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: () => api.deleteDocument(doc.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setConfirm(false);
    },
  });

  if (confirm) {
    return (
      <div className="flex items-center gap-1">
        <button
          onClick={() => mutate()}
          disabled={isPending}
          className="text-xs text-red-600 font-medium hover:underline disabled:opacity-50"
        >
          {isPending ? "Suppression…" : "Confirmer"}
        </button>
        <span className="text-[#ccc]">·</span>
        <button
          onClick={() => setConfirm(false)}
          className="text-xs text-[#888] hover:underline"
        >
          Annuler
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={(e) => { e.preventDefault(); setConfirm(true); }}
      className="p-1.5 rounded text-[#bbb] hover:text-red-500 hover:bg-red-50 transition-colors"
      title="Supprimer"
    >
      <Trash2 className="h-3.5 w-3.5" />
    </button>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function HomePage() {
  const [page, setPage] = useState(1);

  const { data: documents, isPending, error } = useQuery({
    queryKey: ["documents"],
    queryFn: api.listDocuments,
  });

  const total = documents?.length ?? 0;
  const totalPages = Math.ceil(total / PAGE_SIZE);
  const paginated = documents?.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE) ?? [];

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 space-y-6">

      {/* En-tête */}
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1a1a1a] tracking-tight">Mes documents</h1>
          <p className="text-sm text-[#888] mt-0.5">
            {isPending ? "Chargement…" : total > 0
              ? `${total} document${total > 1 ? "s" : ""}`
              : "Importez une facture PDF pour commencer."}
          </p>
        </div>
        <ImportButton />
      </div>

      {/* Chargement */}
      {isPending && (
        <div className="flex items-center justify-center py-24 gap-2 text-[#888]">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="text-sm">Chargement…</span>
        </div>
      )}

      {/* Erreur */}
      {error && !isPending && (
        <div className="rounded-xl border border-red-100 bg-red-50 px-5 py-4 text-sm text-red-700">
          Impossible de contacter le serveur.{" "}
          <button onClick={() => window.location.reload()} className="underline font-medium">
            Réessayer
          </button>
        </div>
      )}

      {/* Vide */}
      {!isPending && !error && total === 0 && (
        <div className="rounded-2xl border-2 border-dashed border-[#e0e0e0] bg-white py-20 flex flex-col items-center gap-4 text-[#aaa]">
          <div className="w-14 h-14 rounded-2xl bg-[#f5f5f5] flex items-center justify-center">
            <FileText className="h-7 w-7" />
          </div>
          <div className="text-center">
            <p className="font-medium text-[#555]">Aucun document</p>
            <p className="text-sm mt-1">Importez une facture PDF pour en extraire les données.</p>
          </div>
          <label className="cursor-pointer">
            <span className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#e8473f] hover:bg-[#d13f38] text-white text-sm font-medium rounded-lg transition-colors">
              <Upload className="h-4 w-4" />
              Importer un document
            </span>
          </label>
        </div>
      )}

      {/* Tableau */}
      {paginated.length > 0 && (
        <div className="bg-white rounded-2xl border border-[#e5e5e5] overflow-hidden shadow-sm">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#f0f0f0] bg-[#fafafa]">
                <th className="text-left text-xs font-medium text-[#888] uppercase tracking-wide px-5 py-3 w-10"></th>
                <th className="text-left text-xs font-medium text-[#888] uppercase tracking-wide px-3 py-3">Fichier</th>
                <th className="text-left text-xs font-medium text-[#888] uppercase tracking-wide px-3 py-3 w-44">Importé le</th>
                <th className="text-left text-xs font-medium text-[#888] uppercase tracking-wide px-3 py-3 w-32">Statut</th>
                <th className="text-right text-xs font-medium text-[#888] uppercase tracking-wide px-5 py-3 w-24"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f5f5f5]">
              {paginated.map((doc) => (
                <tr key={doc.id} className="group hover:bg-[#fafafa] transition-colors">
                  <td className="px-5 py-3.5 text-[#ccc]">
                    <FileText className="h-4 w-4" />
                  </td>
                  <td className="px-3 py-3.5">
                    <Link href={`/documents/${doc.id}`} className="group/link flex items-center gap-1">
                      <span className="text-sm font-medium text-[#1a1a1a] group-hover/link:text-[#e8473f] transition-colors truncate max-w-sm">
                        {doc.filename}
                      </span>
                      <ArrowRight className="h-3.5 w-3.5 text-[#e8473f] opacity-0 group-hover/link:opacity-100 -translate-x-1 group-hover/link:translate-x-0 transition-all shrink-0" />
                    </Link>
                  </td>
                  <td className="px-3 py-3.5 text-sm text-[#888] whitespace-nowrap">
                    {formatDate(doc.created_at)}
                  </td>
                  <td className="px-3 py-3.5">
                    <StatusPill status={doc.status} />
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <DeleteButton doc={doc} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="border-t border-[#f0f0f0] px-5 py-3 flex items-center justify-between">
              <span className="text-xs text-[#888]">
                Page {page} sur {totalPages} — {total} documents
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="p-1.5 rounded text-[#888] hover:bg-[#f0f0f0] disabled:opacity-30 transition-colors"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="p-1.5 rounded text-[#888] hover:bg-[#f0f0f0] disabled:opacity-30 transition-colors"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
