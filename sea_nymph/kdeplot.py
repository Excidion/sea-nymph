from __future__ import annotations

import math

import narwhals as nw

from sea_nymph._utils import resolve_palette
from sea_nymph.mermaidplotlib.xychart import XYChart


def _silverman_bandwidth(data, col: str, bw_adjust: float) -> float:
    n = len(data)
    return 1.06 * float(data[col].std()) * n**-0.2 * bw_adjust


def _gaussian_kde(data, col: str, grid: list[float], bandwidth: float) -> list[float]:
    n = len(data)
    scale = 1.0 / (n * bandwidth * math.sqrt(2 * math.pi))
    return [
        data.select(((-0.5 * ((nw.col(col) - xi) / bandwidth) ** 2).exp()).sum().alias("k"))["k"][0]
        * scale
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

    global_bw = _silverman_bandwidth(data, num_col, bw_adjust)
    lo = float(data[num_col].min()) - cut * global_bw
    hi = float(data[num_col].max()) + cut * global_bw
    step = (hi - lo) / (gridsize - 1)
    grid = [lo + i * step for i in range(gridsize)]

    levels = hue_order or (list(dict.fromkeys(data[hue].to_list())) if hue else [None])
    colors = resolve_palette(palette, levels, color)

    chart = XYChart()
    for level, c in zip(levels, colors):
        sub = data.filter(nw.col(hue) == level) if level is not None else data
        bw = _silverman_bandwidth(sub, num_col, bw_adjust)
        densities = _gaussian_kde(sub, num_col, grid, bw)
        if horizontal:
            chart.lineh(grid, densities, color=c)
        else:
            chart.line(grid, densities, color=c)

    if horizontal:
        chart.xlabel("Density").ylabel(num_col)
    else:
        chart.xlabel(num_col).ylabel("Density")

    return chart
