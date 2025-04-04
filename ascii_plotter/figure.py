from .canvas import ACanvas
from .data import AData
from .utils import _transpose, _y_reverse, _sign
import math as _math
from typing import Sequence, Tuple, Union

Number = Union[int, float]

class AFigure:
    def __init__(self, shape: Tuple[Number, Number] = (80, 20),
                 margins: Tuple[Number, Number] = (0.05, 0.1),
                 draw_axes: bool = True, newline: str = '\n',
                 plot_labels: bool = True, xlim: Sequence[Number] = None,
                 ylim: Sequence[Number] = None):
        self.canvas = ACanvas(shape, margins, xlim, ylim)
        self.draw_axes = draw_axes
        self.new_line = newline
        self.plot_labels = plot_labels
        self.output_buffer = None
        self.tickSymbols = u'\u253C'
        self.x_axis_symbol = u'\u2500'
        self.y_axis_symbol = u'\u2502'
        self.data = []

    def xlim(self, vmin: Number = None, vmax: Number = None) -> Tuple[Number, Number]:
        return self.canvas.xlim(vmin, vmax)
    def ylim(self, vmin: Number = None, vmax: Number = None) -> Tuple[Number, Number]:
        return self.canvas.ylim(vmin, vmax)
    def get_coord(self, val: Number, min_val: Number, step: Number, limits: Sequence[Number] = None) -> int:
        result = int((val - min_val) / step)
        if limits:
            if result <= limits[0]:
                result = limits[0]
            elif result >= limits[1]:
                result = limits[1] - 1
        return result
    def _draw_axes(self):
        zero_x = self.get_coord(0, self.canvas.min_x, self.canvas.x_step, limits=[1, self.canvas.x_size])
        if zero_x >= self.canvas.x_size:
            zero_x = self.canvas.x_size - 1
        for y in range(self.canvas.y_size):
            self.output_buffer[zero_x][y] = self.y_axis_symbol
        zero_y = self.get_coord(0, self.canvas.min_y, self.canvas.y_step, limits=[1, self.canvas.y_size])
        if zero_y >= self.canvas.y_size:
            zero_y = self.canvas.y_size - 1
        for x in range(self.canvas.x_size):
            self.output_buffer[x][zero_y] = self.x_axis_symbol
        self.output_buffer[zero_x][zero_y] = self.tickSymbols
    def _get_symbol_by_slope(self, slope: Number, default_symbol: str) -> str:
        if slope > _math.tan(3*_math.pi/8):
            return "|"
        elif _math.tan(_math.pi/8) < slope < _math.tan(3*_math.pi/8):
            return u'\u27cb'
        elif abs(slope) < _math.tan(_math.pi/8):
            return "-"
        elif _math.tan(-3*_math.pi/8) < slope < _math.tan(-_math.pi/8):
            return u'\u27CD'
        elif slope < _math.tan(-3*_math.pi/8):
            return "|"
        else:
            return default_symbol
    def _plot_labels(self):
        if self.canvas.y_size < 2:
            return
        act_min_x, act_max_x, act_min_y, act_max_y = self.canvas.extent()
        min_x_coord = self.get_coord(act_min_x, self.canvas.min_x, self.canvas.x_step, limits=[0, self.canvas.x_size])
        max_x_coord = self.get_coord(act_max_x, self.canvas.min_x, self.canvas.x_step, limits=[0, self.canvas.x_size])
        min_y_coord = self.get_coord(act_min_y, self.canvas.min_y, self.canvas.y_step, limits=[1, self.canvas.y_size])
        max_y_coord = self.get_coord(act_max_y, self.canvas.min_y, self.canvas.y_step, limits=[1, self.canvas.y_size])
        x_zero_coord = self.get_coord(0, self.canvas.min_x, self.canvas.x_step, limits=[0, self.canvas.x_size])
        y_zero_coord = self.get_coord(0, self.canvas.min_y, self.canvas.y_step, limits=[1, self.canvas.y_size])
        self.output_buffer[x_zero_coord][min_y_coord] = self.tickSymbols
        self.output_buffer[x_zero_coord][max_y_coord] = self.tickSymbols
        self.output_buffer[min_x_coord][y_zero_coord] = self.tickSymbols
        self.output_buffer[max_x_coord][y_zero_coord] = self.tickSymbols
        min_x_str, max_x_str, min_y_str, max_y_str = self.canvas.extent_str()
        if self.canvas.x_str():
            for i, c in enumerate(min_x_str):
                self.output_buffer[min_x_coord + i + 1][y_zero_coord - 1] = c
            for i, c in enumerate(max_x_str):
                self.output_buffer[max_x_coord + i - len(max_x_str)][y_zero_coord - 1] = c
        if self.canvas.y_str():
            for i, c in enumerate(max_y_str):
                self.output_buffer[x_zero_coord + i + 1][max_y_coord] = c
            for i, c in enumerate(min_y_str):
                self.output_buffer[x_zero_coord + i + 1][min_y_coord] = c
    def _plot_line(self, start, end, data: AData) -> bool:
        clipped = self.canvas._clip_line(start, end)
        if clipped is None:
            return False
        start, end = clipped
        x0 = self.get_coord(start[0], self.canvas.min_x, self.canvas.x_step)
        y0 = self.get_coord(start[1], self.canvas.min_y, self.canvas.y_step)
        x1 = self.get_coord(end[0], self.canvas.min_x, self.canvas.x_step)
        y1 = self.get_coord(end[1], self.canvas.min_y, self.canvas.y_step)
        if (x0, y0) == (x1, y1):
            return True
        y_zero_coord = self.get_coord(0, self.canvas.min_y, self.canvas.y_step, limits=[1, self.canvas.y_size])
        if start[0] - end[0] == 0:
            draw_symbol = "|"
        elif start[1] - end[1] == 0:
            draw_symbol = "-"
        else:
            slope = (1.0/self.canvas.ratio)*(end[1]-start[1])/(end[0]-start[0])
            draw_symbol = self._get_symbol_by_slope(slope, data.marker)
        dx = x1 - x0
        dy = y1 - y0
        if abs(dx) > abs(dy):
            s = _sign(dx)
            slope = float(dy)/dx
            for i in range(abs(int(dx))):
                cur = x0 + i * s
                cur_y = int(y0 + slope * i * s)
                sym = draw_symbol
                if self.draw_axes and cur_y == y_zero_coord and draw_symbol == self.x_axis_symbol:
                    sym = "-"
                self.output_buffer[cur][cur_y] = sym
        else:
            s = _sign(dy)
            slope = float(dx)/dy
            for i in range(abs(int(dy))):
                cur_y = y0 + i * s
                cur = int(x0 + slope * i * s)
                sym = draw_symbol
                if self.draw_axes and cur_y == y_zero_coord and draw_symbol == self.x_axis_symbol:
                    sym = "-"
                self.output_buffer[cur][cur_y] = sym
        return False
    def _plot_data_with_slope(self, data: AData):
        points = sorted(zip(data.x, data.y), key=lambda c: c[0])
        prev = points[0]
        for i, (xi, yi) in enumerate(points[1:], start=1):
            line_drawn = self._plot_line(prev, (xi, yi), data)
            prev = (xi, yi)
            if not line_drawn and self.canvas.coords_inside_data(xi, yi):
                sym = data.marker
                if i > 0:
                    px, py = points[i-1]
                    nx, ny = points[i]
                    if abs(nx-px) > 1e-6:
                        slope = (1.0/self.canvas.ratio)*(ny-py)/(nx-px)
                        sym = self._get_symbol_by_slope(slope, sym)
                x_coord = self.get_coord(xi, self.canvas.min_x, self.canvas.x_step)
                y_coord = self.get_coord(yi, self.canvas.min_y, self.canvas.y_step)
                if self.canvas.coords_inside_buffer(x_coord, y_coord):
                    y0_coord = self.get_coord(0, self.canvas.min_y, self.canvas.y_step)
                    if self.draw_axes and y_coord == y0_coord and sym == u"\u23bc":
                        sym = "="
                    self.output_buffer[x_coord][y_coord] = sym
    def _plot_data(self, data: AData):
        if data.plot_slope:
            self._plot_data_with_slope(data)
        else:
            for x, y in zip(data.x, data.y):
                if self.canvas.coords_inside_data(x, y):
                    x_coord = self.get_coord(x, self.canvas.min_x, self.canvas.x_step)
                    y_coord = self.get_coord(y, self.canvas.min_y, self.canvas.y_step)
                    if self.canvas.coords_inside_buffer(x_coord, y_coord):
                        self.output_buffer[x_coord][y_coord] = data.marker
    def auto_limits(self):
        if self.canvas.auto_adjust:
            min_x = float('inf')
            max_x = float('-inf')
            min_y = float('inf')
            max_y = float('-inf')
            for d in self.data:
                ex = d.extent()
                min_x = min(min_x, min(ex[:2]))
                max_x = max(max_x, max(ex[:2]))
                min_y = min(min_y, min(ex[2:]))
                max_y = max(max_y, max(ex[2:]))
            self.canvas.xlim([min_x, max_x])
            self.canvas.ylim([min_y, max_y])
    def append_data(self, data: AData):
        self.data.append(data)
        self.auto_limits()
    def plot(self, x_seq, y_seq=None, marker=None, plot_slope=False, xlim=None, ylim=None) -> str:
        if y_seq is None:
            y_seq = list(x_seq)
            x_seq = list(range(len(y_seq)))
        data = AData(x_seq, y_seq, marker=marker, plot_slope=plot_slope)
        self.append_data(data)
        if xlim is not None:
            self.canvas.xlim(xlim)
        if ylim is not None:
            self.canvas.ylim(ylim)
        return self.draw()
    def _draw_legend(self):
        """Draw legend in top-right corner"""
        legend_items = [(d.marker, d.label) for d in self.data if d.label]
        if not legend_items:
            return
        
        max_label_length = max(len(str(label)) for _, label in legend_items)
        legend_x = self.canvas.x_size - max_label_length - 4
        legend_y = 1

        for i, (marker, label) in enumerate(legend_items):
            y_pos = legend_y + i
            if y_pos >= self.canvas.y_size - 1:
                break
            
            # Draw marker
            x_pos = legend_x
            if self.canvas.coords_inside_buffer(x_pos, y_pos):
                self.output_buffer[x_pos][y_pos] = marker
            
            # Draw label
            for j, c in enumerate(str(label)):
                x_pos = legend_x + 2 + j
                if self.canvas.coords_inside_buffer(x_pos, y_pos):
                    self.output_buffer[x_pos][y_pos] = c

    def draw(self) -> str:
        self.output_buffer = [[" "] * self.canvas.y_size for _ in range(self.canvas.x_size)]
        if self.draw_axes:
            self._draw_axes()
        for d in self.data:
            self._plot_data(d)
        if self.plot_labels:
            self._plot_labels()
            self._draw_legend()  # Added legend drawing
        trans = _transpose(_y_reverse(self.output_buffer))
        return self.new_line.join("".join(row) for row in trans)