import { buildStateTimeline, type TimelineEntry } from "./data/timeline";
import type { ExperimentPayload, HistoryEntry } from "./data/types";
import { renderHistoryChart } from "./view/chart";
import { renderRunDetails, renderStep } from "./view/info";
import { renderShip } from "./view/ship";

export interface Viewer {
  show(experiment: ExperimentPayload, runIndex: number): void;
  goTo(target: number): void;
  move(offset: number): void;
  last(): void;
}

export function createViewer(ship: SVGSVGElement): Viewer {
  let experiment: ExperimentPayload | undefined;
  let timeline: TimelineEntry[] = [];
  let records = new Map<number, HistoryEntry>();
  let index = 0;
  let moveMarker = (_iteration: number): void => {};

  function render(): void {
    const entry = timeline[index];
    if (experiment === undefined || entry === undefined) {
      return;
    }
    renderShip(ship, entry, experiment.problem);
    renderStep(experiment, entry, records.get(entry.iteration), index, timeline.length - 1);
    moveMarker(entry.iteration);
  }

  function goTo(target: number): void {
    index = Math.min(Math.max(target, 0), timeline.length - 1);
    render();
  }

  return {
    show(source, runIndex) {
      const run = source.runs[runIndex];
      if (run === undefined) {
        return;
      }
      const nextTimeline = buildStateTimeline(run);
      const nextRecords = new Map(run.history.map((record) => [record.iteration, record]));
      const nextMarker = renderHistoryChart(run);
      renderRunDetails(source, run);
      experiment = source;
      timeline = nextTimeline;
      records = nextRecords;
      moveMarker = nextMarker;
      goTo(0);
    },
    goTo,
    move: (offset) => goTo(index + offset),
    last: () => goTo(timeline.length - 1),
  };
}
