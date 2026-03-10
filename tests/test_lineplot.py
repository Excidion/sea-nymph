import pytest
import narwhals as nw
import polars as pl

from sea_nymph import lineplot


def _df(data: dict):
    return pl.DataFrame(data)


# ---------------------------------------------------------------------------
# DataFrame data (long-form)
# ---------------------------------------------------------------------------

class TestDataFrame:
    def _data(self):
        return _df({"x": ["A", "A", "B", "B", "C", "C"], "y": [1.0, 3.0, 2.0, 4.0, 5.0, 1.0]})

    def test_basic_line(self):
        fig = lineplot(self._data(), x="x", y="y")
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta" in out
        assert "line [2, 3, 3]" in out  # (1+3)/2=2, (2+4)/2=3, (5+1)/2=3

    def test_numeric_x_sorted(self):
        fig = lineplot(_df({"x": [3.0, 1.0, 2.0], "y": [30.0, 10.0, 20.0]}), x="x", y="y")
        self._figures.append(fig)
        out = fig.render()
        assert "line [10, 20, 30]" in out

    def test_estimator_sum(self):
        fig = lineplot(self._data(), x="x", y="y", estimator=nw.col("y").sum())
        self._figures.append(fig)
        out = fig.render()
        assert "line [4, 6, 6]" in out

    def test_color(self):
        fig = lineplot(self._data(), x="x", y="y", color="#ff0000")
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000" in out

    def test_returns_xychart(self):
        from sea_nymph.mermaidplotlib import XYChart
        fig = lineplot(self._data(), x="x", y="y")
        assert isinstance(fig, XYChart)


# ---------------------------------------------------------------------------
# Hue — multiple line series
# ---------------------------------------------------------------------------

class TestHue:
    def _data(self):
        return _df({
            "category": ["X", "Y", "X", "Y"],
            "value": [10.0, 20.0, 30.0, 40.0],
            "group": ["a", "a", "b", "b"],
        })

    def test_hue_produces_two_series(self):
        fig = lineplot(self._data(), x="category", y="value", hue="group")
        self._figures.append(fig)
        out = fig.render()
        assert out.count("line") == 2

    def test_hue_order(self):
        fig = lineplot(
            self._data(), x="category", y="value", hue="group",
            hue_order=["b", "a"],
        )
        self._figures.append(fig)
        out = fig.render()
        assert out.index("line [30") < out.index("line [10")

    def test_palette_list(self):
        fig = lineplot(
            self._data(), x="category", y="value", hue="group",
            palette=["#ff0000", "#00ff00"],
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000" in out
        assert "#00ff00" in out

    def test_palette_dict(self):
        fig = lineplot(
            self._data(), x="category", y="value", hue="group",
            palette={"a": "#aaaaaa", "b": "#bbbbbb"},
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#aaaaaa" in out
        assert "#bbbbbb" in out


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class TestErrors:
    def test_missing_column(self):
        with pytest.raises(ValueError, match="Column 'z' not found"):
            lineplot(_df({"x": [1]}), x="z", y="x")

    def test_uneven_numeric_x_raises(self):
        with pytest.raises(ValueError, match="not evenly spaced"):
            lineplot(_df({"x": [1.0, 2.0, 10.0], "y": [1.0, 2.0, 3.0]}), x="x", y="y")
