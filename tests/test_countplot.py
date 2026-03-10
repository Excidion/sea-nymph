import pytest
import polars as pl

from seanymph import countplot


def _df(data: dict):
    return pl.DataFrame(data)


# ---------------------------------------------------------------------------
# DataFrame data
# ---------------------------------------------------------------------------

class TestDataFrame:
    def _data(self):
        return _df({"group": ["A", "A", "B", "B", "B", "C"]})

    def test_basic_count_x(self):
        fig = countplot(self._data(), x="group")
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta\n" in out
        assert "horizontal" not in out
        assert "bar [2, 3, 1]" in out  # A:2, B:3, C:1

    def test_basic_count_y(self):
        fig = countplot(self._data(), y="group")
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta horizontal" in out

    def test_order(self):
        fig = countplot(self._data(), x="group", order=["C", "A", "B"])
        self._figures.append(fig)
        out = fig.render()
        assert "bar [1, 2, 3]" in out

    def test_color(self):
        fig = countplot(self._data(), x="group", color="#ff0000")
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000" in out

    def test_returns_xychart(self):
        from seanymph.mermaidplotlib import XYChart
        fig = countplot(self._data(), x="group")
        assert isinstance(fig, XYChart)


# ---------------------------------------------------------------------------
# Hue
# ---------------------------------------------------------------------------

class TestHue:
    def _data(self):
        return _df({
            "category": ["X", "X", "Y", "Y", "X", "Y"],
            "group":    ["a", "a", "a", "b", "b", "b"],
        })

    def test_hue_produces_two_series(self):
        fig = countplot(self._data(), x="category", hue="group")
        self._figures.append(fig)
        out = fig.render()
        assert out.count("bar") == 2

    def test_hue_order(self):
        fig = countplot(self._data(), x="category", hue="group", hue_order=["b", "a"])
        self._figures.append(fig)
        out = fig.render()
        # b: X→1, Y→2 / a: X→2, Y→1 — b series rendered first
        assert out.index("bar [1, 2]") < out.index("bar [2, 1]")

    def test_palette_list(self):
        fig = countplot(
            self._data(), x="category", hue="group",
            palette=["#ff0000", "#00ff00"],
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000" in out
        assert "#00ff00" in out

    def test_palette_dict(self):
        fig = countplot(
            self._data(), x="category", hue="group",
            palette={"a": "#aaaaaa", "b": "#bbbbbb"},
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#aaaaaa" in out
        assert "#bbbbbb" in out


# ---------------------------------------------------------------------------
# Stat
# ---------------------------------------------------------------------------

class TestStat:
    def _data(self):
        # A:2, B:2, C:2 — 6 total, easy math
        return _df({"group": ["A", "A", "B", "B", "C", "C"]})

    def test_stat_count_default(self):
        fig = countplot(self._data(), x="group")
        self._figures.append(fig)
        assert "bar [2, 2, 2]" in fig.render()

    def test_stat_proportion(self):
        fig = countplot(self._data(), x="group", stat="proportion")
        self._figures.append(fig)
        assert "bar [0.3333" in fig.render()

    def test_stat_probability(self):
        fig = countplot(self._data(), x="group", stat="probability")
        self._figures.append(fig)
        assert "bar [0.3333" in fig.render()

    def test_stat_percent(self):
        fig = countplot(self._data(), x="group", stat="percent")
        self._figures.append(fig)
        assert "bar [33.333" in fig.render()

    def test_stat_axis_label_x(self):
        fig = countplot(self._data(), x="group", stat="percent")
        self._figures.append(fig)
        assert '"Percent"' in fig.render()

    def test_stat_axis_label_y(self):
        fig = countplot(self._data(), y="group", stat="proportion")
        self._figures.append(fig)
        assert '"Proportion"' in fig.render()

    def test_stat_invalid(self):
        with pytest.raises(ValueError, match="stat must be"):
            countplot(self._data(), x="group", stat="mean")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class TestErrors:
    def test_both_x_and_y(self):
        with pytest.raises(ValueError, match="exactly one of x or y"):
            countplot(_df({"g": ["A"]}), x="g", y="g")

    def test_neither_x_nor_y(self):
        with pytest.raises(ValueError, match="exactly one of x or y"):
            countplot(_df({"g": ["A"]}))
