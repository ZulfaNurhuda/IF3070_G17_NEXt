import { loadExperiment, loadFileList } from "./api";
import { renderHistoryChart } from "./chart";
import { byId, option, showMessage } from "./dom";
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

  function selectRun(): void {
    const run = experiment?.runs[runSelect.selectedIndex];
    if (experiment === undefined || run === undefined) {
      return;
    }
    timeline = buildStateTimeline(run);
    records = new Map(run.history.map((record) => [record.iteration, record]));
    const population = run.history.some((record) => record.average_value !== undefined);
    moveMarker = renderHistoryChart(run, population);
    renderRunDetails(experiment, run, population);
    index = 0;
    render();
  }

  async function selectFile(): Promise<void> {
    const entry = files[fileSelect.selectedIndex];
    if (entry === undefined) {
      return;
    }
    const request = ++latestRequest;
    const loaded = await loadExperiment(entry);
    if (request !== latestRequest) {
      return;
    }
    experiment = loaded;
    runSelect.replaceChildren(
      ...experiment.runs.map((item) => option(`Run ${item.run} (seed ${item.seed})`)),
    );
    selectRun();
  }

  function move(step: number): void {
    index = Math.min(Math.max(index + step, 0), timeline.length - 1);
    render();
  }

  fileSelect.addEventListener("change", () => selectFile().catch(showMessage));
  runSelect.addEventListener("change", () => {
    try {
      selectRun();
    } catch (error) {
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
    fileSelect.replaceChildren(...files.map((entry) => option(`${entry.folder} / ${entry.name}`)));
    await selectFile();
  } catch (error) {
    showMessage(error);
  }
}

void main();
