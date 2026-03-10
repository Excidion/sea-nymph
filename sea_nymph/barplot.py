from __future__ import annotations

import narwhals as nw

from sea_nymph._utils import resolve_palette
from sea_nymph.mermaidplotlib.xychart import XYChart


@nw.narwhalify
def barplot(
    data,
    *,
    x: str,
    y: str,
    hue: str | None = None,
    order: list | None = None,
    hue_order: list | None = None,
    estimator: nw.Expr | None = None,
    orient: str | None = None,
    color: str | None = None,
    palette=None,
) -> XYChart:
    if orient in ("h", "y"):
        horizontal = True
    elif orient in ("v", "x"):
        horizontal = False
    elif orient is None:
        horizontal = not data.schema[y].is_numeric()
    else:
        raise ValueError("orient must be 'v', 'h', 'x', or 'y'")

    cat_col, num_col = (y, x) if horizontal else (x, y)

    for col in [cat_col, num_col] + ([hue] if hue else []):
        if col not in data.columns:
            raise ValueError(f"Column {col!r} not found in data")

    agg_expr = estimator if estimator is not None else nw.col(num_col).mean()
    group_cols = [cat_col, hue] if hue else [cat_col]
    cats = list(order) if order else data[cat_col].unique(maintain_order=True).to_list()

    # Stay lazy through the aggregation, collect once on the small result
    result = data.lazy().group_by(group_cols).agg(agg_expr).collect()
    levels = hue_order or (data[hue].unique(maintain_order=True).to_list() if hue else [None])
    colors = resolve_palette(palette, levels, color)

    chart = XYChart()
    for level, c in zip(levels, colors):
        sub = result.filter(nw.col(hue) == level) if level is not None else result
        lookup = dict(zip(sub[cat_col].to_list(), sub[num_col].to_list()))
        heights = [lookup[cat] for cat in cats]
        chart.barh(cats, heights, color=c) if horizontal else chart.bar(cats, heights, color=c)

    return chart


