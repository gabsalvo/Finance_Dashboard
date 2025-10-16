"use client";

import { useMemo, useState } from "react";
import { ArrowUpDown, ArrowDown, ArrowUp, Clock } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

type Invoice = {
  id: string;
  vendor: string;
  description?: string;
  due: string; // ISO date
  amount: number; // EUR
  selected: boolean; // ticked in the list
};

// ---- demo data (replace with your DTO wiring later) ------------------------
const initialInvoices: Invoice[] = [
  {
    id: "INV-2025-001",
    vendor: "ENEL Energia",
    description: "Luce – Marzo",
    due: "2025-10-20",
    amount: 120.45,
    selected: false,
  },
  {
    id: "INV-2025-002",
    vendor: "Vodafone",
    description: "Fibra – Ottobre",
    due: "2025-10-25",
    amount: 45.99,
    selected: false,
  },
  {
    id: "INV-2025-003",
    vendor: "Comune di Pisa",
    description: "TARI 2025 (2ª rata)",
    due: "2025-11-10",
    amount: 210.0,
    selected: false,
  },
  {
    id: "INV-2025-004",
    vendor: "AWS",
    description: "Cloud bill",
    due: "2025-10-18",
    amount: 32.8,
    selected: false,
  },
  {
    id: "INV-2025-005",
    vendor: "Supabase",
    description: "Pro plan",
    due: "2025-10-19",
    amount: 25.0,
    selected: false,
  },
    {
    id: "INV-2025-006",
    vendor: "Comune di Pisa",
    description: "TARI 2025 (2ª rata)",
    due: "2025-11-10",
    amount: 210.0,
    selected: false,
  },
  {
    id: "INV-2025-007",
    vendor: "AWS",
    description: "Cloud bill",
    due: "2025-10-18",
    amount: 32.8,
    selected: false,
  },
  {
    id: "INV-2025-008",
    vendor: "Supabase",
    description: "Pro plan",
    due: "2025-10-19",
    amount: 25.0,
    selected: false,
  },
    {
    id: "INV-2025-009",
    vendor: "Comune di Pisa",
    description: "TARI 2025 (2ª rata)",
    due: "2025-11-10",
    amount: 210.0,
    selected: false,
  },
  {
    id: "INV-2025-010",
    vendor: "AWS",
    description: "Cloud bill",
    due: "2025-10-18",
    amount: 32.8,
    selected: false,
  },
  {
    id: "INV-2025-011",
    vendor: "Supabase",
    description: "Pro plan",
    due: "2025-10-19",
    amount: 25.0,
    selected: false,
  },
];

const EUR = new Intl.NumberFormat("it-IT", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 2,
});

// --- small helpers ----------------------------------------------------------
const daysUntil = (isoDate: string) => {
  const today = new Date();
  const due = new Date(isoDate + "T00:00:00");
  const ms = due.setHours(0, 0, 0, 0) - today.setHours(0, 0, 0, 0);
  return Math.ceil(ms / (1000 * 60 * 60 * 24));
};

const statusBadge = (isoDate: string) => {
  const d = daysUntil(isoDate);
  if (d < 0) return <Badge variant="destructive">Scaduta</Badge>;
  if (d === 0) return <Badge className="bg-amber-500 hover:bg-amber-500">Oggi</Badge>;
  if (d <= 7) return <Badge>Tra {d} gg</Badge>;
  return <Badge variant="secondary">In tempo</Badge>;
};

// --- radial progress (empties to zero) --------------------------------------
function RadialProgress({
  value, // 0..100 (remaining %)
  size = 220,
  stroke = 18,
  ringClass = "text-rose-600",
}: {
  value: number;
  size?: number;
  stroke?: number;
  ringClass?: string;
}) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const clamped = Math.max(0, Math.min(100, value));
  const offset = c * (1 - clamped / 100);

  return (
    <div
      className="relative flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} className="block">
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          strokeWidth={stroke}
          className="text-muted-foreground/15"
          stroke="currentColor"
          fill="none"
        />
        {/* Progress */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          strokeWidth={stroke}
          className={ringClass}
          stroke="currentColor"
          fill="none"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 300ms ease" }}
        />
      </svg>
      {/* Center content injected by parent */}
      <div className="absolute inset-0 grid place-items-center pointer-events-none" />
    </div>
  );
}

// --- a single invoice row ----------------------------------------------------
function InvoiceRow({
  inv,
  onToggle,
}: {
  inv: Invoice;
  onToggle: (id: string, checked: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between rounded-xl border p-4 hover:bg-accent/40 transition">
      <div className="flex items-start gap-3">
        <Checkbox
          checked={inv.selected}
          onCheckedChange={(v) => onToggle(inv.id, Boolean(v))}
          className="mt-1"
        />
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <p className="font-medium">{inv.vendor}</p>
            {statusBadge(inv.due)}
          </div>
          <p className="text-sm text-muted-foreground">
            {inv.description ?? "—"} · Scadenza {new Date(inv.due).toLocaleDateString("it-IT")}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-semibold tabular-nums">{EUR.format(inv.amount)}</p>
        <p className="text-xs text-muted-foreground">{inv.id}</p>
      </div>
    </div>
  );
}

// --- page --------------------------------------------------------------------
export default function Page() {
  const [invoices, setInvoices] = useState<Invoice[]>(initialInvoices);
  const [query, setQuery] = useState("");

  const totals = useMemo(() => {
    const total = invoices.reduce((s, i) => s + i.amount, 0);
    const selected = invoices.filter((i) => i.selected).reduce((s, i) => s + i.amount, 0);
    const remaining = Math.max(total - selected, 0);
    const pctRemaining = total > 0 ? (remaining / total) * 100 : 0;
    return { total, selected, remaining, pctRemaining };
  }, [invoices]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return invoices;
    return invoices.filter((i) =>
      [i.vendor, i.description ?? "", i.id].some((t) => t.toLowerCase().includes(q))
    );
  }, [query, invoices]);

  const allSelected = invoices.every((i) => i.selected);
  const anySelected = invoices.some((i) => i.selected);

  const toggle = (id: string, checked: boolean) =>
    setInvoices((prev) => prev.map((i) => (i.id === id ? { ...i, selected: checked } : i)));

  const selectAll = (v: boolean) =>
    setInvoices((prev) => prev.map((i) => ({ ...i, selected: v })));

  const reset = () =>
    setInvoices((prev) => prev.map((i) => ({ ...i, selected: false })));

  return (
    <div className="min-h-[100dvh] bg-background text-foreground">
      {/* Title */}
      <header className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl sm:text-2xl font-semibold tracking-tight">Finance Dashboard — Fatture</h1>
          <div className="hidden sm:flex items-center gap-2">
            <Button variant="ghost" onClick={reset} disabled={!anySelected}>
              Reset spunte
            </Button>
            <Button
              variant={allSelected ? "secondary" : "default"}
              onClick={() => selectAll(!allSelected)}
            >
              {allSelected ? "Deseleziona tutte" : "Seleziona tutte"}
            </Button>
          </div>
        </div>
      </header>

      {/* Main two-pane layout */}
      <main className="mx-auto max-w-6xl px-6 py-6 grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-6 items-start">
        {/* Left: invoice list */}
        <section>
          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center justify-between">
                <span className="text-lg">Fatture da pagare</span>
                <div className="flex items-center gap-2 sm:hidden">
                  <Button size="sm" variant="ghost" onClick={reset} disabled={!anySelected}>
                    Reset
                  </Button>
                  <Button
                    size="sm"
                    variant={allSelected ? "secondary" : "default"}
                    onClick={() => selectAll(!allSelected)}
                  >
                    {allSelected ? "Tutte no" : "Tutte sì"}
                  </Button>
                </div>
              </CardTitle>
              <div className="flex items-center gap-2">
                <Input
                  placeholder="Cerca per fornitore, descrizione o ID…"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
                <Button
                  variant="outline"
                  onClick={() => setQuery("")}
                  className="whitespace-nowrap"
                >
                  Pulisci
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[60vh] pr-2">
                <div className="space-y-3">
                  {filtered.length === 0 ? (
                    <p className="text-sm text-muted-foreground">Nessuna fattura trovata.</p>
                  ) : (
                    filtered.map((inv) => (
                      <InvoiceRow key={inv.id} inv={inv} onToggle={toggle} />
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </section>

        {/* Vertical separator (only md+) */}
        <Separator orientation="vertical" className="hidden md:block h-full mx-auto" />

        {/* Right: total + radial progress */}
        <section className="w-full">
          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Totale previsto da pagare</CardTitle>
              <p className="text-sm text-muted-foreground">
                Seleziona le fatture a sinistra: il cerchio si svuota man mano che arrivi a <span className="font-semibold">zero</span>.
              </p>
            </CardHeader>
            <CardContent className="grid place-items-center gap-6">
              <div className="relative">
                <RadialProgress value={totals.pctRemaining} />
                {/* Center label */}
                <div className="absolute inset-0 grid place-items-center">
                  <div className="text-center leading-tight">
                    <div className="text-xs uppercase tracking-wide text-muted-foreground">
                      Da pagare
                    </div>
                    <div className="text-3xl font-semibold tabular-nums">
                      {EUR.format(totals.remaining)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {Math.round(totals.pctRemaining)}%
                    </div>
                  </div>
                </div>
              </div>

              <div className="w-full grid grid-cols-3 gap-3">
                <Stat label="Selezionato" value={EUR.format(totals.selected)} />
                <Stat label="Totale" value={EUR.format(totals.total)} />
                <Stat
                  label="Residuo"
                  value={EUR.format(totals.remaining)}
                  subtle
                />
              </div>

              <div className="flex flex-wrap gap-3">
                <Button disabled={!anySelected} onClick={() => console.log("TODO: pay API")}>
                  Paga selezionate
                </Button>
                <Button variant="outline" onClick={reset} disabled={!anySelected}>
                  Annulla selezione
                </Button>
              </div>
            </CardContent>
          </Card>
        </section>
      </main>
      {/* --- Sezione upload fatture (nuova) --- */}
      <UploadSection />
         {/* --- Sezione storia fatture (nuova) --- */}
      <HistorySection />
    </div>
  );
}

function Stat({ label, value, subtle = false }: { label: string; value: string; subtle?: boolean }) {
  return (
    <div
      className={`rounded-xl border p-3 ${subtle ? "bg-muted/30" : "bg-background"}`}
    >
      <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}
type UploadedItem = {
  id: string;
  name: string;
  size: number;
  type: string;
  lastModified: number;
};

function humanSize(bytes: number) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

function UploadSection() {
  const [dragActive, setDragActive] = useState(false);
  const [items, setItems] = useState<UploadedItem[]>([]);

  // Accetta i file e aggiorna la lista (dedup su name+size)
  const handleFiles = (fileList: FileList | File[]) => {
    const incoming = Array.from(fileList).map((f) => ({
      id: (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`),
      name: f.name,
      size: f.size,
      type: f.type || (f.name.includes(".") ? f.name.split(".").pop()! : "file"),
      lastModified: f.lastModified ?? Date.now(),
    }));

    setItems((prev) => {
      const key = (x: UploadedItem) => `${x.name}::${x.size}`;
      const map = new Map<string, UploadedItem>();
      [...prev, ...incoming].forEach((x) => map.set(key(x), x));
      return Array.from(map.values()).sort((a, b) => a.name.localeCompare(b.name));
    });
  };

  const onDrop = (e: any) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer?.files?.length) handleFiles(e.dataTransfer.files);
  };

  const onBrowse = (e: any) => {
    const files = e.target.files as FileList;
    if (files?.length) handleFiles(files);
    // reset per poter ricaricare gli stessi file
    e.target.value = "";
  };

  const removeOne = (id: string) => setItems((prev) => prev.filter((x) => x.id !== id));
  const clearAll = () => setItems([]);

  const triggerProcess = () => {
    // Qui collegherai il tuo backend: invia `items`
    console.log("TRIGGER ELABORAZIONE:", items);
  };

  return (
    <section className="mx-auto max-w-6xl px-6 pb-12">
      <h2 className="text-lg sm:text-xl font-semibold tracking-tight mb-4">
        Caricamento fatture
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
        {/* Colonna sinistra: Drag & Drop */}
        <div className="flex flex-col gap-3">
          <Card className="shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Drag &amp; drop per caricare le fatture</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragActive(true);
                }}
                onDragEnter={(e) => {
                  e.preventDefault();
                  setDragActive(true);
                }}
                onDragLeave={(e) => {
                  e.preventDefault();
                  setDragActive(false);
                }}
                onDrop={onDrop}
                onClick={() => document.getElementById("uploader-input")?.click()}
                className={[
                  "rounded-xl border-2 border-dashed p-8 min-h-[240px]",
                  "grid place-items-center text-center cursor-pointer transition",
                  dragActive
                    ? "border-primary bg-primary/5 ring-2 ring-primary/40"
                    : "border-muted-foreground/30 hover:bg-accent/40",
                ].join(" ")}
              >
                <div>
                  <p className="font-medium">Trascina qui i file</p>
                  <p className="text-sm text-muted-foreground">
                    …oppure <span className="underline">sfoglia</span> dal dispositivo
                  </p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Formati consigliati: PDF, XML, CSV, JSON, XLSX, TXT
                  </p>
                </div>
                <input
                  id="uploader-input"
                  type="file"
                  multiple
                  accept=".pdf,.xml,.csv,.json,.xlsx,.txt"
                  className="hidden"
                  onChange={onBrowse}
                />
              </div>
            </CardContent>
          </Card>

          {/* Bottone trigger sotto il box */}
          <div className="flex justify-center">
            <Button onClick={triggerProcess} disabled={items.length === 0}>
              Avvia elaborazione
            </Button>
          </div>
        </div>

        {/* Colonna destra: Lista appena caricate */}
        <div className="flex flex-col gap-3">
          <Card className="shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">File caricati (da controllare)</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[240px] pr-2">
                {items.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    Nessun file caricato. Trascina dei documenti nella casella a sinistra.
                  </p>
                ) : (
                  <ul className="space-y-2">
                    {items.map((f) => (
                      <li
                        key={f.id}
                        className="flex items-center justify-between rounded-lg border p-3 hover:bg-accent/40"
                      >
                        <div className="min-w-0">
                          <p className="truncate font-medium">{f.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {humanSize(f.size)} · {f.type || "file"} ·{" "}
                            {new Date(f.lastModified).toLocaleDateString("it-IT")}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">Pronto</Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-destructive"
                            onClick={() => removeOne(f.id)}
                          >
                            Rimuovi
                          </Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Clear button sotto la lista */}
          <div className="flex justify-center">
            <Button variant="outline" onClick={clearAll} disabled={items.length === 0}>
              Svuota lista
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
type HistoryItem = {
  id: string;
  name: string;
  size: number;          // bytes
  type: string;          // mime/estensione
  uploadedAt: number;    // epoch ms
  source: "drag" | "browse";
  status: "Processed" | "Queued" | "Failed";
};

function fmtDate(ms: number) {
  const d = new Date(ms);
  return `${d.toLocaleDateString("it-IT")} ${d
    .toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" })}`;
}

function HistorySection() {
  // demo dati (interfaccia pronta per collegare backend)
  const demo: HistoryItem[] = [
    { id: "h1", name: "fattura_1234.pdf", size: 234_551, type: "pdf", uploadedAt: Date.now() - 2 * 60_000, source: "drag", status: "Processed" },
    { id: "h2", name: "bolletta_enel_marzo.pdf", size: 121_000, type: "pdf", uploadedAt: Date.now() - 3_600_000, source: "browse", status: "Processed" },
    { id: "h3", name: "aws_oct.csv", size: 78_321, type: "csv", uploadedAt: Date.now() - 86_400_000, source: "browse", status: "Queued" },
    { id: "h4", name: "vodafone_10_2025.xml", size: 64_101, type: "xml", uploadedAt: Date.now() - 2 * 86_400_000, source: "drag", status: "Processed" },
    { id: "h5", name: "supabase_invoice.json", size: 15_440, type: "json", uploadedAt: Date.now() - 3 * 86_400_000, source: "drag", status: "Failed" },
  ];

  const [history, setHistory] = useState<HistoryItem[]>(demo);
  const [q, setQ] = useState("");
  const [sortKey, setSortKey] = useState<"uploadedAt" | "name" | "size">("uploadedAt");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const toggleSort = (key: typeof sortKey) => {
    if (key === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir(key === "uploadedAt" ? "desc" : "asc");
    }
  };

  const iconFor = (key: typeof sortKey) =>
    key !== sortKey ? <ArrowUpDown className="h-4 w-4 opacity-60" /> :
    sortDir === "asc" ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />;

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const base = !needle
      ? history
      : history.filter(h => [h.name, h.type].some(t => t.toLowerCase().includes(needle)));
    const arr = [...base].sort((a, b) => {
      const aV = a[sortKey];
      const bV = b[sortKey];
      const cmp =
        typeof aV === "number" && typeof bV === "number"
          ? aV - bV
          : String(aV).localeCompare(String(bV));
      return sortDir === "asc" ? cmp : -cmp;
    });
    return arr;
  }, [history, q, sortKey, sortDir]);

  const clearAll = () => setHistory([]);
  const humanSize = (n: number) => {
    if (!n) return "0 B";
    const k = 1024, u = ["B","KB","MB","GB","TB"];
    const i = Math.floor(Math.log(n)/Math.log(k));
    return `${(n/Math.pow(k,i)).toFixed(1)} ${u[i]}`;
  };

  const statusBadge = (s: HistoryItem["status"]) =>
    s === "Processed" ? (
      <Badge variant="secondary">Elaborato</Badge>
    ) : s === "Queued" ? (
      <Badge>In coda</Badge>
    ) : (
      <Badge variant="destructive">Errore</Badge>
    );

  return (
    <section className="mx-auto max-w-6xl px-6 pb-12">
      <Card className="shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Storico caricamenti
          </CardTitle>
          <div className="mt-3 flex flex-col sm:flex-row gap-2">
            <div className="flex-1 flex items-center gap-2">
              <Input
                placeholder="Cerca per nome o tipo…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
              <Button variant="outline" onClick={() => setQ("")}>Pulisci</Button>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => toggleSort("uploadedAt")}>
                Data {iconFor("uploadedAt")}
              </Button>
              <Button variant="outline" onClick={() => toggleSort("name")}>
                Nome {iconFor("name")}
              </Button>
              <Button variant="outline" onClick={() => toggleSort("size")}>
                Dimensione {iconFor("size")}
              </Button>
              <Button variant="ghost" onClick={clearAll} disabled={history.length === 0}>
                Svuota storico
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="rounded-xl border">
            {/* Header */}
            <div className="grid grid-cols-[4fr_1fr_1fr_2fr_1fr] px-4 py-2 text-xs uppercase tracking-wide text-muted-foreground border-b">
              <div>Nome file</div>
              <div>Tipo</div>
              <div>Dimensione</div>
              <div>Caricato il</div>
              <div className="text-right">Stato</div>
            </div>

            <ScrollArea className="h-[360px]">
              {filtered.length === 0 ? (
                <div className="p-6 text-sm text-muted-foreground">
                  Nessun elemento nello storico.
                </div>
              ) : (
                <ul className="divide-y">
                  {filtered.map((h) => (
                    <li key={h.id} className="grid grid-cols-[4fr_1fr_1fr_2fr_1fr] items-center px-4 py-3 hover:bg-accent/40">
                      <div className="truncate font-medium">{h.name}</div>
                      <div className="uppercase text-xs">{h.type || "file"}</div>
                      <div className="tabular-nums">{humanSize(h.size)}</div>
                      <div className="tabular-nums">{fmtDate(h.uploadedAt)}</div>
                      <div className="text-right">{statusBadge(h.status)}</div>
                    </li>
                  ))}
                </ul>
              )}
            </ScrollArea>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}


