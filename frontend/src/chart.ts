import { byId, svgElement } from "./dom";
import type { RunPayload } from "./types";

interface ChartLine {
  points: [number, number][];
  className: string;
}

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
  marker: number,
  top: number,
  height: number,
): void {
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
  children.push(
    svgElement("line", {
      class: "marker",
      x1: toX(marker),
      y1: MARGIN.top,
      x2: toX(marker),
      y2: toY(0),
    }),
    tickLabel(MARGIN.left, height - 6, "start", "0"),
    tickLabel(WIDTH - MARGIN.right, height - 6, "end", String(lastIteration)),
  );
  svg.replaceChildren(...children);
}

function valueLines(run: RunPayload): { lines: ChartLine[]; isPopulation: boolean } {
  const history = run.history;
  const isPopulation = history.some(
    (entry) => entry.maximum_value !== undefined && entry.average_value !== undefined,
  );
  if (!isPopulation) {
    const points = history.map((entry): [number, number] => [entry.iteration, entry.value]);
    return { lines: [{ points, className: "series series-main" }], isPopulation };
  }
  return {
    isPopulation,
    lines: [
      {
        points: history.map((entry): [number, number] => [
          entry.iteration,
          entry.maximum_value ?? entry.value,
        ]),
        className: "series series-main",
      },
      {
        points: history.map((entry): [number, number] => [
          entry.iteration,
          entry.average_value ?? 0,
        ]),
        className: "series series-secondary",
      },
    ],
  };
}

export function renderHistoryChart(run: RunPayload, iteration: number): void {
  const { lines, isPopulation } = valueLines(run);
  const largest = Math.max(...lines.flatMap((line) => line.points.map(([, y]) => y)));
  byId("chart-title").textContent = isPopulation
    ? "Nilai maksimum (garis) dan rata-rata (putus-putus) populasi"
    : "Nilai terhadap iterasi";
  drawChart(byId<SVGSVGElement>("history-chart"), lines, iteration, niceTop(largest), 160);
  const probabilities = run.history.flatMap((entry): [number, number][] =>
    entry.acceptance_probability === undefined
      ? []
      : [[entry.iteration, entry.acceptance_probability]],
  );
  byId("probability-section").hidden = probabilities.length === 0;
  if (probabilities.length > 0) {
    drawChart(
      byId<SVGSVGElement>("probability-chart"),
      [{ points: probabilities, className: "series series-probability" }],
      iteration,
      1,
      110,
    );
  }
}
