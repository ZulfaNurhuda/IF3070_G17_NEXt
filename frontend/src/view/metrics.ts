import type { HistoryEntry } from "../data/types";

export interface MetricView {
  label: string;
  title: string;
  placement: "overlay" | "separate";
  className: string;
  top?: number;
}

const METRIC_VIEWS: Record<string, MetricView> = {
  average_value: {
    label: "rata-rata populasi",
    title: "Rata-rata nilai populasi",
    placement: "overlay",
    className: "series series-secondary",
  },
  acceptance_probability: {
    label: "peluang penerimaan",
    title: "Peluang penerimaan e^(ΔE/T)",
    placement: "separate",
    className: "series series-probability",
    top: 1,
  },
};

const UNIT_LABELS: Record<string, string> = { iteration: "Iterasi", generation: "Generasi" };
const RESERVED_KEYS = new Set(["iteration", "value"]);

export function metricView(key: string): MetricView {
  return (
    METRIC_VIEWS[key] ?? {
      label: key,
      title: key,
      placement: "separate",
      className: "series series-extra",
    }
  );
}

export function metricKeys(history: HistoryEntry[]): string[] {
  const keys = new Set<string>();
  for (const entry of history) {
    for (const key of Object.keys(entry)) {
      if (!RESERVED_KEYS.has(key)) {
        keys.add(key);
      }
    }
  }
  return [...keys];
}

export function unitLabel(unit: string | undefined): string {
  return UNIT_LABELS[unit ?? "iteration"] ?? "Iterasi";
}
