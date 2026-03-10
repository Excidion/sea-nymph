import re

import pytest
import polars as pl

from seanymph import histplot


def _df(data: dict):
    return pl.DataFrame(data)


def _data():
    # 10 values: 4 in [0,1), 3 in [1,2), 3 in [2,3)
    return _df({"x": [0.1, 0.2, 0.5, 0.9, 1.1, 1.5, 1.8, 2.0, 2.5, 2.9]})


# ---------------------------------------------------------------------------
# Basic rendering
# ---------------------------------------------------------------------------

class TestBasic:
    def test_basic_x(self):
        fig = histplot(_data(), x="x", bins=3)
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta\n" in out
        assert "horizontal" not in out
        assert "bar" in out

    def test_basic_y_horizontal(self):
        fig = histplot(_data(), y="x", bins=3)
        self._figures.append(fig)
        assert "xychart-beta horizontal" in fig.render()

    def test_bin_count_matches(self):
        fig = histplot(_data(), x="x", bins=3)
        self._figures.append(fig)
        values = re.search(r"bar \[([^\]]+)\]", fig.render()).group(1).split(", ")
        assert len(values) == 3

    def test_correct_counts(self):
        df = _df({"x": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]})
        fig = histplot(df, x="x", bins=3, binrange=(0.0, 3.0))
        self._figures.append(fig)
        assert "bar [2, 2, 2]" in fig.render()

    def test_returns_xychart(self):
        from seanymph.mermaidplotlib import XYChart
        assert isinstance(histplot(_data(), x="x", bins=3), XYChart)


# ---------------------------------------------------------------------------
# Bins
# ---------------------------------------------------------------------------

class TestBins:
    def test_bins_int(self):
        fig = histplot(_data(), x="x", bins=5)
        self._figures.append(fig)
        values = re.search(r"bar \[([^\]]+)\]", fig.render()).group(1).split(", ")
        assert len(values) == 5

    def test_bins_sequence_equal(self):
        fig = histplot(_data(), x="x", bins=[0.0, 1.0, 2.0, 3.0])
        self._figures.append(fig)
        values = re.search(r"bar \[([^\]]+)\]", fig.render()).group(1).split(", ")
        assert len(values) == 3

    def test_bins_sequence_unequal_raises(self):
        with pytest.raises(ValueError, match="not equally spaced"):
            histplot(_data(), x="x", bins=[0.0, 1.0, 3.0, 6.0])

    def test_binwidth(self):
        df = _df({"x": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]})
        fig = histplot(df, x="x", binwidth=1.0, binrange=(0.0, 3.0))
        self._figures.append(fig)
        values = re.search(r"bar \[([^\]]+)\]", fig.render()).group(1).split(", ")
        assert len(values) == 3

    def test_binrange(self):
        df = _df({"x": [0.5, 1.5, 5.0]})
        fig = histplot(df, x="x", bins=2, binrange=(0.0, 2.0))
        self._figures.append(fig)
        assert "bar [1, 1]" in fig.render()  # 5.0 is outside range

    def test_discrete(self):
        df = _df({"x": [1, 1, 2, 3, 3, 3]})
        fig = histplot(df, x="x", discrete=True)
        self._figures.append(fig)
        assert "bar [2, 1, 3]" in fig.render()


# ---------------------------------------------------------------------------
# Stat
# ---------------------------------------------------------------------------

class TestStat:
    def _data(self):
        # 10 values, 2 bins of width 1: bin0=[0,1) has 4, bin1=[1,2) has 6
        return _df({"x": [0.1, 0.2, 0.5, 0.9, 1.1, 1.2, 1.5, 1.6, 1.8, 1.9]})

    def test_stat_count(self):
        fig = histplot(self._data(), x="x", bins=2, binrange=(0.0, 2.0))
        self._figures.append(fig)
        assert "bar [4, 6]" in fig.render()

    def test_stat_probability(self):
        fig = histplot(self._data(), x="x", bins=2, binrange=(0.0, 2.0), stat="probability")
        self._figures.append(fig)
        assert "bar [0.4, 0.6]" in fig.render()

    def test_stat_proportion(self):
        fig = histplot(self._data(), x="x", bins=2, binrange=(0.0, 2.0), stat="proportion")
        self._figures.append(fig)
        assert "bar [0.4, 0.6]" in fig.render()

    def test_stat_percent(self):
        fig = histplot(self._data(), x="x", bins=2, binrange=(0.0, 2.0), stat="percent")
        self._figures.append(fig)
        assert "bar [40, 60]" in fig.render()

    def test_stat_frequency(self):
        # frequency = count / binwidth; binwidth=1 so same as count
        fig = histplot(self._data(), x="x", bins=2, binrange=(0.0, 2.0), stat="frequency")
        self._figures.append(fig)
        assert "bar [4, 6]" in fig.render()

    def test_stat_density(self):
        # density = count / (n * binwidth) = count / (10 * 1)
        fig = histplot(self._data(), x="x", bins=2, binrange=(0.0, 2.0), stat="density")
        self._figures.append(fig)
        assert "bar [0.4, 0.6]" in fig.render()

    def test_stat_invalid(self):
        with pytest.raises(ValueError, match="stat must be"):
            histplot(self._data(), x="x", stat="mean")


# ---------------------------------------------------------------------------
# Hue
# ---------------------------------------------------------------------------

class TestHue:
    def _data(self):
        return _df({
            "x":   [0.5, 0.5, 1.5, 1.5, 0.5, 1.5],
            "grp": ["a", "a", "a", "b", "b", "b"],
        })

    def test_hue_two_series(self):
        fig = histplot(self._data(), x="x", bins=2, binrange=(0.0, 2.0), hue="grp")
        self._figures.append(fig)
        assert fig.render().count("bar") == 2

    def test_hue_order(self):
        fig = histplot(
            self._data(), x="x", bins=2, binrange=(0.0, 2.0),
            hue="grp", hue_order=["b", "a"],
        )
        self._figures.append(fig)
        out = fig.render()
        # b: bin0=1, bin1=2  /  a: bin0=2, bin1=1 — b first
        assert out.index("bar [1") < out.index("bar [2")

    def test_palette_list(self):
        fig = histplot(
            self._data(), x="x", bins=2, binrange=(0.0, 2.0),
            hue="grp", palette=["#ff0000", "#00ff00"],
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000" in out
        assert "#00ff00" in out


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class TestErrors:
    def test_both_x_and_y(self):
        with pytest.raises(ValueError, match="exactly one of x or y"):
            histplot(_data(), x="x", y="x")

    def test_neither_x_nor_y(self):
        with pytest.raises(ValueError, match="exactly one of x or y"):
            histplot(_data())

    def test_missing_column(self):
        with pytest.raises(ValueError, match="Column 'z' not found"):
            histplot(_data(), x="z")
