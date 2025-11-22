from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.hinges import HingeSeriesBase



# ---- Shared support types ------------------------------------------------- #

@dataclass
class BoringTables:
    """
    A and L lookup tables for a hinge series.

    Stored as:
        A[thickness_mm][k_mm] -> A (mm)
        L[thickness_mm][k_mm] -> L (mm)

    `c_offset` is the constant in catalogue formulas like:
        C = c_offset + K + A
    """
    a_table: Dict[int, Dict[int, float]] = field(default_factory=dict)
    l_table: Dict[int, Dict[int, float]] = field(default_factory=dict)
    c_offset: float = 0.0

    def get_a(self, thickness_mm: int, k_mm: int) -> Optional[float]:
        return self.a_table.get(thickness_mm, {}).get(k_mm)

    def get_l(self, thickness_mm: int, k_mm: int) -> Optional[float]:
        return self.l_table.get(thickness_mm, {}).get(k_mm)

    def get_c(self, thickness_mm: int, k_mm: int) -> Optional[float]:
        a = self.get_a(thickness_mm, k_mm)
        if a is None:
            return None
        return self.c_offset + k_mm + a


@dataclass
class DoorSpec:
    """Inputs describing a particular door."""
    thickness_mm: float
    height_mm: Optional[float] = None # If None, series will choose default
    weight_kg: Optional[float] = None
    desired_k_mm: Optional[float] = None  # If None, series will choose default


@dataclass
class BoringResult:
    """Output of a boring calculation."""
    series_code: str
    thickness_mm: float
    height_mm: float
    k_mm: float
    a_mm: Optional[float]
    l_mm: Optional[float]
    c_mm: Optional[float]
    recommended_hinge_count: Optional[int]
    warnings: List[str] = field(default_factory=list)


# ---- Generic calculation function that works for any series ------------ #

def calculate_boring(series: "HingeSeriesBase", door: DoorSpec) -> BoringResult:
    """
    Core calculation pipeline shared by all hinge series:
      - validate thickness
      - choose / clamp K
      - look up A/L
      - compute C
      - compute hinge count
    """
    warnings: List[str] = []

    if not series.supports_thickness(door.thickness_mm):
        warnings.append(
            f"Door thickness {door.thickness_mm}mm is outside the supported "
            f"range for series '{series.display_name}'."
        )

    # Decide K
    if door.desired_k_mm is None:
        k_mm = series.default_k()
        warnings.append(
            f"No desired K provided; using series default K = {k_mm}mm."
        )
    else:
        k_mm = series.clamp_k(door.desired_k_mm)
        if k_mm != door.desired_k_mm:
            warnings.append(
                f"Desired K={door.desired_k_mm}mm was clamped to valid range "
                f"[{series.min_k_mm}, {series.max_k_mm}] -> {k_mm}mm."
            )

    # Lookup A, L, C from tables (using rounded thickness/K keys)
    thickness_int = int(round(door.thickness_mm))
    k_int = int(round(k_mm))

    a_mm = series.tables.get_a(thickness_int, k_int)
    l_mm = series.tables.get_l(thickness_int, k_int)
    c_mm = series.tables.get_c(thickness_int, k_int)

    if a_mm is None or l_mm is None:
        warnings.append(
            f"No A/L table entry for T={thickness_int}mm and K={k_int}mm. "
            "You may need to extend the tables for this series."
        )

    if door.height_mm is None:
        door.height_mm = min(h for (h, _) in series.hinge_count_by_height)

    hinge_count = series.recommend_hinge_count(door.height_mm, door.weight_kg)

    return BoringResult(
        series_code=series.code,
        thickness_mm=door.thickness_mm,
        height_mm=door.height_mm,
        k_mm=k_mm,
        a_mm=a_mm,
        l_mm=l_mm,
        c_mm=c_mm,
        recommended_hinge_count=hinge_count,
        warnings=warnings,
        )
