import { join } from "node:path";
import index from "./index.html";
import type { FileEntry } from "./types";

export const OUTPUT_DIRECTORY = join(import.meta.dir, "..", "output");
export const PORT = 3000;

export async function listOutputFiles(): Promise<FileEntry[]> {
  // TODO: Implementasikan pendaftaran file hasil eksperimen.
  //   Telusuri OUTPUT_DIRECTORY/final dan OUTPUT_DIRECTORY/scratch, ambil semua *.json,
  //   dan kembalikan FileEntry {name, folder, created_at}. created_at dibaca dari field
  //   created_at di dalam JSON (fallback ke waktu modifikasi file). Urutkan terbaru dulu.
  //   Bila folder belum ada, anggap kosong (jangan error).
  throw new Error("Belum diimplementasi");
}

export async function serveOutputFile(folder: string, name: string): Promise<Response> {
  // TODO: Implementasikan penyajian satu file hasil eksperimen.
  //   Keamanan: folder hanya boleh "final" atau "scratch", name tidak boleh mengandung
  //   pemisah path atau "..", dan harus berakhiran .json; selain itu balas 400.
  //   Bila file tidak ada balas 404. Selain itu balas isi file dengan content type JSON.
  throw new Error("Belum diimplementasi");
}

Bun.serve({
  port: PORT,
  routes: {
    "/": index,
    "/api/files": async () => Response.json(await listOutputFiles()),
    "/files/:folder/:name": async (request) =>
      serveOutputFile(request.params.folder, request.params.name),
  },
});
