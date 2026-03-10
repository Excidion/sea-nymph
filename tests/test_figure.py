import pytest

from seanymph.mermaidplotlib import XYChart


# ---------------------------------------------------------------------------
# Categorical x — vertical
# ---------------------------------------------------------------------------

class TestCategoricalVertical:
    x = ["A", "B", "C"]
    y = [1.0, 2.0, 3.0]

    def test_bar(self):
        fig = XYChart().bar(self.x, self.y)
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta\n" in out
        assert "horizontal" not in out
        assert "x-axis [A, B, C]" in out
        assert "bar [1, 2, 3]" in out

    def test_line(self):
        fig = XYChart().line(self.x, self.y)
        self._figures.append(fig)
        out = fig.render()
        assert "horizontal" not in out
        assert "x-axis [A, B, C]" in out
        assert "line [1, 2, 3]" in out

    def test_bar_and_line(self):
        fig = XYChart().bar(self.x, self.y).line(self.x, [4.0, 5.0, 6.0])
        self._figures.append(fig)
        out = fig.render()
        assert "x-axis [A, B, C]" in out
        assert "bar [1, 2, 3]" in out
        assert "line [4, 5, 6]" in out

    def test_multiword_labels_are_quoted(self):
        fig = XYChart().bar(["Cat One", "Cat Two"], [1.0, 2.0])
        self._figures.append(fig)
        out = fig.render()
        assert '"Cat One"' in out
        assert '"Cat Two"' in out

    def test_xlabel_appears_before_brackets(self):
        fig = XYChart().bar(self.x, self.y).xlabel("Group")
        self._figures.append(fig)
        out = fig.render()
        assert 'x-axis "Group" [A, B, C]' in out

    def test_ylabel_and_ylim(self):
        fig = XYChart().bar(self.x, self.y).ylabel("Count").ylim(0, 10)
        self._figures.append(fig)
        out = fig.render()
        assert 'y-axis "Count" 0 --> 10' in out

    def test_ylabel_without_ylim(self):
        fig = XYChart().bar(self.x, self.y).ylabel("Count")
        self._figures.append(fig)
        out = fig.render()
        assert 'y-axis "Count"' in out
        assert "-->" not in out

    def test_title(self):
        fig = XYChart(title="My Chart").bar(self.x, self.y)
        self._figures.append(fig)
        out = fig.render()
        assert 'title "My Chart"' in out

    def test_title_method(self):
        fig = XYChart().bar(self.x, self.y).title("My Chart")
        self._figures.append(fig)
        out = fig.render()
        assert 'title "My Chart"' in out

    def test_series_order_preserved(self):
        fig = XYChart().bar(self.x, self.y).line(self.x, [4.0, 5.0, 6.0])
        self._figures.append(fig)
        out = fig.render()
        assert out.index("bar") < out.index("line")


# ---------------------------------------------------------------------------
# Categorical x — horizontal
# ---------------------------------------------------------------------------

class TestCategoricalHorizontal:
    x = ["A", "B", "C"]
    y = [1.0, 2.0, 3.0]

    def test_barh(self):
        fig = XYChart().barh(self.x, self.y)
        self._figures.append(fig)
        out = fig.render()
        assert out.startswith("xychart-beta horizontal")
        assert "x-axis [A, B, C]" in out
        assert "bar [1, 2, 3]" in out

    def test_barh_and_line(self):
        fig = XYChart().barh(self.x, self.y).line([4.0, 5.0, 6.0], self.x)
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta horizontal" in out
        assert "bar [1, 2, 3]" in out
        assert "line [4, 5, 6]" in out

    def test_ylabel_with_barh(self):
        fig = XYChart().barh(self.x, self.y).ylabel("Group")
        self._figures.append(fig)
        out = fig.render()
        assert 'x-axis "Group" [A, B, C]' in out

    def test_xlabel_with_barh(self):
        fig = XYChart().barh(self.x, self.y).xlabel("Value").xlim(0, 5)
        self._figures.append(fig)
        out = fig.render()
        assert 'y-axis "Value" 0 --> 5' in out

    def test_lineh(self):
        fig = XYChart().lineh(self.x, self.y)
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta horizontal" in out
        assert "x-axis [A, B, C]" in out
        assert "line [1, 2, 3]" in out

    def test_barh_and_lineh(self):
        fig = XYChart().barh(self.x, self.y).lineh(self.x, [4.0, 5.0, 6.0])
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta horizontal" in out
        assert "bar [1, 2, 3]" in out
        assert "line [4, 5, 6]" in out


# ---------------------------------------------------------------------------
# Numeric x — vertical
# ---------------------------------------------------------------------------

class TestNumericVertical:
    x = [0, 1, 2, 3]
    y = [0.0, 1.0, 4.0, 9.0]

    def test_bar_numeric_range(self):
        fig = XYChart().bar(self.x, self.y)
        self._figures.append(fig)
        out = fig.render()
        assert "horizontal" not in out
        assert "x-axis 0 --> 3" in out
        assert "bar [0, 1, 4, 9]" in out

    def test_line_numeric_range(self):
        fig = XYChart().line(self.x, self.y)
        self._figures.append(fig)
        out = fig.render()
        assert "x-axis 0 --> 3" in out
        assert "line [0, 1, 4, 9]" in out

    def test_bar_and_line_numeric(self):
        fig = XYChart().bar(self.x, self.y).line(self.x, [1.0, 2.0, 3.0, 4.0])
        self._figures.append(fig)
        out = fig.render()
        assert "x-axis 0 --> 3" in out
        assert "bar [0, 1, 4, 9]" in out
        assert "line [1, 2, 3, 4]" in out

    def test_float_x_values(self):
        fig = XYChart().line([0.5, 1.5, 2.5], [10.0, 20.0, 30.0])
        self._figures.append(fig)
        out = fig.render()
        assert "x-axis 0.5 --> 2.5" in out

    def test_xlabel_with_numeric_x(self):
        fig = XYChart().line(self.x, self.y).xlabel("Time")
        self._figures.append(fig)
        out = fig.render()
        assert 'x-axis "Time" 0 --> 3' in out

    def test_xlim_overrides_numeric_x_range(self):
        fig = XYChart().line(self.x, self.y).xlim(0, 10)
        self._figures.append(fig)
        out = fig.render()
        assert "x-axis 0 --> 10" in out

    def test_ylim_with_numeric_x(self):
        fig = XYChart().line(self.x, self.y).ylim(0, 100)
        self._figures.append(fig)
        out = fig.render()
        assert "y-axis 0 --> 100" in out


# ---------------------------------------------------------------------------
# Numeric x — horizontal
# ---------------------------------------------------------------------------

class TestNumericHorizontal:
    x = [10, 20, 30]
    y = [5.0, 15.0, 25.0]

    def test_barh_numeric(self):
        fig = XYChart().barh(self.x, self.y)
        self._figures.append(fig)
        out = fig.render()
        assert out.startswith("xychart-beta horizontal")
        assert "x-axis 10 --> 30" in out
        assert "bar [5, 15, 25]" in out

    def test_barh_and_line_numeric(self):
        fig = XYChart().barh(self.x, self.y).line([1.0, 2.0, 3.0], self.x)
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta horizontal" in out
        assert "x-axis 10 --> 30" in out
        assert "bar [5, 15, 25]" in out
        assert "line [1, 2, 3]" in out

    def test_ylabel_with_numeric_horizontal(self):
        fig = XYChart().barh(self.x, self.y).ylabel("Index")
        self._figures.append(fig)
        out = fig.render()
        assert 'x-axis "Index" 10 --> 30' in out


# ---------------------------------------------------------------------------
# Multi-series
# ---------------------------------------------------------------------------

class TestMultiSeries:
    x = ["Jan", "Feb", "Mar", "Apr"]

    def test_two_lines(self):
        fig = XYChart().line(self.x, [1.0, 2.0, 3.0, 4.0]).line(self.x, [4.0, 3.0, 2.0, 1.0])
        self._figures.append(fig)
        out = fig.render()
        assert out.count("line") == 2
        assert "line [1, 2, 3, 4]" in out
        assert "line [4, 3, 2, 1]" in out

    def test_two_bars(self):
        fig = XYChart().bar(self.x, [10.0, 20.0, 30.0, 40.0]).bar(self.x, [5.0, 15.0, 25.0, 35.0])
        self._figures.append(fig)
        out = fig.render()
        assert out.count("bar") == 2
        assert "bar [10, 20, 30, 40]" in out
        assert "bar [5, 15, 25, 35]" in out

    def test_bar_and_two_lines(self):
        fig = (
            XYChart()
            .bar(self.x, [10.0, 20.0, 30.0, 40.0])
            .line(self.x, [5.0, 15.0, 25.0, 35.0])
            .line(self.x, [2.0, 4.0, 6.0, 8.0])
        )
        self._figures.append(fig)
        out = fig.render()
        assert "bar [10, 20, 30, 40]" in out
        assert "line [5, 15, 25, 35]" in out
        assert "line [2, 4, 6, 8]" in out
        assert out.index("bar") < out.index("line")

    def test_two_lines_horizontal(self):
        fig = (
            XYChart()
            .barh(self.x, [10.0, 20.0, 30.0, 40.0])
            .line([5.0, 15.0, 25.0, 35.0], self.x)
            .line([2.0, 4.0, 6.0, 8.0], self.x)
        )
        self._figures.append(fig)
        out = fig.render()
        assert "xychart-beta horizontal" in out
        assert "bar [10, 20, 30, 40]" in out
        assert "line [5, 15, 25, 35]" in out
        assert "line [2, 4, 6, 8]" in out

    def test_series_order_preserved_three(self):
        fig = (
            XYChart()
            .bar(self.x, [1.0, 2.0, 3.0, 4.0])
            .line(self.x, [5.0, 6.0, 7.0, 8.0])
            .line(self.x, [9.0, 10.0, 11.0, 12.0])
        )
        self._figures.append(fig)
        out = fig.render()
        bar_pos = out.index("bar [")
        first_line = out.index("line [")
        second_line = out.rindex("line [")
        assert bar_pos < first_line < second_line


# ---------------------------------------------------------------------------
# Number formatting
# ---------------------------------------------------------------------------

class TestNumberFormatting:
    def test_whole_floats_rendered_without_decimal(self):
        fig = XYChart().bar(["A"], [2.0])
        self._figures.append(fig)
        out = fig.render()
        assert "bar [2]" in out

    def test_actual_floats_preserved(self):
        fig = XYChart().line(["A", "B"], [1.5, 2.7])
        self._figures.append(fig)
        out = fig.render()
        assert "line [1.5, 2.7]" in out

    def test_negative_values(self):
        fig = XYChart().bar(["A", "B"], [-5.0, -3.0])
        self._figures.append(fig)
        out = fig.render()
        assert "bar [-5, -3]" in out


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

class TestColors:
    x = ["A", "B", "C"]

    def test_no_color_no_init_block(self):
        fig = XYChart().bar(self.x, [1.0, 2.0, 3.0])
        self._figures.append(fig)
        out = fig.render()
        assert "%%{init:" not in out

    def test_single_series_color(self):
        fig = XYChart().bar(self.x, [1.0, 2.0, 3.0], color="#ff0000")
        self._figures.append(fig)
        out = fig.render()
        assert "%%{init:" in out
        assert "#ff0000" in out

    def test_multiple_series_colors(self):
        fig = (
            XYChart()
            .bar(self.x, [1.0, 2.0, 3.0], color="#ff0000")
            .line(self.x, [4.0, 5.0, 6.0], color="#00ff00")
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000,#00ff00" in out

    def test_partial_colors_use_fallback(self):
        fig = (
            XYChart()
            .bar(self.x, [1.0, 2.0, 3.0], color="#ff0000")
            .line(self.x, [4.0, 5.0, 6.0])
        )
        self._figures.append(fig)
        out = fig.render()
        assert "#ff0000,#888888" in out

    def test_color_on_barh(self):
        fig = XYChart().barh(self.x, [1.0, 2.0, 3.0], color="#0000ff")
        self._figures.append(fig)
        out = fig.render()
        assert "#0000ff" in out
        assert "xychart-beta horizontal" in out

    def test_init_block_before_chart_header(self):
        fig = XYChart().bar(self.x, [1.0, 2.0, 3.0], color="#ff0000")
        self._figures.append(fig)
        out = fig.render()
        assert out.index("%%{init:") < out.index("xychart-beta")


# ---------------------------------------------------------------------------
# Validation errors — no figures saved (all tests expect exceptions)
# ---------------------------------------------------------------------------

class TestValidationErrors:
    def test_y_length_mismatch_categorical(self):
        with pytest.raises(ValueError, match="y length"):
            XYChart().bar(["A", "B", "C"], [1.0, 2.0])

    def test_y_length_mismatch_numeric(self):
        with pytest.raises(ValueError, match="y length"):
            XYChart().bar([1, 2, 3], [1.0, 2.0])

    def test_series_length_mismatch(self):
        with pytest.raises(ValueError, match="y length"):
            XYChart().bar(["A", "B"], [1.0, 2.0]).line(["A", "B"], [1.0, 2.0, 3.0])

    def test_x_categories_conflict(self):
        with pytest.raises(ValueError, match="conflict"):
            XYChart().bar(["A", "B"], [1.0, 2.0]).line(["X", "Y"], [3.0, 4.0])

    def test_x_numeric_range_conflict(self):
        with pytest.raises(ValueError, match="conflict"):
            XYChart().bar([1, 2], [1.0, 2.0]).line([3, 4], [3.0, 4.0])

    def test_mix_vertical_and_horizontal(self):
        with pytest.raises(ValueError, match="Cannot mix"):
            XYChart().bar(["A", "B"], [1.0, 2.0]).barh(["A", "B"], [3.0, 4.0])

    def test_mix_bar_and_barh(self):
        with pytest.raises(ValueError, match="Cannot mix"):
            XYChart().bar(["A", "B"], [1.0, 2.0]).barh(["A", "B"], [3.0, 4.0])

    def test_non_numeric_y(self):
        with pytest.raises(TypeError, match="not numeric"):
            XYChart().bar(["A"], ["oops"])

    def test_infinite_y(self):
        with pytest.raises(ValueError, match="not finite"):
            XYChart().bar(["A"], [float("inf")])

    def test_empty_y(self):
        with pytest.raises(ValueError, match="must not be empty"):
            XYChart().bar(["A"], [])
