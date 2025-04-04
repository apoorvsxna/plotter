from typing import Iterable, Tuple, Union
from .markers import markers

Number = Union[int, float]

class AData:
    def __init__(self, x: Iterable, y: Iterable, marker: str = '_.', 
                 plot_slope: bool = True, label: str = None):
        self.x = list(x)
        self.y = list(y)
        self.plot_slope = plot_slope
        self.label = label  # New label attribute
        self.set_marker(marker)
    
    def set_marker(self, marker: str) -> None:
        if marker in [None, 'None', u'None', '']:
            self.plot_slope = True
            self.marker = ''
        elif marker[0] == '_':
            self.marker = markers[marker[1:]]
        else:
            self.marker = marker
    
    def extent(self) -> Tuple[Number, Number, Number, Number]:
        return [min(self.x), max(self.x), min(self.y), max(self.y)]
    
    def __repr__(self) -> str:
        return f"AData({self.x}, {self.y}, label={self.label})"