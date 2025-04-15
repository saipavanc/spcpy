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
from typing import Dict, Optional, Tuple, Union, List


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


def despike(
    phi_vals, freqs, slope_threshold=0.25e-5, width=10e-2
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove spikes from a curve by filtering out points, and their neighbouring points,
    with a slope above slope_threshold.

    Args:
        phi_vals (array): pts on x-axis
        freqs (array): pts on y-axis
        slope_threshold (float, optional): The threshold of slope over which peaks will be removed.
                                            Defaults to 0.25e-5.
        width (float, optional): The width on x-axis over which the neighbouring pts will be removed.
                                    Defaults to 10e-2.

    Returns:
        Tuple[np.ndarray, np.ndarray]: phi_vals and freqs after removing spikes.
    """
    slopes = np.abs(np.gradient(freqs))
    idxs_slopes = [idx for idx in range(len(slopes)) if slopes[idx] > slope_threshold]
    # width of peaks or dips in units of the x-axis
    dx = phi_vals[1] - phi_vals[0]
    number_of_pts_around_peaks = int(width / dx)
    idxs_remove = idxs_slopes.copy()

    for idx in idxs_slopes:
        additional_pts = np.array(
            [
                idx + i
                for i in range(-number_of_pts_around_peaks, number_of_pts_around_peaks)
            ]
        )
        additional_pts = additional_pts[
            (additional_pts >= 0) & (additional_pts < len(phi_vals))
        ]
        idxs_remove.extend(additional_pts)

    idxs_remove = np.sort(np.unique(idxs_remove))
    idxs_filtered = [idx for idx in range(len(phi_vals)) if idx not in idxs_remove]
    return phi_vals[idxs_filtered], freqs[idxs_filtered]


def moving_average(data, window=2):
    """Makes a moving average of the data.

    Parameters
    ----------
    data
        Array like object
    window, optional
        The window size for the moving average. The default is 2.
    """
    averaged_data = data.copy()
    for idx, y in enumerate(data):
        subset = data[(idx-window//2) if idx >= window//2 else 0:idx+window//2+1]
        averaged_data[idx] = sum(subset)/len(subset)
    return averaged_data

def filter(x_vals, y_vals, y_range: tuple):
    """
    Used to filter out all the points which are not in the y_range.

    Parameters
    ----------
    x_vals
        array like object
    y_vals
        array like object
    y_range
        tuple showing the range of y values to be kept.

    Returns
    -------
        All the data points which are in the y_range.
    """
    x_vals_copy = np.array(x_vals.copy())
    y_vals_copy = np.array(y_vals.copy())
    filtered_out_idxs = []
    for idx, y_val in enumerate(y_vals):
        if not y_range[0] <= y_val <= y_range[1]:
            filtered_out_idxs.append(idx)
    result_idxs = [idx for idx in range(len(x_vals)) if idx not in filtered_out_idxs]
    return x_vals_copy[result_idxs], y_vals_copy[result_idxs]