import { byId, svgElement } from "./dom";
import type { HistoryEntry, RunPayload } from "./types";

interface ChartLine {
  points: [number, number][];
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

function horizontalLine(className: string, y: number): SVGElement {
  return svgElement("line", {
    class: className,
    x1: MARGIN.left,
    y1: y,
    x2: WIDTH - MARGIN.right,
    y2: y,
  });
}

function tickLabel(x: number, y: number, anchor: string, text: string): SVGElement {
  return svgElement("text", { class: "tick-label", x, y, "text-anchor": anchor }, text);
}

function drawChart(
  svg: SVGSVGElement,
  lines: ChartLine[],
  top: number,
  height: number,
): MoveMarker {
  const lastIteration = lines.reduce(
    (largest, line) => line.points.reduce((inner, [x]) => Math.max(inner, x), largest),
    1,
  );
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

function valueLines(history: HistoryEntry[], population: boolean): ChartLine[] {
  const lines: ChartLine[] = [
    {
      points: history.map((entry): [number, number] => [entry.iteration, entry.value]),
      className: "series series-main",
    },
  ];
  if (population) {
    lines.push({
      points: history.map((entry): [number, number] => [entry.iteration, entry.average_value ?? 0]),
      className: "series series-secondary",
    });
  }
  return lines;
}

export function renderHistoryChart(run: RunPayload, population: boolean): MoveMarker {
  const lines = valueLines(run.history, population);
  const largest = lines.reduce(
    (highest, line) => line.points.reduce((inner, [, y]) => Math.max(inner, y), highest),
    0,
  );
  byId("chart-title").textContent = population
    ? "Nilai maksimum (garis) dan rata-rata (putus-putus) populasi"
    : "Nilai terhadap iterasi";
  const markers = [drawChart(byId<SVGSVGElement>("history-chart"), lines, niceTop(largest), 160)];
  const probabilities = run.history.flatMap((entry): [number, number][] =>
    entry.acceptance_probability === undefined
      ? []
      : [[entry.iteration, entry.acceptance_probability]],
  );
  byId("probability-section").hidden = probabilities.length === 0;
  if (probabilities.length > 0) {
    markers.push(
      drawChart(
        byId<SVGSVGElement>("probability-chart"),
        [{ points: probabilities, className: "series series-probability" }],
        1,
        110,
      ),
    );
  }
  return (iteration) => {
    for (const moveMarker of markers) {
      moveMarker(iteration);
    }
  };
}
