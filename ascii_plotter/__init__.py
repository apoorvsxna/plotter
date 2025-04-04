__version__ = "2.0"
__author__ = "M. Fouesneau"

from .markers import markers
from .data import AData
from .canvas import ACanvas
from .figure import AFigure
from .plot import (plot, steppify, stemify, hist, hist2d, imshow, 
                  percentile_imshow, stem, step, bar, interactive, svg_export)

__all__ = [
    'markers', 'ACanvas', 'AData', 'AFigure', 'hist', 'hist2d', 
    'imshow', 'percentile_imshow', 'plot', 'stem', 'stemify', 'step', 
    'steppify', 'bar', 'interactive', 'svg_export', '__version__', '__author__'
]