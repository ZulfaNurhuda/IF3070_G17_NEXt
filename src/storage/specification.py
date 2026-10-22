import random
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

ATTRIBUTE_KEYS: Final = ("width", "length", "shipping_fee", "weight", "eta")
IDENTIFIER_KEY: Final = "id"


@dataclass(frozen=True, slots=True)
class IntegerRange:
    low: int
    high: int

    def draw(self, rng: random.Random) -> int:
        return rng.randint(self.low, self.high)


@dataclass(frozen=True, slots=True)
class VehicleSpecification:
    number: int | None
    ranges: Mapping[str, IntegerRange]


def parse_range(text: str, owner: str) -> IntegerRange:
    low_text, separator, high_text = text.partition(":")
    try:
        low = int(low_text)
        high = int(high_text) if separator else low
    except ValueError:
        raise ValueError(f"{owner}: '{text}' harus berbentuk n atau rendah:tinggi") from None
    if low <= 0 or high < low:
        raise ValueError(f"{owner}: '{text}' harus bilangan bulat positif dengan rendah <= tinggi")
    return IntegerRange(low, high)


def parse_vehicle_specification(text: str, index: int) -> VehicleSpecification:
    owner = f"--vehicle ke-{index}"
    number: int | None = None
    ranges: dict[str, IntegerRange] = {}
    for pair in text.split(","):
        key, separator, value = pair.partition("=")
        if not separator:
            raise ValueError(f"{owner}: '{pair}' harus berbentuk nama=nilai")
        if key == IDENTIFIER_KEY:
            if number is not None:
                raise ValueError(f"{owner}: kunci {key} diberikan lebih dari sekali")
            parsed = parse_range(value, f"{owner} {key}")
            if parsed.low != parsed.high:
                raise ValueError(f"{owner}: {key} harus berupa satu bilangan, bukan rentang")
            number = parsed.low
        elif key in ATTRIBUTE_KEYS:
            if key in ranges:
                raise ValueError(f"{owner}: kunci {key} diberikan lebih dari sekali")
            ranges[key] = parse_range(value, f"{owner} {key}")
        else:
            valid_keys = ", ".join((IDENTIFIER_KEY, *ATTRIBUTE_KEYS))
            raise ValueError(f"{owner}: kunci tidak dikenal '{key}'; pilihan: {valid_keys}")
    return VehicleSpecification(number, ranges)
