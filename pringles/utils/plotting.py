import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter
from typing import Any
from .utils import VirtualTime


def __vtime_formatter(x: Any, pos: Any):
    vtime_from_number = VirtualTime.from_number(x)
    return str(vtime_from_number)


def new_vtime_aware_axes() -> Axes:
    """Creates a new VirtualTime aware axes, which formats auttomatically
    the X axis with a VirtualTime format.

    :return: A new VirtualTime aware axes
    :rtype: Axes
    """
    ax = plt.axes()
    formatter = FuncFormatter(__vtime_formatter)
    ax.xaxis.set_minor_formatter(formatter)
    ax.xaxis.set_major_formatter(formatter)
    ax.tick_params("x", labelrotation=90)
    return ax
