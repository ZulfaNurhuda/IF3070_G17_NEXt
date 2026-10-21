import type { TimelineEntry } from "./data/timeline";
import type { Orientation, PlacementPayload, ProblemPayload, VehiclePayload } from "./data/types";
import { svgElement } from "./dom";

const CELL = 32;
const HUE_CLASSES = 12;
const LABEL_PADDING = 6;
const GLYPH_WIDTH = 0.6;
const LABEL_FITS: [number, string][] = [
  [16, "label-lg"],
  [13, "label-md"],
  [11, "label-sm"],
];

function labelClass(vehicle: VehiclePayload, width: number): string {
  const fit = (width - LABEL_PADDING) / (vehicle.id.length * GLYPH_WIDTH);
  const match = LABEL_FITS.find(([minimum]) => fit >= minimum);
  return `vehicle-label ${match === undefined ? "label-xs" : match[1]}`;
}

function footprint(
  vehicle: VehiclePayload,
  orientation: Orientation,
): { across: number; down: number } {
  if (orientation === "Vertical") {
    return { across: vehicle.width, down: vehicle.length };
  }
  return { across: vehicle.length, down: vehicle.width };
}

function gridLines(width: number, length: number): SVGElement[] {
  const line = (x1: number, y1: number, x2: number, y2: number): SVGElement =>
    svgElement("line", { class: "gridline", x1, y1, x2, y2 });
  const columns = Array.from({ length: width - 1 }, (_, index) => 1 + (index + 1) * CELL);
  const rows = Array.from({ length: length - 1 }, (_, index) => 1 + (index + 1) * CELL);
  return [
    ...columns.map((x) => line(x, 1, x, 1 + length * CELL)),
    ...rows.map((y) => line(1, y, 1 + width * CELL, y)),
  ];
}

function vehicleShape(
  vehicle: VehiclePayload,
  index: number,
  placement: PlacementPayload,
  changed: boolean,
): SVGElement {
  const { across, down } = footprint(vehicle, placement.orientation);
  const left = 1 + placement.x * CELL;
  const top = 1 + placement.y * CELL;
  const hue = `hue-${index % HUE_CLASSES}`;
  const group = svgElement("g", { class: changed ? `vehicle ${hue} changed` : `vehicle ${hue}` });
  group.append(
    svgElement("rect", {
      class: "vehicle-body",
      x: left + 2,
      y: top + 2,
      width: across * CELL - 4,
      height: down * CELL - 4,
    }),
    svgElement(
      "text",
      {
        class: labelClass(vehicle, across * CELL),
        x: left + (across * CELL) / 2,
        y: top + (down * CELL) / 2,
      },
      vehicle.id,
    ),
  );
  return group;
}

export function renderShip(
  svg: SVGSVGElement,
  entry: TimelineEntry,
  problem: ProblemPayload,
): void {
  const { width, length } = problem.ship;
  svg.setAttribute("viewBox", `0 0 ${width * CELL + 2} ${length * CELL + 2}`);
  const changed = new Set(entry.changes.map((change) => change.id));
  const vehicles = problem.vehicles.flatMap((vehicle, index) => {
    const placement = entry.placements.get(vehicle.id);
    return placement === undefined
      ? []
      : [vehicleShape(vehicle, index, placement, changed.has(vehicle.id))];
  });
  svg.replaceChildren(
    svgElement("rect", {
      class: "ship-frame",
      x: 1,
      y: 1,
      width: width * CELL,
      height: length * CELL,
    }),
    ...gridLines(width, length),
    ...vehicles,
  );
}
