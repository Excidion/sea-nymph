from __future__ import annotations

import math

import narwhals as nw

from seanymph._utils import resolve_palette
from seanymph.mermaidplotlib.xychart import XYChart


def _silverman_bandwidth(values: list[float]) -> float:
    n = len(values)
    mean = sum(values) / n
    std = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1))
    return 1.06 * std * n**-0.2


def _gaussian_kde(
    grid: list[float], values: list[float], bandwidth: float
) -> list[float]:
    scale = 1.0 / (len(values) * bandwidth * math.sqrt(2 * math.pi))
    return [
        scale * sum(math.exp(-0.5 * ((xi - v) / bandwidth) ** 2) for v in values)
        for xi in grid
    ]


@nw.narwhalify
def kdeplot(
    data,
    *,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    hue_order: list | None = None,
    bw_adjust: float = 1.0,
    cut: float = 3.0,
    gridsize: int = 200,
    color: str | None = None,
    palette=None,
) -> XYChart:
    if (x is None) == (y is None):
        raise ValueError("exactly one of x or y must be provided")
    if gridsize < 2:
        raise ValueError(f"gridsize must be at least 2, got {gridsize}")

    horizontal = y is not None
    num_col = y if horizontal else x

    for col in [num_col] + ([hue] if hue else []):
        if col not in data.columns:
            raise ValueError(f"Column {col!r} not found in data")

    all_values = [float(v) for v in data[num_col].to_list()]
    bandwidth = _silverman_bandwidth(all_values) * bw_adjust

    lo = min(all_values) - cut * bandwidth
    hi = max(all_values) + cut * bandwidth
    step = (hi - lo) / (gridsize - 1)
    grid = [lo + i * step for i in range(gridsize)]

    levels = hue_order or (list(dict.fromkeys(data[hue].to_list())) if hue else [None])
    colors = resolve_palette(palette, levels, color)

    chart = XYChart()
    for level, c in zip(levels, colors):
        level_values = (
            [float(v) for v in data.filter(nw.col(hue) == level)[num_col].to_list()]
            if level is not None
            else all_values
        )
        bw = _silverman_bandwidth(level_values) * bw_adjust
        densities = _gaussian_kde(grid, level_values, bw)
        if horizontal:
            chart.lineh(grid, densities, color=c)
        else:
            chart.line(grid, densities, color=c)

    if horizontal:
        chart.xlabel("Density")
        chart.ylabel(num_col)
    else:
        chart.xlabel(num_col)
        chart.ylabel("Density")

    return chart
