import type { ChangePayload, PlacementPayload, RunPayload } from "./types";

export interface TimelineEntry {
  iteration: number;
  changes: ChangePayload[];
  placements: ReadonlyMap<string, PlacementPayload>;
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
