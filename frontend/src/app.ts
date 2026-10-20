import { loadExperiment, loadFileList } from "./api";
import { renderHistoryChart } from "./chart";
import { byId, option, showMessage } from "./dom";
import { renderInfo } from "./info";
import { renderShip } from "./ship";
import { buildStateTimeline, type TimelineEntry } from "./timeline";
import type { ExperimentPayload, FileEntry, RunPayload } from "./types";

export async function main(): Promise<void> {
  const fileSelect = byId<HTMLSelectElement>("file-select");
  const runSelect = byId<HTMLSelectElement>("run-select");
  const ship = byId<SVGSVGElement>("ship");
  let files: FileEntry[] = [];
  let experiment: ExperimentPayload | undefined;
  let run: RunPayload | undefined;
  let timeline: TimelineEntry[] = [];
  let index = 0;

  function render(): void {
    const entry = timeline[index];
    if (experiment === undefined || run === undefined || entry === undefined) {
      return;
    }
    renderShip(ship, entry, experiment.problem);
    renderInfo(experiment, run, timeline, index);
    renderHistoryChart(run, entry.iteration);
  }

  function selectRun(): void {
    run = experiment?.runs[runSelect.selectedIndex];
    if (run === undefined) {
      return;
    }
    timeline = buildStateTimeline(run);
    index = 0;
    render();
  }

  async function selectFile(): Promise<void> {
    const entry = files[fileSelect.selectedIndex];
    if (entry === undefined) {
      return;
    }
    experiment = await loadExperiment(entry);
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

if (typeof document !== "undefined") {
  void main();
}
