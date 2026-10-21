import type { TimelineEntry } from "../../data/timeline";
import type { ChangePayload, HistoryEntry, VehiclePayload } from "../../data/types";
import { metricKeys, metricView } from "../metrics";

function describeChange(change: ChangePayload): string {
  const { from, to } = change;
  if (to === null) {
    return `${change.id} keluar dari kapal`;
  }
  const target = `(${to.x}, ${to.y}) ${to.orientation.toLowerCase()}`;
  if (from === null) {
    return `${change.id} masuk ke ${target}`;
  }
  if (from.x === to.x && from.y === to.y) {
    return `${change.id} diputar menjadi ${to.orientation.toLowerCase()}`;
  }
  return `${change.id} pindah ke ${target}`;
}

export function formatValue(value: unknown): string {
  if (value === null) {
    return "otomatis";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : String(Number(value.toPrecision(6)));
  }
  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${formatValue(item)}`)
      .join(", ");
  }
  return String(value);
}

export function sumOf(vehicles: VehiclePayload[], key: "weight" | "shipping_fee"): number {
  return vehicles.reduce((sum, vehicle) => sum + vehicle[key], 0);
}

export function describeStep(entry: TimelineEntry, index: number): string {
  if (index === 0) {
    return "State awal";
  }
  if (entry.changes.length === 0) {
    return "Tidak ada perubahan";
  }
  return entry.changes.map(describeChange).join("; ");
}

export function describeNote(record: HistoryEntry | undefined): string {
  if (record === undefined) {
    return "";
  }
  return metricKeys([record])
    .map((key) => `${metricView(key).label}: ${formatValue(record[key])}`)
    .join(", ");
}
