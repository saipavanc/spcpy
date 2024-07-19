from typing import Optional
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import rand

from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text


class Plot:
    def __init__(self, fig: Figure, ax: Axes, is_interactive: bool = False):
        self.fig = fig
        self.ax = ax
        self.is_interactive = is_interactive
        if self.is_interactive:
            plt.ion()

    def onpick1(event):
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print("onpick1 line:", np.column_stack([xdata[ind], ydata[ind]]))
        elif isinstance(event.artist, Rectangle):
            patch = event.artist
            print("onpick1 patch:", patch.get_path())

    def plot1D(
        self,
        x,
        y,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
    ):
        self.ax.plot(x, y)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_title(title)
        self.fig.canvas.draw()

    def return_clicked_pts(self, num_pts: int):
        """
        Returns the clicked points on the plot.

        Args:
            num_pts (int): number of points to be clicked on the plot.
        """
        self.fig.ginput(num_pts, timeout=0, show_clicks=True)
