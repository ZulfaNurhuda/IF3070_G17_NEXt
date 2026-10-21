import { svgElement } from "../dom";
import type { Bounds, ChartLine } from "./scale";

export type MoveMarker = (iteration: number) => void;

const WIDTH = 640;
const MARGIN = { left: 44, right: 12, top: 12, bottom: 24 };

function horizontalLine(className: string, y: number): SVGElement {
  return svgElement("line", {
    class: className,
    x1: MARGIN.left,
    y1: y,
    x2: WIDTH - MARGIN.right,
    y2: y,
  });
}

function tickLabel(x: number, y: number, edge: "start" | "end", text: string): SVGElement {
  return svgElement("text", { class: `tick-label tick-${edge}`, x, y }, text);
}

export function drawChart(
  svg: SVGSVGElement,
  lines: ChartLine[],
  lastIteration: number,
  [bottom, top]: Bounds,
  height: number,
): MoveMarker {
  const toX = (iteration: number): number =>
    MARGIN.left + (iteration / lastIteration) * (WIDTH - MARGIN.left - MARGIN.right);
  const plotBottom = height - MARGIN.bottom;
  const toY = (value: number): number =>
    MARGIN.top + ((top - value) / (top - bottom)) * (plotBottom - MARGIN.top);
  svg.setAttribute("viewBox", `0 0 ${WIDTH} ${height}`);
  const children: SVGElement[] = [horizontalLine("axis", toY(0))];
  for (const tick of [bottom, bottom < 0 && top > 0 ? 0 : (bottom + top) / 2, top]) {
    children.push(
      horizontalLine("gridline", toY(tick)),
      tickLabel(MARGIN.left - 6, toY(tick) + 4, "end", String(Math.round(tick * 100) / 100)),
    );
  }
  for (const line of lines) {
    const points = line.points.map(([x, y]) => `${toX(x).toFixed(1)},${toY(y).toFixed(1)}`);
    children.push(svgElement("polyline", { class: line.className, points: points.join(" ") }));
  }
  const marker = svgElement("line", { class: "marker", y1: MARGIN.top, y2: plotBottom });
  children.push(
    marker,
    tickLabel(MARGIN.left, height - 6, "start", "0"),
    tickLabel(WIDTH - MARGIN.right, height - 6, "end", String(lastIteration)),
  );
  svg.replaceChildren(...children);
  return (iteration) => {
    const x = String(toX(iteration));
    marker.setAttribute("x1", x);
    marker.setAttribute("x2", x);
  };
}
