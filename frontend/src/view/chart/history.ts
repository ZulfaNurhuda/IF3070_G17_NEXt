import type { RunPayload } from "../../data/types";
import { byId, svgElement, textElement } from "../dom";
import { metricKeys, metricView, unitLabel } from "../metrics";
import { drawChart, type MoveMarker } from "./draw";
import { type ChartLine, seriesPoints, valueBounds } from "./scale";

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
