import re

import pytest
import polars as pl

from sea_nymph import kdeplot


def _df(data: dict):
    return pl.DataFrame(data)


def _data():
    return _df({"x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]})


def _series_values(out: str) -> list[float]:
    return [float(v) for v in re.search(r"line \[([^\]]+)\]", out).group(1).split(", ")]


# ---------------------------------------------------------------------------
# Basic rendering
# ---------------------------------------------------------------------------


class TestBasic:
    def test_basic(self):
        fig = kdeplot(_data(), x="x")
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta\n" in out
        assert "line" in out

    def test_returns_xychart(self):
        from sea_nymph.mermaidplotlib import XYChart

        assert isinstance(kdeplot(_data(), x="x"), XYChart)

    def test_default_gridsize(self):
        fig = kdeplot(_data(), x="x")
        self._figures.append(fig)
        assert len(_series_values(fig.render())) == 200

    def test_custom_gridsize(self):
        fig = kdeplot(_data(), x="x", gridsize=50)
        self._figures.append(fig)
        assert len(_series_values(fig.render())) == 50

    def test_density_non_negative(self):
        fig = kdeplot(_data(), x="x")
        self._figures.append(fig)
        assert all(v >= 0 for v in _series_values(fig.render()))

    def test_bw_adjust_wider(self):
        # higher bw_adjust → smoother/flatter curve → lower peak density
        fig_narrow = kdeplot(_data(), x="x", bw_adjust=0.5, gridsize=50)
        fig_wide = kdeplot(_data(), x="x", bw_adjust=2.0, gridsize=50)
        self._figures.append(fig_narrow)
        self._figures.append(fig_wide)
        peak_narrow = max(_series_values(fig_narrow.render()))
        peak_wide = max(_series_values(fig_wide.render()))
        assert peak_narrow > peak_wide

    def test_axis_labels_vertical(self):
        fig = kdeplot(_data(), x="x", gridsize=20)
        self._figures.append(fig)
        out = fig.render()
        assert '"x"' in out  # column name on x-axis
        assert '"Density"' in out  # density on y-axis

    def test_axis_labels_horizontal(self):
        fig = kdeplot(_data(), y="x", gridsize=20)
        self._figures.append(fig)
        out = fig.render()
        assert '"Density"' in out  # density on horizontal axis
        assert '"x"' in out  # column name on vertical axis

    def test_cut_extends_range(self):
        # cut=0 → grid starts at min(data), cut=3 → grid extends beyond
        fig_no_cut = kdeplot(_data(), x="x", cut=0.0, gridsize=50)
        fig_cut = kdeplot(_data(), x="x", cut=3.0, gridsize=50)
        self._figures.append(fig_no_cut)
        self._figures.append(fig_cut)
        out_no_cut = fig_no_cut.render()
        out_cut = fig_cut.render()
        # x-axis range should be wider with cut=3
        no_cut_range = re.search(r"x-axis [^\n]*?([\d.\-]+) --> ([\d.\-]+)", out_no_cut)
        cut_range = re.search(r"x-axis [^\n]*?([\d.\-]+) --> ([\d.\-]+)", out_cut)
        assert float(no_cut_range.group(1)) > float(cut_range.group(1))


# ---------------------------------------------------------------------------
# Hue
# ---------------------------------------------------------------------------


class TestHue:
    def _data(self):
        return _df(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
                "grp": ["a", "a", "a", "a", "b", "b", "b", "b"],
            }
        )

    def test_hue_two_series(self):
        fig = kdeplot(self._data(), x="x", hue="grp", gridsize=20)
        self._figures.append(fig)
        assert fig.render().count("line") == 2

    def test_hue_order(self):
        fig = kdeplot(self._data(), x="x", hue="grp", hue_order=["b", "a"], gridsize=20)
        self._figures.append(fig)
        out = fig.render()
        # b peaks at higher x than a — first line should have peak later
        lines = re.findall(r"line \[([^\]]+)\]", out)
        b_values = [float(v) for v in lines[0].split(", ")]
        a_values = [float(v) for v in lines[1].split(", ")]
        assert b_values.index(max(b_values)) > a_values.index(max(a_values))

    def test_palette_list(self):
        fig = kdeplot(
            self._data(), x="x", hue="grp", palette=["#ff0000", "#00ff00"], gridsize=20
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000" in out
        assert "#00ff00" in out

    def test_palette_dict(self):
        fig = kdeplot(
            self._data(),
            x="x",
            hue="grp",
            palette={"a": "#aaaaaa", "b": "#bbbbbb"},
            gridsize=20,
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
            kdeplot(_data(), x="z")

    def test_both_x_and_y(self):
        with pytest.raises(ValueError, match="exactly one of x or y"):
            kdeplot(_data(), x="x", y="x")

    def test_neither_x_nor_y(self):
        with pytest.raises(ValueError, match="exactly one of x or y"):
            kdeplot(_data())

    def test_y_horizontal(self):
        fig = kdeplot(_data(), y="x", gridsize=20)
        assert "xychart-beta horizontal" in fig.render()

    def test_gridsize_too_small(self):
        with pytest.raises(ValueError, match="gridsize must be at least 2"):
            kdeplot(_data(), x="x", gridsize=1)
