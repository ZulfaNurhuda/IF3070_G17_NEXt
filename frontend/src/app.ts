import { loadExperiment, loadFileList } from "./data/api";
import type { ExperimentPayload, FileEntry } from "./data/types";
import { byId, clearMessage, showMessage, textElement } from "./view/dom";
import { createViewer } from "./viewer";

async function main(): Promise<void> {
  const fileSelect = byId<HTMLSelectElement>("file-select");
  const runSelect = byId<HTMLSelectElement>("run-select");
  const viewer = createViewer(byId<SVGSVGElement>("ship"));
  let files: FileEntry[] = [];
  let shown: ExperimentPayload | undefined;
  let latestRequest = 0;
  let shownFile = -1;
  let shownRun = 0;

  function showRun(source: ExperimentPayload, runIndex: number): void {
    viewer.show(source, runIndex);
    clearMessage();
    shown = source;
    shownRun = runIndex;
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
      if (shown !== undefined) {
        showRun(shown, runSelect.selectedIndex);
      }
    } catch (error) {
      runSelect.selectedIndex = shownRun;
      showMessage(error);
    }
  });
  byId("step-first").addEventListener("click", () => viewer.goTo(0));
  byId("step-back").addEventListener("click", () => viewer.move(-1));
  byId("step-next").addEventListener("click", () => viewer.move(1));
  byId("step-last").addEventListener("click", () => viewer.last());

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
