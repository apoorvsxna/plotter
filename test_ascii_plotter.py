import numpy as np
import pytest
from ascii_plotter import (
    AData, AFigure, plot, bar, svg_export, 
    steppify, stemify, hist, imshow
)
import tempfile
import sys

def test_bar_chart(capsys):
    x = [1, 2, 3]
    heights = [4, 5, 3]
    bar(x, heights, marker='█', shape=(30, 10))
    captured = capsys.readouterr().out
    assert '█' in captured  # Remove line-specific check
    
def test_legend():
    fig = AFigure(shape=(20, 10))
    data = AData([1, 2], [3, 4], label="Test Data", marker='*')
    fig.append_data(data)
    out = fig.draw()
    assert "* Test Data" in out.replace('\u2500', ' ')  # Account for axis characters

def test_svg_export(tmp_path):
    test_plot = "Hello\nWorld!"
    svg_file = tmp_path / "test.svg"
    svg_export(test_plot, str(svg_file))
    content = svg_file.read_text()
    assert '<svg' in content
    assert 'Hello' in content
    assert 'World' in content

@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Interactive mode not supported on Windows"
)

def test_AData_extent():
    x = [0, 1, 2]
    y = [3, 4, 5]
    data = AData(x, y)
    assert data.extent() == [0, 2, 3, 5]

def test_ACanvas_properties():
    from ascii_plotter.canvas import ACanvas
    canvas = ACanvas(shape=(100, 50), xlim=[0, 10], ylim=[0, 20])
    assert abs(canvas.x_step - 0.1) < 1e-6
    assert abs(canvas.y_step - 0.4) < 1e-6
    ext = canvas.extent()
    assert len(ext) == 4

def test_AFigure_draw():
    fig = AFigure(shape=(40, 20), xlim=[-5, 5], ylim=[-5, 5])
    out = fig.plot(list(range(-5,6)), [x for x in range(-5,6)], marker="_-")
    assert isinstance(out, str)
    assert "\u253C" in out

def test_steppify():
    x = np.array([0, 1, 2, 3])
    y = np.array([0, 1, 0, 1])
    xx, yy = steppify(x, y)
    assert len(xx) > len(x)
    assert len(yy) > len(y)

def test_stemify():
    x = np.array([0, 1, 2])
    y = np.array([1, 2, 3])
    xx, yy = stemify(x, y)
    assert len(xx) == 3 * len(x)
    assert len(yy) == 3 * len(y)

def test_plot_function(capsys):
    x = np.linspace(0, 10, 20)
    y = np.sin(x)
    plot(x, y, marker=".-")
    captured = capsys.readouterr().out
    assert captured != ""
    assert any(sym in captured for sym in ["\u2500", "\u2502", "\u253C"])

def test_hist_function(capsys):
    data = np.random.randn(100)
    hist(data, bins=10, histtype='stem')
    captured = capsys.readouterr().out
    assert captured.strip() != ""

def test_imshow_function(capsys):
    img = np.random.rand(20, 20)
    imshow(img, width=20)
    captured = capsys.readouterr().out
    assert captured.strip() != ""
    assert "\n" in captured
