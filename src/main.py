from __future__ import annotations

from typing import Optional

from src.hinges import get_hinge_series
from src.models import DoorSpec, calculate_boring



def _prompt_float(prompt: str, allow_blank: bool = False) -> Optional[float]:
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            return float(raw)
        except ValueError:
            print("Please enter a numeric value.")

def main() -> None:
    print("Available hinge series: salice_100")

    series_key = input("Enter hinge series key: ").strip()
    series = get_hinge_series(series_key)

    print(f"Using hinge series: {series.display_name}")
    print(f"Supported door thickness range: {series.min_door_thickness_mm}-"
          f"{series.max_door_thickness_mm} mm")
    print(f"Allowed K range: {series.min_k_mm}-{series.max_k_mm} mm\n")

    thickness = _prompt_float("Door thickness T (mm): ")
    height = _prompt_float("Door height (mm) [optional, press Enter to skip]: ", allow_blank=True)
    weight = _prompt_float("Door weight (kg) [optional, press Enter to skip]: ", allow_blank=True)
    desired_k = _prompt_float(
        f"Boring distance K (mm) [optional, press Enter for default ({series.default_k()} mm)]: ",
        allow_blank=True,
    )

    door = DoorSpec(
        thickness_mm=thickness,
        height_mm=height,
        weight_kg=weight,
        desired_k_mm=desired_k,
    )

    result = calculate_boring(series, door)

    print("\n=== Calculation Result ===")
    print(f"Hinge series:      {result.series_code}")
    print(f"Door thickness:    {result.thickness_mm:.1f} mm")
    print(f"Door height:       {result.height_mm:.1f} mm")
    print(f"Chosen K:          {result.k_mm:.1f} mm")

    print(f"A (inner clear):  {result.a_mm if result.a_mm is not None else 'N/A'} mm")
    print(f"L (outer clear):  {result.l_mm if result.l_mm is not None else 'N/A'} mm")
    print(f"C (max moulding):  {result.c_mm if result.c_mm is not None else 'N/A'} mm")

    if result.recommended_hinge_count is not None:
        print(f"Recommended hinges: {result.recommended_hinge_count}")
    else:
        print("Recommended hinges: N/A (no hinge-count curve defined)")

    if result.warnings:
        print("\nWarnings:")
        for w in result.warnings:
            print(f" - {w}")


if __name__ == "__main__":
    main()
