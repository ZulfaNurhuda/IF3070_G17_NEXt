import { readdir, stat } from "node:fs/promises";
import { join } from "node:path";
import index from "./index.html";
import type { FileEntry } from "./src/data/types";

const OUTPUT_DIRECTORY = join(import.meta.dir, "..", "output");
const PORT = Number(Bun.env.PORT ?? 3000);

const FOLDERS = ["final", "scratch"];
const SAFE_NAME = /^(?!.*\.\.)[\w.-]+\.json$/;
const TIMESTAMP_IN_NAME = /_(\d+)\.json$/;

async function createdAt(folder: string, name: string): Promise<string> {
  const match = TIMESTAMP_IN_NAME.exec(name);
  if (match?.[1] !== undefined) {
    const stamped = new Date(Number(match[1]) * 1000);
    if (!Number.isNaN(stamped.getTime())) {
      return stamped.toISOString();
    }
  }
  return (await stat(join(OUTPUT_DIRECTORY, folder, name))).mtime.toISOString();
}

async function listOutputFiles(): Promise<FileEntry[]> {
  const entries: FileEntry[] = [];
  for (const folder of FOLDERS) {
    const names = await readdir(join(OUTPUT_DIRECTORY, folder)).catch(() => []);
    for (const name of names) {
      const created = SAFE_NAME.test(name)
        ? await createdAt(folder, name).catch(() => undefined)
        : undefined;
      if (created !== undefined) {
        entries.push({ name, folder, created_at: created });
      }
    }
  }
  return entries.sort((a, b) => b.created_at.localeCompare(a.created_at));
}

async function serveOutputFile(folder: string, name: string): Promise<Response> {
  if (!FOLDERS.includes(folder) || !SAFE_NAME.test(name)) {
    return new Response("Permintaan tidak valid", { status: 400 });
  }
  const file = Bun.file(join(OUTPUT_DIRECTORY, folder, name));
  if (!(await file.exists())) {
    return new Response("File tidak ditemukan", { status: 404 });
  }
  return new Response(file, { headers: { "Content-Type": "application/json" } });
}

Bun.serve({
  hostname: "127.0.0.1",
  port: PORT,
  routes: {
    "/": index,
    "/api/files": async () => Response.json(await listOutputFiles()),
    "/files/:folder/:name": async (request) =>
      serveOutputFile(request.params.folder, request.params.name),
  },
});
