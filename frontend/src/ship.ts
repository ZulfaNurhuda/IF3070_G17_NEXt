import { svgElement } from "./dom";
import type { TimelineEntry } from "./timeline";
import type { Orientation, ProblemPayload, VehiclePayload } from "./types";

const CELL = 32;

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
  const lines: SVGElement[] = [];
  for (let column = 1; column < width; column++) {
    const x = 1 + column * CELL;
    lines.push(
      svgElement("line", { class: "ship-gridline", x1: x, y1: 1, x2: x, y2: 1 + length * CELL }),
    );
  }
  for (let row = 1; row < length; row++) {
    const y = 1 + row * CELL;
    lines.push(
      svgElement("line", { class: "ship-gridline", x1: 1, y1: y, x2: 1 + width * CELL, y2: y }),
    );
  }
  return lines;
}

function vehicleShape(
  vehicle: VehiclePayload,
  index: number,
  x: number,
  y: number,
  orientation: Orientation,
  changed: boolean,
): SVGElement {
  const { across, down } = footprint(vehicle, orientation);
  const left = 1 + x * CELL;
  const top = 1 + y * CELL;
  const group = svgElement("g", { class: changed ? "vehicle changed" : "vehicle" });
  group.style.setProperty("--hue", String((index * 47) % 360));
  group.append(
    svgElement("rect", {
      class: "vehicle-body",
      x: left + 2,
      y: top + 2,
      width: across * CELL - 4,
      height: down * CELL - 4,
      rx: 3,
    }),
    svgElement(
      "text",
      {
        class: "vehicle-label",
        x: left + (across * CELL) / 2,
        y: top + (down * CELL) / 2,
        "font-size": Math.max(9, Math.min(16, (across * CELL - 6) / (vehicle.id.length * 0.6))),
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
  const vehicles: SVGElement[] = [];
  problem.vehicles.forEach((vehicle, index) => {
    const placement = entry.placements.get(vehicle.id);
    if (placement !== undefined) {
      vehicles.push(
        vehicleShape(
          vehicle,
          index,
          placement.x,
          placement.y,
          placement.orientation,
          changed.has(vehicle.id),
        ),
      );
    }
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
