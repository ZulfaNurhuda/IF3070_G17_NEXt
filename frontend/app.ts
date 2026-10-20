import type {
  ChangePayload,
  ExperimentPayload,
  FileEntry,
  Orientation,
  PlacementPayload,
  ProblemPayload,
  RunPayload,
  VehiclePayload,
} from "./types";

const CELL = 32;
const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

export interface TimelineEntry {
  iteration: number;
  changes: ChangePayload[];
  placements: ReadonlyMap<string, PlacementPayload>;
}

interface ChartLine {
  points: [number, number][];
  color: string;
  dashed?: boolean;
}

function byId<T extends HTMLElement | SVGElement = HTMLElement>(id: string): T {
  const element = document.getElementById(id);
  if (element === null) {
    throw new Error(`Elemen #${id} tidak ada di halaman`);
  }
  return element as T;
}

function isFileEntry(value: unknown): value is FileEntry {
  return (
    typeof value === "object" &&
    value !== null &&
    "name" in value &&
    typeof value.name === "string" &&
    "folder" in value &&
    typeof value.folder === "string" &&
    "created_at" in value &&
    typeof value.created_at === "string"
  );
}

function isExperiment(value: unknown): value is ExperimentPayload {
  return (
    typeof value === "object" &&
    value !== null &&
    "problem" in value &&
    typeof value.problem === "object" &&
    "algorithm" in value &&
    typeof value.algorithm === "string" &&
    "runs" in value &&
    Array.isArray(value.runs) &&
    value.runs.length > 0
  );
}

export async function loadFileList(): Promise<FileEntry[]> {
  const response = await fetch("/api/files");
  if (!response.ok) {
    throw new Error(`Gagal memuat daftar file (HTTP ${response.status})`);
  }
  const data: unknown = await response.json();
  if (!Array.isArray(data) || !data.every(isFileEntry)) {
    throw new Error("Daftar file tidak sesuai format yang diharapkan");
  }
  return data;
}

export async function loadExperiment(entry: FileEntry): Promise<ExperimentPayload> {
  const response = await fetch(`/files/${entry.folder}/${entry.name}`);
  if (!response.ok) {
    throw new Error(`Gagal memuat ${entry.name} (HTTP ${response.status})`);
  }
  const data: unknown = await response.json();
  if (!isExperiment(data)) {
    throw new Error(`${entry.name} bukan file hasil eksperimen yang valid`);
  }
  return data;
}

function samePlacement(left: PlacementPayload | null, right: PlacementPayload | null): boolean {
  if (left === null || right === null) {
    return left === right;
  }
  return left.x === right.x && left.y === right.y && left.orientation === right.orientation;
}

export function buildStateTimeline(run: RunPayload): TimelineEntry[] {
  let placements = new Map<string, PlacementPayload>(
    run.initial_state.placements.map(({ id, x, y, orientation }) => [id, { x, y, orientation }]),
  );
  const timeline: TimelineEntry[] = [{ iteration: 0, changes: [], placements }];
  for (const step of run.steps) {
    const next = new Map(placements);
    for (const change of step.changes) {
      if (!samePlacement(next.get(change.id) ?? null, change.from)) {
        throw new Error(`Step ${step.iteration}: posisi awal ${change.id} tidak cocok dengan data`);
      }
      if (change.to === null) {
        next.delete(change.id);
      } else {
        next.set(change.id, change.to);
      }
    }
    timeline.push({ iteration: step.iteration, changes: step.changes, placements: next });
    placements = next;
  }
  return timeline;
}

function svgElement(
  name: string,
  attributes: Record<string, string | number>,
  text?: string,
): SVGElement {
  const element = document.createElementNS(SVG_NAMESPACE, name);
  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, String(value));
  }
  if (text !== undefined) {
    element.textContent = text;
  }
  return element;
}

function footprint(
  vehicle: VehiclePayload,
  orientation: Orientation,
): { across: number; down: number } {
  if (orientation === "Vertical") {
    return { across: vehicle.width, down: vehicle.length };
  }
  return { across: vehicle.length, down: vehicle.width };
}

export function renderShip(
  svg: SVGSVGElement,
  entry: TimelineEntry,
  problem: ProblemPayload,
): void {
  const { width, length } = problem.ship;
  svg.setAttribute("viewBox", `0 0 ${width * CELL + 2} ${length * CELL + 2}`);
  const children: SVGElement[] = [
    svgElement("rect", {
      x: 1,
      y: 1,
      width: width * CELL,
      height: length * CELL,
      fill: "#fff",
      stroke: "#999",
    }),
  ];
  for (let column = 1; column < width; column++) {
    const x = 1 + column * CELL;
    children.push(
      svgElement("line", { x1: x, y1: 1, x2: x, y2: 1 + length * CELL, stroke: "#e2e2e2" }),
    );
  }
  for (let row = 1; row < length; row++) {
    const y = 1 + row * CELL;
    children.push(
      svgElement("line", { x1: 1, y1: y, x2: 1 + width * CELL, y2: y, stroke: "#e2e2e2" }),
    );
  }
  const changed = new Set(entry.changes.map((change) => change.id));
  problem.vehicles.forEach((vehicle, index) => {
    const placement = entry.placements.get(vehicle.id);
    if (placement === undefined) {
      return;
    }
    const { across, down } = footprint(vehicle, placement.orientation);
    const hue = (index * 47) % 360;
    const left = 1 + placement.x * CELL;
    const top = 1 + placement.y * CELL;
    children.push(
      svgElement("rect", {
        x: left + 2,
        y: top + 2,
        width: across * CELL - 4,
        height: down * CELL - 4,
        rx: 3,
        fill: `hsl(${hue} 70% 85%)`,
        stroke: `hsl(${hue} 50% 30%)`,
        "stroke-width": changed.has(vehicle.id) ? 3 : 1,
      }),
    );
    const fontSize = Math.max(9, Math.min(16, (across * CELL - 6) / (vehicle.id.length * 0.6)));
    children.push(
      svgElement(
        "text",
        {
          x: left + (across * CELL) / 2,
          y: top + (down * CELL) / 2,
          "text-anchor": "middle",
          "dominant-baseline": "central",
          "font-size": fontSize,
          fill: `hsl(${hue} 50% 20%)`,
        },
        vehicle.id,
      ),
    );
  });
  svg.replaceChildren(...children);
}

function niceTop(maximum: number): number {
  if (maximum <= 0) {
    return 1;
  }
  const magnitude = 10 ** Math.floor(Math.log10(maximum));
  return Math.ceil(maximum / magnitude) * magnitude;
}

function drawChart(
  svg: SVGSVGElement,
  lines: ChartLine[],
  marker: number,
  top: number,
  height: number,
): void {
  const width = 640;
  const margin = { left: 44, right: 12, top: 12, bottom: 24 };
  const lastIteration = lines.reduce(
    (largest, line) => line.points.reduce((inner, [x]) => Math.max(inner, x), largest),
    1,
  );
  const toX = (iteration: number): number =>
    margin.left + (iteration / lastIteration) * (width - margin.left - margin.right);
  const toY = (value: number): number =>
    margin.top + (1 - value / top) * (height - margin.top - margin.bottom);
  const label = (x: number, y: number, anchor: string, text: string): SVGElement =>
    svgElement("text", { x, y, "text-anchor": anchor, "font-size": 12, fill: "#666" }, text);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  const children: SVGElement[] = [
    svgElement("line", {
      x1: margin.left,
      y1: toY(0),
      x2: width - margin.right,
      y2: toY(0),
      stroke: "#999",
    }),
  ];
  for (const tick of [0, top / 2, top]) {
    children.push(
      svgElement("line", {
        x1: margin.left,
        y1: toY(tick),
        x2: width - margin.right,
        y2: toY(tick),
        stroke: "#e2e2e2",
      }),
      label(margin.left - 6, toY(tick) + 4, "end", String(Math.round(tick * 100) / 100)),
    );
  }
  for (const line of lines) {
    children.push(
      svgElement("polyline", {
        points: line.points.map(([x, y]) => `${toX(x).toFixed(1)},${toY(y).toFixed(1)}`).join(" "),
        fill: "none",
        stroke: line.color,
        "stroke-width": 2,
        "stroke-dasharray": line.dashed ? "5 4" : "none",
      }),
    );
  }
  children.push(
    svgElement("line", {
      x1: toX(marker),
      y1: margin.top,
      x2: toX(marker),
      y2: toY(0),
      stroke: "#2563eb",
      "stroke-dasharray": "3 3",
    }),
    label(margin.left, height - 6, "start", "0"),
    label(width - margin.right, height - 6, "end", String(lastIteration)),
  );
  svg.replaceChildren(...children);
}

export function renderHistoryChart(run: RunPayload, iteration: number): void {
  const history = run.history;
  const isPopulation = history.some(
    (entry) => entry.maximum_value !== undefined && entry.average_value !== undefined,
  );
  const lines: ChartLine[] = isPopulation
    ? [
        {
          points: history.map((entry) => [entry.iteration, entry.maximum_value ?? entry.value]),
          color: "#2563eb",
        },
        {
          points: history.map((entry) => [entry.iteration, entry.average_value ?? 0]),
          color: "#888",
          dashed: true,
        },
      ]
    : [{ points: history.map((entry) => [entry.iteration, entry.value]), color: "#2563eb" }];
  const largest = Math.max(...lines.flatMap((line) => line.points.map(([, y]) => y)));
  byId("chart-title").textContent = isPopulation
    ? "Nilai maksimum (garis) dan rata-rata (putus-putus) populasi"
    : "Nilai terhadap iterasi";
  drawChart(byId<SVGSVGElement>("history-chart"), lines, iteration, niceTop(largest), 160);
  const probabilities: [number, number][] = history.flatMap((entry) =>
    entry.acceptance_probability === undefined
      ? []
      : [[entry.iteration, entry.acceptance_probability]],
  );
  byId("probability-section").hidden = probabilities.length === 0;
  if (probabilities.length > 0) {
    drawChart(
      byId<SVGSVGElement>("probability-chart"),
      [{ points: probabilities, color: "#d97706" }],
      iteration,
      1,
      110,
    );
  }
}

function describeChange(change: ChangePayload): string {
  const { from, to } = change;
  if (to === null) {
    return `${change.id} keluar dari kapal`;
  }
  const target = `(${to.x}, ${to.y}) ${to.orientation.toLowerCase()}`;
  if (from === null) {
    return `${change.id} masuk ke ${target}`;
  }
  if (from.x === to.x && from.y === to.y) {
    return `${change.id} diputar menjadi ${to.orientation.toLowerCase()}`;
  }
  return `${change.id} pindah ke ${target}`;
}

function formatValue(value: unknown): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : String(Math.round(value * 100) / 100);
  }
  if (typeof value === "object" && value !== null) {
    return JSON.stringify(value);
  }
  return String(value);
}

export function renderInfo(
  experiment: ExperimentPayload,
  run: RunPayload,
  timeline: TimelineEntry[],
  index: number,
): void {
  const entry = timeline[index];
  if (entry === undefined) {
    return;
  }
  const record = run.history.find((item) => item.iteration === entry.iteration);
  const value = index === 0 ? run.initial_state.value : record?.value;
  const weight = experiment.problem.vehicles.reduce(
    (sum, vehicle) => sum + (entry.placements.has(vehicle.id) ? vehicle.weight : 0),
    0,
  );
  const outside = experiment.problem.vehicles
    .filter((vehicle) => !entry.placements.has(vehicle.id))
    .map((vehicle) => vehicle.id);
  let change = "State awal";
  if (index > 0) {
    change =
      entry.changes.length === 0
        ? "Tidak ada perubahan"
        : entry.changes.map(describeChange).join("; ");
  }
  let note = "";
  if (record?.acceptance_probability !== undefined) {
    note = `Peluang penerimaan: ${formatValue(record.acceptance_probability)}`;
  } else if (record?.maximum_value !== undefined && record.average_value !== undefined) {
    note = `Maksimum ${formatValue(record.maximum_value)}, rata-rata ${formatValue(record.average_value)}`;
  }
  byId("unit-label").textContent =
    experiment.algorithm === "genetic-algorithm" ? "Generasi" : "Iterasi";
  byId("iteration").textContent = String(entry.iteration);
  byId("value").textContent = value === undefined ? "-" : formatValue(value);
  byId("weight").textContent = `Berat ${weight} dari ${experiment.problem.ship.max_capacity}`;
  byId("change").textContent = change;
  byId("note").textContent = note;
  byId("outside").textContent = outside.length > 0 ? outside.join(", ") : "Semua terangkut";
  byId("step-label").textContent = `Step ${index} dari ${timeline.length - 1}`;
  const details: [string, unknown][] = [
    ["algorithm", experiment.algorithm],
    ["objective", experiment.objective],
    ["run", run.run],
    ["seed", run.seed],
    ["duration_seconds", run.duration_seconds],
    ["iterations", run.iterations],
    ["nilai awal", run.initial_state.value],
    ["nilai akhir", run.final_state.value],
    ...Object.entries(experiment.params),
    ...Object.entries(run.extra),
  ];
  byId("details").replaceChildren(
    ...details.map(([key, detail]) => {
      const line = document.createElement("div");
      line.textContent = `${key}: ${formatValue(detail)}`;
      return line;
    }),
  );
}

function showMessage(error: unknown): void {
  byId("note").textContent = error instanceof Error ? error.message : String(error);
}

function option(text: string): HTMLOptionElement {
  const element = document.createElement("option");
  element.textContent = text;
  return element;
}

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
