from src.core.models import Change, Move, Orientation, Placement, State, Vehicle


def flipped(orientation: Orientation) -> Orientation:
    if orientation is Orientation.VERTICAL:
        return Orientation.HORIZONTAL
    return Orientation.VERTICAL


def rotation_move(vehicle: Vehicle, state: State) -> Move | None:
    placement = state.placements[vehicle.id]
    if placement is None or vehicle.width == vehicle.length:
        return None
    rotated = Placement(placement.x, placement.y, flipped(placement.orientation))
    return (Change(vehicle.id, placement, rotated),)


def swap_move(first: Vehicle, second: Vehicle, state: State) -> Move | None:
    first_placement = state.placements[first.id]
    second_placement = state.placements[second.id]
    if first_placement == second_placement:
        return None
    return (
        Change(first.id, first_placement, second_placement),
        Change(second.id, second_placement, first_placement),
    )
