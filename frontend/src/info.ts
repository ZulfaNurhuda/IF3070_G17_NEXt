import type { TimelineEntry } from "./data/timeline";
import type {
  ChangePayload,
  ExperimentPayload,
  HistoryEntry,
  RunPayload,
  VehiclePayload,
} from "./data/types";
import { byId, textElement } from "./dom";
import { metricKeys, metricView, unitLabel } from "./metrics";

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

function formatValue(value: unknown): string {
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

function sumOf(vehicles: VehiclePayload[], key: "weight" | "shipping_fee"): number {
  return vehicles.reduce((sum, vehicle) => sum + vehicle[key], 0);
}

function describeStep(entry: TimelineEntry, index: number): string {
  if (index === 0) {
    return "State awal";
  }
  if (entry.changes.length === 0) {
    return "Tidak ada perubahan";
  }
  return entry.changes.map(describeChange).join("; ");
}

function describeNote(record: HistoryEntry | undefined): string {
  if (record === undefined) {
    return "";
  }
  return metricKeys([record])
    .map((key) => `${metricView(key).label}: ${formatValue(record[key])}`)
    .join(", ");
}

export function renderRunDetails(experiment: ExperimentPayload, run: RunPayload): void {
  byId("unit-label").textContent = unitLabel(run.unit);
  const details: [string, unknown][] = [
    ["algorithm", experiment.algorithm],
    ["objective", experiment.objective],
    ["run", run.run],
    ["seed", run.seed],
    ["duration_seconds", run.duration_seconds],
    ["iterations", run.iterations],
    ["nilai awal", run.initial_state.value],
    ["nilai akhir", run.final_state.value],
    ...Object.entries(experiment.params).map(([key, value]): [string, unknown] =>
      value === null && key in run.extra
        ? [key, `${formatValue(run.extra[key])} (otomatis)`]
        : [key, value],
    ),
    ...Object.entries(run.extra).filter(([key]) => !(key in experiment.params)),
  ];
  byId("details").replaceChildren(
    ...details.map(([key, detail]) => textElement("div", `${key}: ${formatValue(detail)}`)),
  );
}

export function renderStep(
  experiment: ExperimentPayload,
  entry: TimelineEntry,
  record: HistoryEntry | undefined,
  index: number,
  lastIndex: number,
): void {
  const vehicles = experiment.problem.vehicles;
  const carried = vehicles.filter((vehicle) => entry.placements.has(vehicle.id));
  const outside = vehicles
    .filter((vehicle) => !entry.placements.has(vehicle.id))
    .map((vehicle) => vehicle.id);
  byId("iteration").textContent = String(entry.iteration);
  byId("value").textContent = record === undefined ? "-" : formatValue(record.value);
  byId("weight").textContent =
    `Berat ${sumOf(carried, "weight")} dari ${experiment.problem.ship.max_capacity}`;
  byId("fee").textContent = `Total fee ${sumOf(carried, "shipping_fee")}`;
  byId("change").textContent = describeStep(entry, index);
  byId("note").textContent = describeNote(record);
  byId("outside").textContent = outside.length > 0 ? outside.join(", ") : "Semua terangkut";
  byId("step-label").textContent = `Step ${index} dari ${lastIndex}`;
}
