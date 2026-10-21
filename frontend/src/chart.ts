import type { HistoryEntry, RunPayload } from "./data/types";
import { byId, svgElement, textElement } from "./dom";
import { metricKeys, metricView, unitLabel } from "./metrics";

type Point = [number, number];

interface ChartLine {
  points: Point[];
  className: string;
}

type MoveMarker = (iteration: number) => void;
type Bounds = [number, number];

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

function valueBounds(lines: ChartLine[]): Bounds {
  let minimum = 0;
  let maximum = 0;
  for (const line of lines) {
    for (const [, value] of line.points) {
      minimum = Math.min(minimum, value);
      maximum = Math.max(maximum, value);
    }
  }
  const top = maximum > 0 ? niceTop(maximum) : 0;
  const bottom = minimum < 0 ? -niceTop(-minimum) : 0;
  return top === bottom ? [0, 1] : [bottom, top];
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
    drawChart(byId<SVGSVGElement>("history-chart"), lines, lastIteration, valueBounds(lines), 160),
  ];
  byId("metric-charts").replaceChildren(
    ...separate.map((key) => {
      const view = metricView(key);
      const lines = [{ points: seriesPoints(run.history, key), className: view.className }];
      const svg = svgElement("svg", { role: "img", "aria-label": view.title }) as SVGSVGElement;
      markers.push(
        drawChart(
          svg,
          lines,
          lastIteration,
          view.top === undefined ? valueBounds(lines) : [0, view.top],
          110,
        ),
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
