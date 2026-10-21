import type { TimelineEntry } from "../../data/timeline";
import type { ExperimentPayload, HistoryEntry } from "../../data/types";
import { byId } from "../dom";
import { describeNote, describeStep, formatValue, sumOf } from "./format";

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
