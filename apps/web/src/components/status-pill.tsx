import { Loader2 } from "lucide-react";
import type { DocumentStatus } from "@/lib/api";

const STATUS: Record<DocumentStatus, { label: string; color: string; dot: string }> = {
  pending:    { label: "En attente",  color: "text-amber-600 bg-amber-50",  dot: "bg-amber-400" },
  processing: { label: "En cours",    color: "text-blue-600 bg-blue-50",    dot: "bg-blue-400"  },
  done:       { label: "Traité",      color: "text-green-700 bg-green-50",  dot: "bg-green-500" },
  error:      { label: "Erreur",      color: "text-red-600 bg-red-50",      dot: "bg-red-400"   },
};

export function StatusPill({ status }: { status: DocumentStatus }) {
  const s = STATUS[status];
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${s.color}`}>
      {status === "processing" ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : (
        <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${s.dot}`} />
      )}
      {s.label}
    </span>
  );
}
