import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


from utils.util_types import *
from utils.plane import Plane


def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)


# ====== Utilities ======
def plot_plane(ax, point, normal, size=3, color='cyan', alpha=0.2, label=None):
    """
    Plot a 3D plane from a point and normal.
    """
    # Create a grid of points
    d = -point.dot(normal)
    xx, yy = np.meshgrid(np.linspace(-size, size, 10), np.linspace(-size, size, 10))

    # Solve for z: (a*x + b*y + c*z + d = 0) → z = (-d - a*x - b*y) / c
    a, b, c = normal
    if np.isclose(c, 0):
        # Vertical plane (avoid division by zero)
        zz = (-d - a * xx - b * yy) * 0
    else:
        zz = (-d - a * xx - b * yy) / c

    ax.plot_surface(xx, yy, zz, color=color, alpha=alpha, rstride=1, cstride=1, edgecolor='none')

    # if label:
    #     ax.text(point[0], point[1], point[2], label, color='black', fontsize=10, weight='bold')


def plot_arrow(ax, start, end, color='blue'):
    """
    Plot an arrow in 3D.
    """
    start = np.array(start)
    end = np.array(end)
    vec = end - start
    ax.quiver(start[0], start[1], start[2],
              vec[0], vec[1], vec[2],
              arrow_length_ratio=0.1, color=color, linewidth=3)


# ====== Example intersection check (stub, replace with your function) ======
def arrow_intersects_plane(start, end, point, normal):
    """
    Check if the line segment intersects a plane.
    """
    start = np.array(start)
    end = np.array(end)
    point = np.array(point)
    normal = np.array(normal)

    u = end - start
    denom = normal.dot(u)
    if np.isclose(denom, 0):
        return False  # Parallel, no intersection

    t = normal.dot(point - start) / denom
    return 0 <= t <= 1  # Intersection lies within the segment


# ====== Demo ======
def visualize(hyperplanes: List[Plane], arrows_from: Position, arrows_to: List[Position]):
    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(111, projection='3d')
    cm = get_cmap(len(hyperplanes))

    # Plot hyperplanes
    for i, plane in enumerate(hyperplanes, start=1):
        plot_plane(ax, plane.point, plane.normal, label=f"P{i}", color=cm(i), size=5)

    # Plot arrows
    for target in arrows_to:
        c = 'green'
        for plane in hyperplanes:
            d = plane.intersection_with_line_coeff(arrows_from, target)
            if d is not None and d > 0:
                c = 'black'
                break
        plot_arrow(ax, arrows_from.as_np_array(), arrows_from.as_np_array() + target.as_np_array(), color=c)

    for plane in hyperplanes:
        plot_arrow(ax, plane.point, plane.point + plane.normal, color='red')

    # Formatting
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_box_aspect([1, 1, 1])
    plt.show()
