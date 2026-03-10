import pytest
import narwhals as nw
import polars as pl

from sea_nymph import barplot


def _df(data: dict):
    return pl.DataFrame(data)


# ---------------------------------------------------------------------------
# DataFrame data (long-form)
# ---------------------------------------------------------------------------


class TestDataFrame:
    def _data(self):
        return _df(
            {
                "group": ["A", "A", "B", "B", "C", "C"],
                "value": [1.0, 3.0, 2.0, 4.0, 5.0, 1.0],
            }
        )

    def test_basic_bar(self):
        fig = barplot(self._data(), x="group", y="value")
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta\n" in out
        assert "horizontal" not in out
        assert "x-axis [A, B, C]" in out
        assert "bar [2, 3, 3]" in out  # (1+3)/2=2, (2+4)/2=3, (5+1)/2=3

    def test_horizontal_via_orient(self):
        fig = barplot(self._data(), x="value", y="group", orient="h")
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta horizontal" in out

    def test_horizontal_inferred_from_categorical_y(self):
        fig = barplot(self._data(), x="value", y="group")
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta horizontal" in out

    def test_order(self):
        fig = barplot(self._data(), x="group", y="value", order=["C", "A", "B"])
        self._figures.append(fig)
        out = fig.render()
        assert "bar [3, 2, 3]" in out

    def test_color(self):
        fig = barplot(self._data(), x="group", y="value", color="#ff0000")
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000" in out

    def test_estimator_sum(self):
        fig = barplot(
            self._data(), x="group", y="value", estimator=nw.col("value").sum()
        )
        self._figures.append(fig)
        out = fig.render()
        assert "bar [4, 6, 6]" in out

    def test_estimator_max(self):
        fig = barplot(
            self._data(), x="group", y="value", estimator=nw.col("value").max()
        )
        self._figures.append(fig)
        out = fig.render()
        assert "bar [3, 4, 5]" in out

    def test_returns_xychart(self):
        from sea_nymph.mermaidplotlib import XYChart

        fig = barplot(self._data(), x="group", y="value")
        assert isinstance(fig, XYChart)


# ---------------------------------------------------------------------------
# Hue — multiple bar series
# ---------------------------------------------------------------------------


class TestHue:
    def _data(self):
        return _df(
            {
                "category": ["X", "Y", "X", "Y"],
                "value": [10.0, 20.0, 30.0, 40.0],
                "group": ["a", "a", "b", "b"],
            }
        )

    def test_hue_produces_two_series(self):
        fig = barplot(self._data(), x="category", y="value", hue="group")
        self._figures.append(fig)
        out = fig.render()
        assert out.count("bar") == 2

    def test_hue_order(self):
        fig = barplot(
            self._data(),
            x="category",
            y="value",
            hue="group",
            hue_order=["b", "a"],
        )
        self._figures.append(fig)
        out = fig.render()
        first_bar = out.index("bar [30")
        second_bar = out.index("bar [10")
        assert first_bar < second_bar

    def test_palette_list(self):
        fig = barplot(
            self._data(),
            x="category",
            y="value",
            hue="group",
            palette=["#ff0000", "#00ff00"],
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000" in out
        assert "#00ff00" in out

    def test_palette_dict(self):
        fig = barplot(
            self._data(),
            x="category",
            y="value",
            hue="group",
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
    def test_bad_orient(self):
        with pytest.raises(ValueError, match="orient must be"):
            barplot(_df({"x": ["A"], "y": [1.0]}), x="x", y="y", orient="diagonal")

    def test_missing_column(self):
        with pytest.raises(ValueError, match="Column 'z' not found"):
            barplot(_df({"x": [1]}), x="z", y="x")
