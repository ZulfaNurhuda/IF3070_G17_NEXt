import type { ExperimentPayload, FileEntry } from "./types";

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
