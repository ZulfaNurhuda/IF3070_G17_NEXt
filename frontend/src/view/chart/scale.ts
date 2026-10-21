import type { HistoryEntry } from "../../data/types";

export type Point = [number, number];
export type Bounds = [number, number];

export interface ChartLine {
  points: Point[];
  className: string;
}

function niceTop(maximum: number): number {
  if (maximum <= 0) {
    return 1;
  }
  const magnitude = 10 ** Math.floor(Math.log10(maximum));
  return Math.ceil(maximum / magnitude) * magnitude;
}

export function seriesPoints(history: HistoryEntry[], key: string): Point[] {
  return history.flatMap((entry): Point[] => {
    const value = entry[key];
    return value === undefined ? [] : [[entry.iteration, value]];
  });
}

export function valueBounds(lines: ChartLine[]): Bounds {
  let minimum = 0;
  let maximum = 0;
  for (const line of lines) {
    for (const [, value] of line.points) {
      minimum = Math.min(minimum, value);
      maximum = Math.max(maximum, value);
    }
  }
  const top = maximum > 0 ? niceTop(maximum) : 0;
  const bottom = minimum < 0 ? -niceTop(-minimum) : 0;
  return top === bottom ? [0, 1] : [bottom, top];
}
