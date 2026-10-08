"use client";

import { useState, useRef, useEffect } from "react";
import dynamic from "next/dynamic";
import {
  ChevronLeft, ChevronRight, ZoomIn, ZoomOut,
  Maximize2, FileX, Loader2,
} from "lucide-react";

const PDFDocument = dynamic(
  () => import("react-pdf").then((m) => m.Document),
  { ssr: false }
);
const PDFPage = dynamic(
  () => import("react-pdf").then((m) => m.Page),
  { ssr: false }
);

if (typeof window !== "undefined") {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { pdfjs } = require("react-pdf");
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url
  ).toString();
}

const API = process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") ?? "http://127.0.0.1:8000";

interface PdfViewerProps {
  filename: string;
}

export function PdfViewer({ filename }: PdfViewerProps) {
  const [numPages, setNumPages] = useState(0);
  const [page, setPage] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [loadError, setLoadError] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(600);

  const fileUrl = `${API}/files/${encodeURIComponent(filename)}`;

  useEffect(() => {
    if (!containerRef.current) return;
    const ro = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect.width;
      if (w) setContainerWidth(w);
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  const pageWidth = Math.floor((containerWidth - 48) * scale);

  if (loadError) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-3 bg-[#f5f5f5] text-[#aaa]">
        <FileX className="h-10 w-10" />
        <p className="text-sm font-medium text-[#666]">Aperçu indisponible</p>
        <p className="text-xs">Le fichier ne peut pas être affiché.</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-[#e8e8e8]">
      {/* Toolbar */}
      <div className="h-10 bg-[#f0f0f0] border-b border-[#d8d8d8] flex items-center px-3 gap-2 shrink-0">
        {/* Navigation */}
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1}
          className="p-1 rounded text-[#555] hover:bg-[#e0e0e0] disabled:opacity-30 transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <span className="text-xs text-[#555] tabular-nums">
          {numPages > 0 ? `${page} / ${numPages}` : "—"}
        </span>
        <button
          onClick={() => setPage((p) => Math.min(numPages, p + 1))}
          disabled={page >= numPages || numPages === 0}
          className="p-1 rounded text-[#555] hover:bg-[#e0e0e0] disabled:opacity-30 transition-colors"
        >
          <ChevronRight className="h-4 w-4" />
        </button>

        <div className="w-px h-4 bg-[#d0d0d0] mx-1" />

        {/* Zoom */}
        <button
          onClick={() => setScale((s) => Math.max(0.5, +(s - 0.2).toFixed(1)))}
          disabled={scale <= 0.5}
          className="p-1 rounded text-[#555] hover:bg-[#e0e0e0] disabled:opacity-30 transition-colors"
        >
          <ZoomOut className="h-4 w-4" />
        </button>
        <span className="text-xs text-[#555] tabular-nums w-10 text-center">
          {Math.round(scale * 100)}%
        </span>
        <button
          onClick={() => setScale((s) => Math.min(3, +(s + 0.2).toFixed(1)))}
          disabled={scale >= 3}
          className="p-1 rounded text-[#555] hover:bg-[#e0e0e0] disabled:opacity-30 transition-colors"
        >
          <ZoomIn className="h-4 w-4" />
        </button>
        <button
          onClick={() => setScale(1.0)}
          title="Ajuster à la largeur"
          className="p-1 rounded text-[#555] hover:bg-[#e0e0e0] transition-colors"
        >
          <Maximize2 className="h-4 w-4" />
        </button>
      </div>

      {/* PDF */}
      <div ref={containerRef} className="flex-1 overflow-auto flex justify-center py-6 px-6">
        <PDFDocument
          file={fileUrl}
          onLoadSuccess={({ numPages }) => { setNumPages(numPages); setPage(1); }}
          onLoadError={() => setLoadError(true)}
          loading={
            <div className="flex items-center gap-2 text-[#888] mt-10">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span className="text-sm">Chargement du document…</span>
            </div>
          }
        >
          <PDFPage
            pageNumber={page}
            width={pageWidth}
            className="shadow-xl"
            renderTextLayer
            renderAnnotationLayer
          />
        </PDFDocument>
      </div>
    </div>
  );
}
