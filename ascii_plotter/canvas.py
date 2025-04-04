from typing import Sequence, Tuple, Union
from .utils import _sign

Number = Union[int, float]

class ACanvas:
    def __init__(self, shape: Sequence[Number] = None, margins: Sequence[Number] = None,
                 xlim: Sequence[Number] = None, ylim: Sequence[Number] = None):
        self.shape = shape or (50, 20)
        self.margins = margins or (0.05, 0.1)
        self._xlim = list(xlim) if xlim is not None else [0, 1]
        self._ylim = list(ylim) if ylim is not None else [0, 1]
        self.auto_adjust = True
        self.margin_factor = 1
    @property
    def x_size(self) -> int:
        return self.shape[0]
    @property
    def y_size(self) -> int:
        return self.shape[1]
    @property
    def x_margin(self) -> int:
        return self.margins[0]
    @property
    def y_margin(self) -> int:
        return self.margins[1]
    def xlim(self, vmin: Number = None, vmax: Number = None):
        if vmin is None and vmax is None:
            return self._xlim
        elif hasattr(vmin, '__iter__'):
            self._xlim = list(vmin)[:2]
        else:
            self._xlim = [vmin, vmax]
        if self._xlim[0] == self._xlim[1]:
            self._xlim[1] += 1
        self._xlim[0] -= self.x_mod
        self._xlim[1] += self.x_mod
    def ylim(self, vmin: Number = None, vmax: Number = None):
        if vmin is None and vmax is None:
            return self._ylim
        elif hasattr(vmin, '__iter__'):
            self._ylim = list(vmin)[:2]
        else:
            self._ylim = [vmin, vmax]
        if self._ylim[0] == self._ylim[1]:
            self._ylim[1] += 1
        self._ylim[0] -= self.y_mod
        self._ylim[1] += self.y_mod
    @property
    def min_x(self) -> Number:
        return self._xlim[0]
    @property
    def max_x(self) -> Number:
        return self._xlim[1]
    @property
    def min_y(self) -> Number:
        return self._ylim[0]
    @property
    def max_y(self) -> Number:
        return self._ylim[1]
    @property
    def x_step(self) -> Number:
        return (self.max_x - self.min_x) / self.x_size
    @property
    def y_step(self) -> Number:
        return (self.max_y - self.min_y) / self.y_size
    @property
    def ratio(self) -> Number:
        return self.y_step / self.x_step
    @property
    def x_mod(self) -> Number:
        return (self.max_x - self.min_x) * self.x_margin
    @property
    def y_mod(self) -> Number:
        return (self.max_y - self.min_y) * self.y_margin
    def extent(self, margin_factor: Number = None) -> Tuple[Number, Number, Number, Number]:
        mf = margin_factor or self.margin_factor
        min_x = self.min_x + self.x_mod * mf
        max_x = self.max_x - self.x_mod * mf
        min_y = self.min_y + self.y_mod * mf
        max_y = self.max_y - self.y_mod * mf
        return (min_x, max_x, min_y, max_y)
    def extent_str(self, margin: Number = None) -> Tuple[str, str, str, str]:
        def transform(val: Number, fmt: str) -> str:
            if abs(val) < 1:
                return f"{val:+.2g}"
            elif fmt is not None:
                return fmt % val
            else:
                return str(val)
        e = self.extent(margin)
        xfmt = self.x_str()
        yfmt = self.y_str()
        return transform(e[0], xfmt), transform(e[1], xfmt), transform(e[2], yfmt), transform(e[3], yfmt)
    def x_str(self) -> str:
        if self.x_size < 16:
            return None
        elif self.x_size < 23:
            return "%+.2g"
        else:
            return "%+g"
    def y_str(self) -> str:
        if self.x_size < 8:
            return None
        elif self.x_size < 11:
            return "%+.2g"
        else:
            return "%+g"
    def coords_inside_buffer(self, x: Number, y: Number) -> bool:
        return (0 <= x < self.x_size) and (0 <= y < self.y_size)
    def coords_inside_data(self, x: Number, y: Number) -> bool:
        return (self.min_x <= x < self.max_x) and (self.min_y <= y < self.max_y)
    def _clip_line(self, pt1: Sequence, pt2: Sequence):
        e = self.extent()
        x_min = min(pt1[0], pt2[0])
        x_max = max(pt1[0], pt2[0])
        y_min = min(pt1[1], pt2[1])
        y_max = max(pt1[1], pt2[1])
        if pt1[0] == pt2[0]:
            return ((pt1[0], max(y_min, e[1])), (pt1[0], min(y_max, e[3])))
        if pt1[1] == pt2[1]:
            return ((max(x_min, e[0]), pt1[1]), (min(x_max, e[2]), pt1[1]))
        if (e[0] <= pt1[0] < e[2] and e[1] <= pt1[1] < e[3] and
            e[0] <= pt2[0] < e[2] and e[1] <= pt2[1] < e[3]):
            return pt1, pt2
        ts = [0.0, 1.0,
              float(e[0] - pt1[0]) / (pt2[0] - pt1[0]),
              float(e[2] - pt1[0]) / (pt2[0] - pt1[0]),
              float(e[1] - pt1[1]) / (pt2[1] - pt1[1]),
              float(e[3] - pt1[1]) / (pt2[1] - pt1[1])]
        ts.sort()
        if ts[2] < 0 or ts[2] >= 1 or ts[3] < 0 or ts[3] >= 1:
            return None
        result = [(a + t * (b - a)) for t in (ts[2], ts[3]) for a, b in zip(pt1, pt2)]
        return (result[:2], result[2:])
