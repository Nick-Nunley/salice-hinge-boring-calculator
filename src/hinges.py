from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional, List, Iterable
from abc import ABC

from src.models import BoringTables


# ---------------------------------------------------------------------------
# Registry for all hinge series
# ---------------------------------------------------------------------------

HINGE_SERIES_REGISTRY: dict[str, type["HingeSeriesBase"]] = {}

def register_hinge_series(key: str, cls: type["HingeSeriesBase"]):
    """
    Register a hinge series class under a given key.

    Example:
        register_hinge_series("salice_100", SaliceSilentia100Series)
    """
    key = key.lower().strip()
    HINGE_SERIES_REGISTRY[key] = cls


def get_hinge_series(key: str, **kwargs) -> "HingeSeriesBase":
    """
    Retrieve and instantiate the appropriate hinge series by key.

    Example:
        series = get_hinge_series("salice_100")
    """
    key = key.lower().strip()

    if key not in HINGE_SERIES_REGISTRY:
        raise ValueError(
            f"Unknown hinge series '{key}'. "
            f"Available: {list(HINGE_SERIES_REGISTRY.keys())}"
            )

    cls = HINGE_SERIES_REGISTRY[key]
    return cls(**kwargs)


@dataclass
class HingeSeriesBase(ABC):
    """
    Generic hinge series base class.

    Subclasses supply the concrete series values (ranges, tables, etc),
    and can override methods if a particular series has special rules.
    """
    code: str
    display_name: str
    opening_angle_deg: float

    min_door_thickness_mm: float
    max_door_thickness_mm: Optional[float]

    min_k_mm: float
    max_k_mm: float

    cup_diameter_mm: float
    cup_depth_mm: float

    tables: BoringTables

    # Optional hinge-count curve: [(max_height_mm, count), ...]
    hinge_count_by_height: Optional[List[Tuple[float, int]]] = None

    # ---- Shared behavior for all series ---- #

    def supports_thickness(self, thickness_mm: float) -> bool:
        return (
            thickness_mm >= self.min_door_thickness_mm
            and (self.max_door_thickness_mm is None or thickness_mm <= self.max_door_thickness_mm)
        )

    def clamp_k(self, k_mm: float) -> float:
        """Clamp K into the valid range for this series."""
        return max(self.min_k_mm, min(self.max_k_mm, k_mm))

    def default_k(self) -> float:
        """
        Default K if the user doesn't specify one.
        For many series, this might just be the minimum or a 'catalogue standard'.
        Subclasses can override if they want a different default.
        """
        return self.min_k_mm

    def recommend_hinge_count(self, door_height_mm: Optional[float] = None, door_weight_kg: Optional[float] = None) -> Optional[int]:
        """
        Basic piecewise hinge-count recommendation based on height.

        Subclasses can override if they need more complex behavior
        (e.g., weight-dependent tables).
        """
        if not self.hinge_count_by_height:
            return None
        for max_height, count in self.hinge_count_by_height:
            if door_height_mm <= max_height:
                return count
        return self.hinge_count_by_height[-1][1]


@dataclass
class SaliceSilentia100Series(HingeSeriesBase):
    """
    Salice Silentia+ 100 series - typically for thinner doors.
    """

    def __init__(
        self,
        tables: BoringTables = None,
        hinge_count_by_height: Optional[List[Tuple[float, int]]] = None,
        ) -> None:

        # Initialize default boring tables
        if tables is None:
            tables = BoringTables(
                a_table = {
                    # thickness_mm: {k_mm: A_value}
                    15: {3: 1.0, 4: 0.9, 5: 0.9, 6: 0.9},
                    16: {3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0},
                    17: {3: 1.2, 4: 1.2, 5: 1.1, 6: 1.1},
                    18: {3: 1.4, 4: 1.3, 5: 1.2, 6: 1.2},
                    19: {3: 1.6, 4: 1.5, 5: 1.5, 6: 1.4},
                    20: {3: 1.9, 4: 1.8, 5: 1.8, 6: 1.7}
                    },
                l_table = {
                    # thickness_mm: {k_mm: L_value}
                    15: {3: 0.0, 4: 0.4, 5: 1.0, 6: 1.6},
                    16: {3: 0.0, 4: 0.6, 5: 1.0, 6: 1.8},
                    17: {3: 0.0, 4: 0.7, 5: 1.2, 6: 2.0},
                    18: {3: 0.0, 4: 0.9, 5: 1.8, 6: 2.1},
                    19: {3: 0.1, 4: 1.1, 5: 2.0, 6: 2.3},
                    20: {3: 0.3, 4: 1.2, 5: 2.0, 6: 2.5}
                    },
                c_offset=20.5
                )


        super().__init__(
            code="salice_silentia_100",
            display_name="Salice Silentia+ 100 series 105 degree opening angle",
            opening_angle_deg=105.0,
            min_door_thickness_mm=15.0,
            max_door_thickness_mm=20.0,
            min_k_mm=3.0,
            max_k_mm=6.0,
            cup_diameter_mm=35.0,
            cup_depth_mm=12.0,
            tables=tables,
            hinge_count_by_height=(
                hinge_count_by_height
                or [
                    (1000.0, 2),
                    (1500.0, 3),
                    (2200.0, 4),
                    (2800.0, 5),
                ]
            ),
        )


@dataclass
class SaliceSilentia200_94Series(HingeSeriesBase):
    """
    Salice Silentia+ 200 series - typically for standard doors.
    """

    def __init__(
        self,
        tables: BoringTables = None,
        hinge_count_by_height: Optional[List[Tuple[float, int]]] = None,
        ) -> None:

        # Initialize default boring tables
        if tables is None:
            tables = BoringTables(
                a_table = {
                    # thickness_mm: {k_mm: A_value}
                    19: {3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
                    20: {3: 0.2, 4: 0.2, 5: 0.2, 6: 0.2, 7: 0.2, 8: 0.2, 9: 0.2},
                    21: {3: 0.3, 4: 0.3, 5: 0.3, 6: 0.3, 7: 0.3, 8: 0.3, 9: 0.3},
                    22: {3: 0.4, 4: 0.4, 5: 0.4, 6: 0.4, 7: 0.4, 8: 0.4, 9: 0.4},
                    23: {3: 0.5, 4: 0.5, 5: 0.5, 6: 0.5, 7: 0.5, 8: 0.5, 9: 0.5},
                    24: {3: 0.7, 4: 0.7, 5: 0.7, 6: 0.6, 7: 0.6, 8: 0.6, 9: 0.6},
                    25: {3: 0.8, 4: 0.8, 5: 0.8, 6: 0.8, 7: 0.8, 8: 0.8, 9: 0.8},
                    26: {3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 0.9, 9: 0.9},
                    27: {3: 1.6, 4: 1.2, 5: 1.2, 6: 1.2, 7: 1.1, 8: 1.1, 9: 1.1},
                    28: {3: 2.6, 4: 1.9, 5: 1.4, 6: 1.4, 7: 1.3, 8: 1.3, 9: 1.3},
                    29: {3: 3.5, 4: 2.8, 5: 2.2, 6: 1.7, 7: 1.6, 8: 1.6, 9: 1.5},
                    30: {3: 4.5, 4: 3.8, 5: 3.1, 6: 2.6, 7: 2.1, 8: 1.8, 9: 1.8},
                    31: {3: 5.4, 4: 4.7, 5: 4.1, 6: 3.5, 7: 3.0, 8: 2.5, 9: 2.1},
                    32: {3: 6.4, 4: 5.7, 5: 5.0, 6: 4.4, 7: 3.8, 8: 3.3, 9: 2.9},
                    33: {3: 7.4, 4: 6.6, 5: 5.9, 6: 5.3, 7: 4.7, 8: 4.2, 9: 3.7},
                    34: {3: 8.3, 4: 7.6, 5: 6.9, 6: 6.2, 7: 5.6, 8: 5.1, 9: 4.6},
                    35: {3: 9.3, 4: 8.6, 5: 7.8, 6: 7.2, 7: 6.5, 8: 6.0, 9: 5.4}
                    },
                l_table = {
                    # thickness_mm: {k_mm: L_value}
                    19: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    20: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    21: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    22: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    23: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    24: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    25: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    26: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    27: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    28: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    29: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    30: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    31: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    32: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    33: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    34: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3},
                    35: {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.3, 9: 1.3}
                    },
                c_offset=23.0
                )


        super().__init__(
            code="salice_silentia_200_94",
            display_name="Salice Silentia+ 200 series 94 degree opening angle",
            opening_angle_deg=94.0,
            min_door_thickness_mm=19.0,
            max_door_thickness_mm=35.0,
            min_k_mm=3.0,
            max_k_mm=9.0,
            cup_diameter_mm=35.0,
            cup_depth_mm=15.5,
            tables=tables,
            hinge_count_by_height=(
                hinge_count_by_height
                or [
                    (1000.0, 2),
                    (1500.0, 3),
                    (2200.0, 4),
                    (2800.0, 5),
                ]
            ),
        )



# Registering subclass aliases
register_hinge_series("100", SaliceSilentia100Series)
register_hinge_series("200-94", SaliceSilentia200_94Series)


def _range_mid(s: HingeSeriesBase) -> float:
    if s.max_door_thickness_mm is None:
        return s.min_door_thickness_mm
    return 0.5 * (s.min_door_thickness_mm + s.max_door_thickness_mm)


def select_hinge_series_for_thickness(
    thickness_mm: float,
    required_opening_angle_deg: Optional[float] = None,
    ) -> HingeSeriesBase:
    """
    Select the most appropriate hinge series for a given door thickness (and
    optionally a minimum opening angle).

    Currently uses all registered hinge series in HINGE_SERIES_REGISTRY,
    instantiates each with default parameters, and filters by:

      1) supports_thickness(thickness_mm)
      2) opening_angle_deg >= required_opening_angle_deg (if provided)

    If multiple candidates remain, we pick the one whose thickness range
    is 'closest' to the requested thickness (by the midpoint of its range).

    Raises:
        ValueError if no hinge series support the given thickness/angle.
    """
    if not HINGE_SERIES_REGISTRY:
        raise ValueError("No hinge series registered.")

    candidates: list[HingeSeriesBase] = []

    for cls in HINGE_SERIES_REGISTRY.values():
        series = cls()  # uses default tables / hinge-count
        if not series.supports_thickness(thickness_mm):
            continue
        if required_opening_angle_deg is not None:
            if series.opening_angle_deg < required_opening_angle_deg:
                continue
        candidates.append(series)

    if not candidates:
        msg = f"No hinge series supports thickness {thickness_mm}mm"
        if required_opening_angle_deg is not None:
            msg += f" with opening angle >= {required_opening_angle_deg} degrees"
        raise ValueError(msg)

    # Pick the hinge whose thickness range 'center' is closest to requested T
    best = min(
        candidates,
        key=lambda s: abs(_range_mid(s) - thickness_mm),
        )
    return best
