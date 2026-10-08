"use client";

import { useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

const ACCEPTED = ".pdf,.jpg,.jpeg,.png";

export function ImportTrigger({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { mutate, isPending } = useMutation({
    mutationFn: (file: File) => api.importDocument(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setError(null);
    },
    onError: (err: unknown) => {
      setError(err instanceof Error ? err.message : "Erreur lors de l'import");
    },
  });

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    mutate(file);
    e.target.value = "";
  }

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={() => inputRef.current?.click()}
        disabled={isPending}
        className={className}
      >
        {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
        {children ?? (isPending ? "Import…" : "Importer un document")}
      </button>
      {error && <p className="text-xs text-red-600">{error}</p>}
      <input ref={inputRef} type="file" accept={ACCEPTED} className="hidden" onChange={handleFileChange} />
    </div>
  );
}

export function ImportButton() {
  const inputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { mutate, isPending } = useMutation({
    mutationFn: (file: File) => api.importDocument(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setError(null);
    },
    onError: (err: unknown) => {
      setError(err instanceof Error ? err.message : "Erreur lors de l'import");
    },
  });

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    mutate(file);
    e.target.value = "";
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        onClick={() => inputRef.current?.click()}
        disabled={isPending}
        className="flex items-center gap-2 px-4 py-2 bg-[#e8473f] hover:bg-[#d13f38] disabled:opacity-60 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm"
      >
        {isPending ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Upload className="h-4 w-4" />
        )}
        {isPending ? "Import…" : "Importer"}
      </button>
      {error && (
        <p className="text-xs text-red-600 max-w-xs text-right">{error}</p>
      )}
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        className="hidden"
        onChange={handleFileChange}
      />
    </div>
  );
}
