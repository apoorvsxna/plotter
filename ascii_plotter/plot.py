import numpy as np
from .figure import AFigure
from .data import AData
import sys

def plot(x, y=None, marker=None, shape=(50, 20), draw_axes=True, newline='\n',
         plot_slope=False, x_margin=0.05, y_margin=0.1, plot_labels=True, xlim=None, ylim=None):
    fig = AFigure(shape=shape, margins=(x_margin, y_margin), draw_axes=draw_axes,
                  newline=newline, plot_labels=plot_labels, xlim=xlim, ylim=ylim)
    result = fig.plot(x, y, marker=marker, plot_slope=plot_slope)
    print(result)

def steppify(x, y):
    dx = 0.5 * (x[1:] + x[:-1])
    xx = np.zeros(2 * len(dx), dtype=float)
    yy = np.zeros(2 * len(y), dtype=float)
    xx[0::2], xx[1::2] = dx, dx
    yy[0::2], yy[1::2] = y, y
    xx = np.concatenate(([x[0] - (dx[0] - x[0])], xx, [x[-1] + (x[-1] - dx[-1])]))
    return xx, yy

def stemify(x, y):
    xx = np.zeros(3 * len(x), dtype=float)
    yy = np.zeros(3 * len(y), dtype=float)
    xx[0::3], xx[1::3], xx[2::3] = x, x, x
    yy[1::3] = y
    return xx, yy

def step(x, y, shape=(50, 20), draw_axes=True, newline='\n', marker='_.',
         plot_slope=True, x_margin=0.05, y_margin=0.1, plot_labels=True, xlim=None, ylim=None):
    _x, _y = steppify(x, y)
    plot(_x, _y, shape=shape, draw_axes=draw_axes, newline=newline, marker=marker,
         plot_slope=plot_slope, x_margin=x_margin, y_margin=y_margin,
         plot_labels=plot_labels, xlim=xlim, ylim=ylim)

def stem(x, y, shape=(50, 20), draw_axes=True, newline='\n', marker='_.',
         plot_slope=True, x_margin=0.05, y_margin=0.1, plot_labels=True, xlim=None, ylim=None):
    _x, _y = stemify(x, y)
    plot(_x, _y, shape=shape, draw_axes=draw_axes, newline=newline, marker=marker,
         plot_slope=plot_slope, x_margin=x_margin, y_margin=y_margin,
         plot_labels=plot_labels, xlim=xlim, ylim=ylim)

def hist(x, bins=10, normed=False, weights=None, density=None, histtype='stem',
         shape=(50, 20), draw_axes=True, newline='\n', marker='_.', plot_slope=False,
         x_margin=0.05, y_margin=0.1, plot_labels=True, xlim=None, ylim=None):
    n, b = np.histogram(x, bins=bins, range=xlim, density=density, weights=weights)
    _x = 0.5 * (b[:-1] + b[1:])
    if histtype == 'step':
        step(_x, n.astype(float), shape, draw_axes, newline, marker, plot_slope, x_margin, y_margin, plot_labels, xlim, ylim)
    elif histtype == 'stem':
        stem(_x, n.astype(float), shape, draw_axes, newline, marker, plot_slope, x_margin, y_margin, plot_labels, xlim, ylim)
    else:
        y_vals = n.astype(float)
        plot(_x, y_vals, shape=shape, draw_axes=draw_axes, newline=newline, marker=marker,
             plot_slope=plot_slope, x_margin=x_margin, y_margin=y_margin,
             plot_labels=plot_labels, xlim=xlim, ylim=ylim)

def hist2d(x, y, bins=[50,20], range=None, normed=False, weights=None, ncolors=16, width=50, percentiles=None):
    im, ex, ey = np.histogram2d(x, y, bins=bins, range=range, density=normed, weights=weights)
    if percentiles is None:
        imshow(im, extent=[min(ex), max(ex), min(ey), max(ey)], ncolors=ncolors, width=width)
    else:
        percentile_imshow(im, levels=percentiles, extent=None, width=width, ncolors=ncolors)

def percentile_imshow(im, levels=[68,95,99], extent=None, width=50, ncolors=16):
    _im = im.astype(float)
    _im -= im.min()
    _im /= _im.max()
    n = len(levels)
    for e, lk in enumerate(sorted(levels)):
        _im[_im <= 0.01 * lk] = n - e
    imshow(1. - _im, extent=None, width=width, ncolors=ncolors)

def imshow(im, extent=None, width=50, ncolors=16):
    from scipy import ndimage
    width0 = im.shape[0]
    _im = ndimage.zoom(im.astype(float), float(width)/float(width0))
    _im -= im.min()
    _im /= _im.max()
    width, height = _im.shape[:2]
    if len(im.shape) > 2:
        clr = True
    else:
        clr = False
    if ncolors == 16:
        color = "MNHQ$OC?7>!:-;. "[::-1]
    else:
        color = ('''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`'. '''[::-1])
    ncolors = len(color)
    string = ""
    if not clr:
        for h in range(height):
            for w in range(width):
                string += color[int(_im[w, h]*(ncolors-1))]
            string += "\n"
    else:
        for h in range(height):
            for w in range(width):
                string += color[int(sum(_im[w, h])*(ncolors-1))]
            string += "\n"
    print(string)
 
def bar(x, heights, width=0.8, marker='█', **kwargs):
    """Plot vertical ASCII bars"""
    _x = []
    _y = []
    if len(x) > 1:
        bar_width = (max(x) - min(x)) / len(x) * width
    else:
        bar_width = width
    
    for xi, h in zip(x, heights):
        _x.extend([xi - bar_width/2, xi + bar_width/2])
        _y.extend([0, h])
    
    return plot(_x, _y, marker=marker, plot_slope=False, **kwargs)

def interactive(fig: AFigure):
    """Enable interactive pan/zoom mode"""
    if sys.platform.startswith('win'):
        raise NotImplementedError("Interactive mode not supported on Windows")

    try:
        import curses
    except ImportError:
        raise RuntimeError("curses library required for interactive mode")
    
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        while True:
            stdscr.clear()
            stdscr.addstr(fig.draw())
            stdscr.refresh()
            
            key = stdscr.getch()
            xmin, xmax = fig.canvas.xlim()
            ymin, ymax = fig.canvas.ylim()
            dx = (xmax - xmin) * 0.1
            dy = (ymax - ymin) * 0.1

            if key == curses.KEY_RIGHT:
                fig.canvas.xlim(xmin + dx, xmax + dx)
            elif key == curses.KEY_LEFT:
                fig.canvas.xlim(xmin - dx, xmax - dx)
            elif key == curses.KEY_UP:
                fig.canvas.ylim(ymin + dy, ymax + dy)
            elif key == curses.KEY_DOWN:
                fig.canvas.ylim(ymin - dy, ymax - dy)
            elif key == ord('+'):
                fig.canvas.xlim(xmin - dx, xmax + dx)
                fig.canvas.ylim(ymin - dy, ymax + dy)
            elif key == ord('-'):
                fig.canvas.xlim(xmin + dx, xmax - dx)
                fig.canvas.ylim(ymin + dy, ymax - dy)
            elif key == ord('q'):
                break
    finally:
        curses.endwin()

def svg_export(ascii_plot: str, filename: str, font_size: int = 12):
    """Export ASCII plot to SVG"""
    lines = ascii_plot.split('\n')
    height = len(lines)
    width = max(len(line) for line in lines) if height > 0 else 0

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width * font_size} {height * font_size}" '
        f'width="{width * font_size}" height="{height * font_size}">',
        '<style>text { font-family: monospace; font-size: %dpx; }</style>' % font_size
    ]

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            svg.append(
                f'<text x="{x * font_size}" y="{(y + 1) * font_size}">{char}</text>'
            )
    
    svg.append('</svg>')
    
    with open(filename, 'w') as f:
        f.write('\n'.join(svg))