from collections.abc import Sequence
from typing import get_args

from src.algorithms.base import Algorithm
from src.algorithms.registry import parameter_types


def convert_parameter(algorithm: str, key: str, text: str, annotation: object) -> object:
    if annotation is Algorithm:
        return text
    candidates = (annotation, *get_args(annotation))
    for number_type in (int, float):
        if number_type in candidates:
            try:
                return number_type(text)
            except ValueError:
                raise ValueError(
                    f"--param {key}: nilai '{text}' bukan {number_type.__name__}"
                ) from None
    raise ValueError(f"--param {key}: tipe parameter {algorithm} tidak didukung")


def parse_parameters(algorithm: str, pairs: Sequence[str]) -> dict[str, object]:
    types = parameter_types(algorithm)
    parameters: dict[str, object] = {}
    for pair in pairs:
        key, separator, text = pair.partition("=")
        if not separator:
            raise ValueError(f"--param harus berbentuk nama=nilai, bukan '{pair}'")
        if key in parameters:
            raise ValueError(f"--param {key}: diberikan lebih dari sekali")
        parameters[key] = (
            convert_parameter(algorithm, key, text, types[key]) if key in types else text
        )
    return parameters
