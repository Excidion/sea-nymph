from __future__ import annotations

import narwhals as nw

from sea_nymph._utils import resolve_palette
from sea_nymph.mermaidplotlib.xychart import XYChart

_VALID_STATS = ("count", "frequency", "probability", "proportion", "percent", "density")


def _compute_bin_edges(
    data,
    num_col: str,
    bins,
    binwidth: float | None,
    binrange: tuple | None,
    discrete: bool,
) -> list[float]:
    if discrete:
        unique_vals = data[num_col].unique().sort().to_list()
        return [v - 0.5 for v in unique_vals] + [unique_vals[-1] + 0.5]

    lo = float(binrange[0]) if binrange else float(data[num_col].min())
    hi = float(binrange[1]) if binrange else float(data[num_col].max())

    if not isinstance(bins, int):
        edges = [float(e) for e in bins]
        if len(edges) > 2:
            gaps = [edges[i + 1] - edges[i] for i in range(len(edges) - 1)]
            if max(gaps) - min(gaps) > 1e-9 * abs(edges[-1] - edges[0]):
                raise ValueError(
                    f"Bin edges are not equally spaced: {edges}. "
                    "Mermaid xychart places bars equidistantly, which would misrepresent unequal-width bins."
                )
        return edges

    n = bins if binwidth is None else max(1, round((hi - lo) / binwidth))
    width = (hi - lo) / n
    return [lo + i * width for i in range(n + 1)]


def _fmt(v: float) -> str:
    return str(int(v)) if v == int(v) else str(v)


@nw.narwhalify
def histplot(
    data,
    *,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    hue_order: list | None = None,
    stat: str = "count",
    bins: int | list = 10,
    binwidth: float | None = None,
    binrange: tuple | None = None,
    discrete: bool = False,
    color: str | None = None,
    palette=None,
) -> XYChart:
    if (x is None) == (y is None):
        raise ValueError("exactly one of x or y must be provided")
    if stat not in _VALID_STATS:
        raise ValueError(f"stat must be one of {_VALID_STATS}, got {stat!r}")

    horizontal = y is not None
    num_col = y if horizontal else x

    for col in [num_col] + ([hue] if hue else []):
        if col not in data.columns:
            raise ValueError(f"Column {col!r} not found in data")

    edges = _compute_bin_edges(data, num_col, bins, binwidth, binrange, discrete)
    n_bins = len(edges) - 1
    binw = edges[1] - edges[0]
    lo, hi = edges[0], edges[-1]
    total_n = len(data)

    bin_labels = [_fmt(edges[i] + 0.5 if discrete else edges[i]) for i in range(n_bins)]

    counts_df = (
        data.lazy()
        .filter(nw.col(num_col).is_between(lo, hi))
        .with_columns(
            ((nw.col(num_col) - lo) / binw)
            .floor()
            .cast(nw.Int32())
            .clip(0, n_bins - 1)
            .alias("__bin__")
        )
        .group_by(["__bin__"] + ([hue] if hue else []))
        .agg(nw.len().alias("__count__"))
        .collect()
    )

    levels = hue_order or (list(dict.fromkeys(data[hue].to_list())) if hue else [None])
    colors = resolve_palette(palette, levels, color)

    chart = XYChart()
    for level, c in zip(levels, colors):
        sub = counts_df.filter(nw.col(hue) == level) if level is not None else counts_df
        bin_to_count = dict(zip(sub["__bin__"].to_list(), sub["__count__"].to_list()))
        counts = [bin_to_count.get(i, 0) for i in range(n_bins)]

        if stat == "count":
            heights = [float(n) for n in counts]
        elif stat == "frequency":
            heights = [n / binw for n in counts]
        elif stat in ("probability", "proportion"):
            heights = [n / total_n for n in counts]
        elif stat == "percent":
            heights = [n / total_n * 100 for n in counts]
        elif stat == "density":
            heights = [n / (total_n * binw) for n in counts]

        if horizontal:
            chart.barh(bin_labels, heights, color=c)
        else:
            chart.bar(bin_labels, heights, color=c)

    return chart
