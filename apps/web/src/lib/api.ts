/**
 * Client API DocuFlow — fonctions de communication avec le backend FastAPI.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

// ── Types ─────────────────────────────────────────────────────────────────────

export type DocumentStatus = "pending" | "processing" | "done" | "error";
export type FieldSource = "extracted" | "deduced" | "corrected";
export type CheckSeverity = "error" | "warning";

export interface Document {
  id: number;
  filename: string;
  status: DocumentStatus;
  created_at: string;
}

export interface ExtractionField {
  id: number;
  field_name: string;
  raw_value: string | null;
  corrected_value: string | null;
  source: FieldSource;
  page: number | null;
  location: string | null;
}

export interface ExtractionCheck {
  id: number;
  rule: string;
  passed: boolean;
  severity: CheckSeverity;
  message: string;
}

export interface Extraction {
  id: number;
  document_id: number;
  engine: string;
  engine_version: string | null;
  prompt_config: string | null;
  invoice_number: string | null;
  invoice_date: string | null;
  supplier: string | null;
  client: string | null;
  total_ht: string | null;
  tax_amount: string | null;
  total_ttc: string | null;
  currency: string | null;
  due_date: string | null;
  created_at: string;
  fields: ExtractionField[];
  checks: ExtractionCheck[];
}

export interface DocumentDetail extends Document {
  original_path: string;
  extractions: Extraction[];
}

// ── Helpers ───────────────────────────────────────────────────────────────────

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "Erreur API");
  }
  if (res.status === 204 || res.headers.get("content-length") === "0") {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

// ── Documents ─────────────────────────────────────────────────────────────────

export const api = {
  /** Retourne la liste de tous les documents. */
  listDocuments(): Promise<Document[]> {
    return request<Document[]>("/documents/");
  },

  /** Retourne un document avec ses extractions et ses champs. */
  getDocument(id: number): Promise<DocumentDetail> {
    return request<DocumentDetail>(`/documents/${id}`);
  },

  /** Uploade un fichier PDF ou image et crée un document. */
  async importDocument(file: File): Promise<Document> {
    const form = new FormData();
    form.append("file", file);
    return request<Document>("/documents/", { method: "POST", body: form });
  },

  /** Déclenche l'extraction des champs d'un document. */
  extractDocument(id: number): Promise<Extraction> {
    return request<Extraction>(`/documents/${id}/extract`, { method: "POST" });
  },

  /** Corrige la valeur d'un champ extrait. */
  correctField(
    documentId: number,
    extractionId: number,
    fieldId: number,
    correctedValue: string | null
  ): Promise<ExtractionField> {
    return request<ExtractionField>(
      `/documents/${documentId}/extractions/${extractionId}/fields/${fieldId}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ corrected_value: correctedValue }),
      }
    );
  },

  /** Supprime un document et ses extractions. */
  deleteDocument(id: number): Promise<void> {
    return request<void>(`/documents/${id}`, { method: "DELETE" });
  },

  /** URL de téléchargement JSON. */
  exportJsonUrl(documentId: number): string {
    return `${API_BASE}/documents/${documentId}/export.json`;
  },

  /** URL de téléchargement CSV. */
  exportCsvUrl(documentId: number): string {
    return `${API_BASE}/documents/${documentId}/export.csv`;
  },
};
