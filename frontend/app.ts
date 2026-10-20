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

export async function loadFileList(): Promise<FileEntry[]> {
  // TODO: Implementasikan pengambilan daftar file hasil eksperimen.
  //   Panggil GET /api/files, validasi bahwa responsnya array FileEntry, dan kembalikan.
  //   Lempar Error berisi status HTTP bila respons tidak ok.
  throw new Error("Belum diimplementasi");
}

export async function loadExperiment(entry: FileEntry): Promise<ExperimentPayload> {
  // TODO: Implementasikan pemuatan satu file eksperimen.
  //   Panggil GET /files/<folder>/<name>, parse JSON, dan kembalikan sebagai
  //   ExperimentPayload. Lempar Error bila respons tidak ok atau bentuk JSON tidak sesuai
  //   types.ts (periksa kunci wajib: problem, algorithm, runs).
  throw new Error("Belum diimplementasi");
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

export function renderHistoryChart(svg: SVGSVGElement, run: RunPayload): void {
  // TODO: Implementasikan plot nilai objective terhadap iterasi dengan SVG.
  //   Sumbu x = history[].iteration, sumbu y = history[].value. Bila ada
  //   acceptance_probability (SA) atau maximum_value dan average_value (GA), gambar
  //   plot tambahan untuk kunci tersebut. Tanpa library eksternal.
  throw new Error("Belum diimplementasi");
}

export function renderInfo(
  container: HTMLElement,
  experiment: ExperimentPayload,
  run: RunPayload,
): void {
  // TODO: Implementasikan panel informasi.
  //   Tampilkan algorithm, objective, params, run, seed, duration_seconds, iterations,
  //   nilai initial_state dan final_state, serta seluruh pasangan kunci-nilai di run.extra.
  throw new Error("Belum diimplementasi");
}

export async function main(): Promise<void> {
  // TODO: Implementasikan inisialisasi halaman.
  //   Isi #file-select dari loadFileList, isi #run-select saat file dipilih, panggil
  //   buildStateTimeline saat run dipilih, hubungkan tombol #step-back dan #step-next ke
  //   indeks timeline (batasi 0..panjang-1), lalu render ulang renderShip, renderInfo, dan
  //   renderHistoryChart pada setiap perubahan pilihan atau step.
  throw new Error("Belum diimplementasi");
}

if (typeof document !== "undefined") {
  void main();
}
