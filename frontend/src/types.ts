export type Orientation = "Horizontal" | "Vertical";

export interface ShipPayload {
  width: number;
  length: number;
  max_capacity: number;
}

export interface VehiclePayload {
  id: string;
  width: number;
  length: number;
  shipping_fee: number;
  weight: number;
  eta: number;
}

export interface ProblemPayload {
  ship: ShipPayload;
  vehicles: VehiclePayload[];
}

export interface PlacementPayload {
  x: number;
  y: number;
  orientation: Orientation;
}

export interface PlacedVehiclePayload extends PlacementPayload {
  id: string;
}

export interface StatePayload {
  placements: PlacedVehiclePayload[];
  outside: string[];
  value: number;
  total_shipping_fee: number;
}

export interface ChangePayload {
  id: string;
  from: PlacementPayload | null;
  to: PlacementPayload | null;
}

export interface HistoryEntry {
  iteration: number;
  value: number;
  [metric: string]: number;
}

export interface StepPayload {
  iteration: number;
  changes: ChangePayload[];
}

export interface RunPayload {
  run: number;
  seed: number;
  duration_seconds: number;
  iterations: number;
  unit?: string;
  initial_state: StatePayload;
  final_state: StatePayload;
  history: HistoryEntry[];
  steps: StepPayload[];
  extra: Record<string, number>;
}

export interface ExperimentPayload {
  problem: ProblemPayload;
  algorithm: string;
  objective: string;
  params: Record<string, unknown>;
  created_at: string;
  runs: RunPayload[];
}

export interface FileEntry {
  name: string;
  folder: string;
  created_at: string;
}
