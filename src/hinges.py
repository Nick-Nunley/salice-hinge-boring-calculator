from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional, List
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

    You should supply a BoringTables instance populated with A/L/C data
    for this specific series (e.g. 105° version) from the catalogue.
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
                    20: {3: 1.9, 4: 1.8, 5: 1.8, 6: 1.7},
                    },
                l_table = {
                    # thickness_mm: {k_mm: L_value}
                    15: {3: 0.0, 4: 0.4, 5: 1.0, 6: 1.6},
                    16: {3: 0.0, 4: 0.6, 5: 1.0, 6: 1.8},
                    17: {3: 0.0, 4: 0.7, 5: 1.2, 6: 2.0},
                    18: {3: 0.0, 4: 0.9, 5: 1.8, 6: 2.1},
                    19: {3: 0.1, 4: 1.1, 5: 2.0, 6: 2.3},
                    20: {3: 0.3, 4: 1.2, 5: 2.0, 6: 2.5},
                    },
                c_offset=20.5,
                )


        super().__init__(
            code="salice_silentia_100",
            display_name="Salice Silentia+ 100 series (e.g. 105°)",
            opening_angle_deg=105.0,
            min_door_thickness_mm=14.0,
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



# Registering subclass aliases
register_hinge_series("salice_100", SaliceSilentia100Series)
register_hinge_series("salice_silentia_100", SaliceSilentia100Series)
register_hinge_series("100", SaliceSilentia100Series)
