import { loadExperiment, loadFileList } from "./api";
import { renderHistoryChart } from "./chart";
import { byId, showMessage, textElement } from "./dom";
import { renderRunDetails, renderStep } from "./info";
import { renderShip } from "./ship";
import { buildStateTimeline, type TimelineEntry } from "./timeline";
import type { ExperimentPayload, FileEntry, HistoryEntry } from "./types";

async function main(): Promise<void> {
  const fileSelect = byId<HTMLSelectElement>("file-select");
  const runSelect = byId<HTMLSelectElement>("run-select");
  const ship = byId<SVGSVGElement>("ship");
  let files: FileEntry[] = [];
  let experiment: ExperimentPayload | undefined;
  let timeline: TimelineEntry[] = [];
  let records = new Map<number, HistoryEntry>();
  let index = 0;
  let latestRequest = 0;
  let shownFile = -1;
  let shownRun = 0;
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

  function move(step: number): void {
    index = Math.min(Math.max(index + step, 0), timeline.length - 1);
    render();
  }

  function showRun(source: ExperimentPayload, runIndex: number): void {
    const run = source.runs[runIndex];
    if (run === undefined) {
      return;
    }
    const nextTimeline = buildStateTimeline(run);
    const nextRecords = new Map(run.history.map((record) => [record.iteration, record]));
    const population = run.history.some((record) => record.average_value !== undefined);
    const nextMarker = renderHistoryChart(run, population);
    renderRunDetails(source, run, population);
    experiment = source;
    timeline = nextTimeline;
    records = nextRecords;
    moveMarker = nextMarker;
    shownRun = runIndex;
    index = 0;
    render();
  }

  async function selectFile(): Promise<void> {
    const fileIndex = fileSelect.selectedIndex;
    const entry = files[fileIndex];
    if (entry === undefined) {
      return;
    }
    const request = ++latestRequest;
    try {
      const loaded = await loadExperiment(entry);
      if (request !== latestRequest) {
        return;
      }
      showRun(loaded, 0);
      runSelect.replaceChildren(
        ...loaded.runs.map((item) => textElement("option", `Run ${item.run} (seed ${item.seed})`)),
      );
      shownFile = fileIndex;
    } catch (error) {
      if (request === latestRequest) {
        fileSelect.selectedIndex = shownFile;
        showMessage(error);
      }
    }
  }

  fileSelect.addEventListener("change", () => void selectFile());
  runSelect.addEventListener("change", () => {
    try {
      if (experiment !== undefined) {
        showRun(experiment, runSelect.selectedIndex);
      }
    } catch (error) {
      runSelect.selectedIndex = shownRun;
      showMessage(error);
    }
  });
  byId("step-back").addEventListener("click", () => move(-1));
  byId("step-next").addEventListener("click", () => move(1));

  try {
    files = await loadFileList();
    if (files.length === 0) {
      showMessage("Belum ada hasil di folder output. Jalankan eksperimen terlebih dahulu.");
      return;
    }
    fileSelect.replaceChildren(
      ...files.map((entry) => textElement("option", `${entry.folder} / ${entry.name}`)),
    );
    await selectFile();
  } catch (error) {
    showMessage(error);
  }
}

void main();
