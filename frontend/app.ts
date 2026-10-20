import type {
  ExperimentPayload,
  FileEntry,
  ProblemPayload,
  RunPayload,
  StatePayload,
} from "./types";

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

export function buildStateTimeline(run: RunPayload): StatePayload[] {
  // TODO: Implementasikan pembangunan daftar state untuk next/back step.
  //   Mulai dari run.initial_state; untuk tiap step di run.steps terapkan change.to
  //   (state maju). Hasilnya array state berindeks step 0..steps.length, dihitung sekali
  //   saat run dipilih. Back step cukup mengurangi indeks. Perbarui juga daftar outside
  //   (kendaraan dengan to = null masuk outside, from = null keluar dari outside).
  throw new Error("Belum diimplementasi");
}

export function renderShip(
  canvas: HTMLCanvasElement,
  state: StatePayload,
  problem: ProblemPayload,
): void {
  // TODO: Implementasikan penggambaran grid kapal di canvas.
  //   Gambar grid ship.width x ship.length; tiap kendaraan terangkut digambar sebagai
  //   persegi panjang berlabel id. Footprint: orientation "Vertical" = width searah sumbu x
  //   dan length searah sumbu y; "Horizontal" = ditukar.
  //   Tampilkan daftar kendaraan di luar kapal (state.outside) di samping grid.
  throw new Error("Belum diimplementasi");
}

export function renderHistoryChart(canvas: HTMLCanvasElement, run: RunPayload): void {
  // TODO: Implementasikan plot nilai objective terhadap iterasi dengan canvas.
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

main();
