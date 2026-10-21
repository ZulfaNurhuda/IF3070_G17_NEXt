import { byId, svgElement, textElement } from "./dom";
import { metricKeys, metricView, unitLabel } from "./metrics";
import type { HistoryEntry, RunPayload } from "./types";

type Point = [number, number];

interface ChartLine {
  points: Point[];
  className: string;
}

type MoveMarker = (iteration: number) => void;

const WIDTH = 640;
const MARGIN = { left: 44, right: 12, top: 12, bottom: 24 };

function niceTop(maximum: number): number {
  if (maximum <= 0) {
    return 1;
  }
  const magnitude = 10 ** Math.floor(Math.log10(maximum));
  return Math.ceil(maximum / magnitude) * magnitude;
}

function seriesPoints(history: HistoryEntry[], key: string): Point[] {
  return history.flatMap((entry): Point[] => {
    const value = entry[key];
    return value === undefined ? [] : [[entry.iteration, value]];
  });
}

function largestValue(lines: ChartLine[]): number {
  return lines.reduce(
    (largest, line) => line.points.reduce((inner, [, value]) => Math.max(inner, value), largest),
    0,
  );
}

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

function drawChart(
  svg: SVGSVGElement,
  lines: ChartLine[],
  lastIteration: number,
  top: number,
  height: number,
): MoveMarker {
  const toX = (iteration: number): number =>
    MARGIN.left + (iteration / lastIteration) * (WIDTH - MARGIN.left - MARGIN.right);
  const toY = (value: number): number =>
    MARGIN.top + (1 - value / top) * (height - MARGIN.top - MARGIN.bottom);
  svg.setAttribute("viewBox", `0 0 ${WIDTH} ${height}`);
  const children: SVGElement[] = [horizontalLine("axis", toY(0))];
  for (const tick of [0, top / 2, top]) {
    children.push(
      horizontalLine("gridline", toY(tick)),
      tickLabel(MARGIN.left - 6, toY(tick) + 4, "end", String(Math.round(tick * 100) / 100)),
    );
  }
  for (const line of lines) {
    const points = line.points.map(([x, y]) => `${toX(x).toFixed(1)},${toY(y).toFixed(1)}`);
    children.push(svgElement("polyline", { class: line.className, points: points.join(" ") }));
  }
  const marker = svgElement("line", { class: "marker", y1: MARGIN.top, y2: toY(0) });
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

function metricBlock(title: string, svg: SVGSVGElement): HTMLDivElement {
  const block = document.createElement("div");
  block.className = "charts-secondary";
  const heading = textElement("div", title);
  heading.className = "muted";
  block.append(heading, svg);
  return block;
}

export function renderHistoryChart(run: RunPayload): MoveMarker {
  const keys = metricKeys(run.history);
  const overlays = keys.filter((key) => metricView(key).placement === "overlay");
  const separate = keys.filter((key) => metricView(key).placement === "separate");
  const lines: ChartLine[] = [
    { points: seriesPoints(run.history, "value"), className: "series series-main" },
    ...overlays.map((key) => ({
      points: seriesPoints(run.history, key),
      className: metricView(key).className,
    })),
  ];
  const unit = unitLabel(run.unit).toLowerCase();
  const overlayLabels = overlays.map((key) => metricView(key).label).join(", ");
  byId("chart-title").textContent =
    overlays.length > 0
      ? `Nilai objective terhadap ${unit} dan ${overlayLabels} (putus-putus)`
      : `Nilai objective terhadap ${unit}`;
  const lastIteration = Math.max(1, run.iterations);
  const markers = [
    drawChart(
      byId<SVGSVGElement>("history-chart"),
      lines,
      lastIteration,
      niceTop(largestValue(lines)),
      160,
    ),
  ];
  byId("metric-charts").replaceChildren(
    ...separate.map((key) => {
      const view = metricView(key);
      const lines = [{ points: seriesPoints(run.history, key), className: view.className }];
      const svg = svgElement("svg", { role: "img", "aria-label": view.title }) as SVGSVGElement;
      markers.push(
        drawChart(svg, lines, lastIteration, view.top ?? niceTop(largestValue(lines)), 110),
      );
      return metricBlock(view.title, svg);
    }),
  );
  return (iteration) => {
    for (const moveMarker of markers) {
      moveMarker(iteration);
    }
  };
}
