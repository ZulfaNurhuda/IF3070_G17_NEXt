import type { ExperimentPayload, FileEntry } from "./types";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isFileEntry(value: unknown): value is FileEntry {
  return (
    isRecord(value) &&
    typeof value.name === "string" &&
    typeof value.folder === "string" &&
    typeof value.created_at === "string"
  );
}

function isState(value: unknown): boolean {
  return isRecord(value) && Array.isArray(value.placements) && typeof value.value === "number";
}

function isRun(value: unknown): boolean {
  return (
    isRecord(value) &&
    isState(value.initial_state) &&
    isState(value.final_state) &&
    Array.isArray(value.history) &&
    Array.isArray(value.steps) &&
    isRecord(value.extra)
  );
}

function isExperiment(value: unknown): value is ExperimentPayload {
  return (
    isRecord(value) &&
    isRecord(value.problem) &&
    typeof value.algorithm === "string" &&
    isRecord(value.params) &&
    Array.isArray(value.runs) &&
    value.runs.length > 0 &&
    value.runs.every(isRun)
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
