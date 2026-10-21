from pathlib import Path
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent.parent
DEFAULT_INSTANCE: Final = PROJECT_ROOT / "src" / "instances" / "default.json"
OUTPUT_ROOT: Final = PROJECT_ROOT / "output"
DEFAULT_OUTPUT: Final = "scratch"
FINAL_OUTPUT: Final = "final"
OUTPUT_FOLDERS: Final = (DEFAULT_OUTPUT, FINAL_OUTPUT)
