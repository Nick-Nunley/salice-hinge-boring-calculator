from __future__ import annotations

import streamlit as st

from typing import Optional, List

from src.hinges import get_hinge_series, HINGE_SERIES_REGISTRY
from src.models import DoorSpec, calculate_boring


def _parse_required_float(label: str, value: str, errors: List[str]) -> Optional[float]:
    value = value.strip()
    if value == "":
        errors.append(f"{label} is required.")
        return None
    try:
        return float(value)
    except ValueError:
        errors.append(f"{label} must be a number.")
        return None


def _parse_optional_float(label: str, value: str, errors: List[str]) -> Optional[float]:
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        errors.append(f"{label} must be a number if provided.")
        return None


def main() -> None:
    title = "Salice Hinge Boring Calculator"
    st.set_page_config(
        page_title=title,
        page_icon="🪚",
        layout="centered",
        )

    st.title(title)
    st.caption(
        "Tool to calculate boring parameters (T, K -> A, L, C) and "
        "recommended hinge count for Salice Silentia hinges."
    )

    # Sidebar: series selection and metadata
    st.sidebar.header("Hinge series")

    if not HINGE_SERIES_REGISTRY:
        st.sidebar.error(
            "No hinge series registered. Check that series are "
            "imported and registered in `src/hinges.py`."
            )
        st.stop()

    series_keys = sorted(HINGE_SERIES_REGISTRY.keys())
    # Try to default to "100" if present
    default_index = series_keys.index("100") if "100" in series_keys else 0

    series_key = st.sidebar.selectbox(
        "Select hinge series",
        options=series_keys,
        index=default_index,
        )

    # Instantiate the selected series
    series = get_hinge_series(series_key)

    st.sidebar.markdown(f"**Series:** {series.display_name}")
    st.sidebar.markdown(
        f"**Door thickness range:** {series.min_door_thickness_mm}-"
        f"{series.max_door_thickness_mm} mm"
        )
    st.sidebar.markdown(
        f"**Allowed K range:** {series.min_k_mm}-{series.max_k_mm} mm"
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "This is an internal MVP tool. Verify outputs against the Salice "
        "catalogue and shop standards before updating SOPs."
        )

    # Main form for user inputs
    st.markdown("### Door parameters")

    with st.form("boring_form"):
        col1, col2 = st.columns(2)

        with col1:
            thickness_str = st.text_input("Door thickness T (mm)", value="18")
            height_str = st.text_input("Door height (mm) (optional)", value="")
        with col2:
            weight_str = st.text_input("Door weight (kg) (optional)", value="")
            default_k = series.default_k()
            k_str = st.text_input(
                f"Boring distance K (mm) (optional, default {default_k})",
                value="",
                )

        submitted = st.form_submit_button("Calculate boring")

    if not submitted:
        return

    # --- Parse and validate inputs ---
    errors: List[str] = []

    thickness = _parse_required_float("Door thickness T", thickness_str, errors)
    height = _parse_optional_float("Door height", height_str, errors)
    weight = _parse_optional_float("Door weight", weight_str, errors)
    desired_k = _parse_optional_float("Boring distance K", k_str, errors)

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Build DoorSpec
    door = DoorSpec(
        thickness_mm=thickness,  # type: ignore[arg-type]
        height_mm=height,
        weight_kg=weight,
        desired_k_mm=desired_k,
        )

    # Run calculation
    result = calculate_boring(series, door)

    # Display results
    st.markdown("## Results")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Inputs / Derived")
        st.write(f"**Series code:** `{result.series_code}`")
        st.write(f"**Door thickness T:** {result.thickness_mm:.1f} mm")
        st.write(f"**Door height:** {result.height_mm:.1f} mm")
        st.write(f"**Chosen K:** {result.k_mm:.1f} mm")

        if result.recommended_hinge_count is not None:
            st.write(f"**Recommended hinges:** {result.recommended_hinge_count}")
        else:
            st.write("**Recommended hinges:** N/A (no hinge-count curve defined)")

    with col_right:
        st.markdown("### Clearances")
        st.write(
            f"**A (inner clearance):** "
            f"{result.a_mm if result.a_mm is not None else 'N/A'} mm"
            )
        st.write(
            f"**L (outer clearance):** "
            f"{result.l_mm if result.l_mm is not None else 'N/A'} mm"
            )
        st.write(
            f"**C (max moulding thickness):** "
            f"{result.c_mm if result.c_mm is not None else 'N/A'} mm"
            )

    if result.warnings:
        st.markdown("### Warnings")
        for w in result.warnings:
            st.warning(w)

    # Optional: debug panel
    with st.expander("Debug / raw result"):
        st.json(
            {
                "series_code": result.series_code,
                "thickness_mm": result.thickness_mm,
                "height_mm": result.height_mm,
                "k_mm": result.k_mm,
                "a_mm": result.a_mm,
                "l_mm": result.l_mm,
                "c_mm": result.c_mm,
                "recommended_hinge_count": result.recommended_hinge_count,
                "warnings": result.warnings,
            }
        )


if __name__ == "__main__":
    main()
