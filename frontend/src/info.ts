import { byId } from "./dom";
import type { TimelineEntry } from "./timeline";
import type { ChangePayload, ExperimentPayload, RunPayload } from "./types";

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
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : String(Math.round(value * 100) / 100);
  }
  if (typeof value === "object" && value !== null) {
    return JSON.stringify(value);
  }
  return String(value);
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

function describeNote(record: RunPayload["history"][number] | undefined): string {
  if (record?.acceptance_probability !== undefined) {
    return `Peluang penerimaan: ${formatValue(record.acceptance_probability)}`;
  }
  if (record?.maximum_value !== undefined && record.average_value !== undefined) {
    return `Maksimum ${formatValue(record.maximum_value)}, rata-rata ${formatValue(record.average_value)}`;
  }
  return "";
}

function renderDetails(experiment: ExperimentPayload, run: RunPayload): void {
  const details: [string, unknown][] = [
    ["algorithm", experiment.algorithm],
    ["objective", experiment.objective],
    ["run", run.run],
    ["seed", run.seed],
    ["duration_seconds", run.duration_seconds],
    ["iterations", run.iterations],
    ["nilai awal", run.initial_state.value],
    ["nilai akhir", run.final_state.value],
    ...Object.entries(experiment.params),
    ...Object.entries(run.extra),
  ];
  byId("details").replaceChildren(
    ...details.map(([key, detail]) => {
      const line = document.createElement("div");
      line.textContent = `${key}: ${formatValue(detail)}`;
      return line;
    }),
  );
}

export function renderInfo(
  experiment: ExperimentPayload,
  run: RunPayload,
  timeline: TimelineEntry[],
  index: number,
): void {
  const entry = timeline[index];
  if (entry === undefined) {
    return;
  }
  const record = run.history.find((item) => item.iteration === entry.iteration);
  const value = index === 0 ? run.initial_state.value : record?.value;
  const vehicles = experiment.problem.vehicles;
  const weight = vehicles.reduce(
    (sum, vehicle) => sum + (entry.placements.has(vehicle.id) ? vehicle.weight : 0),
    0,
  );
  const outside = vehicles
    .filter((vehicle) => !entry.placements.has(vehicle.id))
    .map((vehicle) => vehicle.id);
  byId("unit-label").textContent =
    experiment.algorithm === "genetic-algorithm" ? "Generasi" : "Iterasi";
  byId("iteration").textContent = String(entry.iteration);
  byId("value").textContent = value === undefined ? "-" : formatValue(value);
  byId("weight").textContent = `Berat ${weight} dari ${experiment.problem.ship.max_capacity}`;
  byId("change").textContent = describeStep(entry, index);
  byId("note").textContent = describeNote(record);
  byId("outside").textContent = outside.length > 0 ? outside.join(", ") : "Semua terangkut";
  byId("step-label").textContent = `Step ${index} dari ${timeline.length - 1}`;
  renderDetails(experiment, run);
}
