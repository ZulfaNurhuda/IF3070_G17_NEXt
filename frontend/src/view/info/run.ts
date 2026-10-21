import type { ExperimentPayload, RunPayload } from "../../data/types";
import { byId, textElement } from "../dom";
import { unitLabel } from "../metrics";
import { formatValue } from "./format";

export function renderRunDetails(experiment: ExperimentPayload, run: RunPayload): void {
  byId("unit-label").textContent = unitLabel(run.unit);
  const details: [string, unknown][] = [
    ["algorithm", experiment.algorithm],
    ["objective", experiment.objective],
    ["run", run.run],
    ["seed", run.seed],
    ["duration_seconds", run.duration_seconds],
    ["iterations", run.iterations],
    ["nilai awal", run.initial_state.value],
    ["nilai akhir", run.final_state.value],
    ...Object.entries(experiment.params).map(([key, value]): [string, unknown] =>
      value === null && key in run.extra
        ? [key, `${formatValue(run.extra[key])} (otomatis)`]
        : [key, value],
    ),
    ...Object.entries(run.extra).filter(([key]) => !(key in experiment.params)),
  ];
  byId("details").replaceChildren(
    ...details.map(([key, detail]) => textElement("div", `${key}: ${formatValue(detail)}`)),
  );
}
