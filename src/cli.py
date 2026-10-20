from collections.abc import Sequence
from pathlib import Path
from typing import Final

DEFAULT_INSTANCE: Final = Path("src/instances/default.json")
DEFAULT_RUNS: Final = 3
DEFAULT_SEED: Final = 0
DEFAULT_OUTPUT: Final = "scratch"


def main(argv: Sequence[str] | None = None) -> int:
    # TODO: Implementasikan entrypoint CLI dengan argparse.
    #   Subcommand `run`: --algorithm (wajib, kunci REGISTRY), --instance (default
    #   DEFAULT_INSTANCE), --objective (default objectives.DEFAULT_OBJECTIVE_NAME),
    #   --param nama=nilai (boleh diulang), --runs (default DEFAULT_RUNS),
    #   --seed (default DEFAULT_SEED),
    #   --out {scratch,final} (default DEFAULT_OUTPUT). Alur: load_problem, ubah --param ke
    #   tipe field dataclass algoritma terkait (batas luar sistem: validasi dan raise error
    #   yang jelas), create_algorithm, execute_runs, write_experiment ke output/<out>/.
    #   Subcommand `run-all`: --instance, --objective, --seed; menjalankan
    #   orchestrate_official_experiments dan menulis semuanya ke output/final.
    #   Output: exit code 0 bila sukses, tidak nol bila argumen tidak valid.
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
