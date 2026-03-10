from __future__ import annotations

import narwhals as nw

from sea_nymph._utils import resolve_palette
from sea_nymph.mermaidplotlib.xychart import XYChart


@nw.narwhalify
def lineplot(
    data,
    *,
    x: str,
    y: str,
    hue: str | None = None,
    hue_order: list | None = None,
    estimator: nw.Expr | None = None,
    color: str | None = None,
    palette=None,
) -> XYChart:
    for col in [x, y] + ([hue] if hue else []):
        if col not in data.columns:
            raise ValueError(f"Column {col!r} not found in data")

    agg_expr = estimator if estimator is not None else nw.col(y).mean()
    group_cols = [x, hue] if hue else [x]
    numeric_x = data.schema[x].is_numeric()

    if numeric_x:
        result = data.lazy().group_by(group_cols).agg(agg_expr).sort(x).collect()
        xs = list(dict.fromkeys(result[x].to_list()))
    else:
        result = data.lazy().group_by(group_cols).agg(agg_expr).collect()
        xs = list(dict.fromkeys(data[x].to_list()))

    levels = hue_order or (list(dict.fromkeys(result[hue].to_list())) if hue else [None])
    colors = resolve_palette(palette, levels, color)

    chart = XYChart()
    for level, c in zip(levels, colors):
        sub = result.filter(nw.col(hue) == level) if level is not None else result
        lookup = dict(zip(sub[x].to_list(), sub[y].to_list()))
        chart.line(xs, [lookup[xi] for xi in xs], color=c)

    return chart


