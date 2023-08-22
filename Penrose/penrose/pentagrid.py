# Define two lines with random a(slope) and b(intercept) values
# Plot the lines and their intersection point
# %%
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


WORKING_RANGE = 500
UNIT = 20

DRAW = False


def intersection(a1, b1, a2, b2):
    x = (b2 - b1) / (a1 - a2)
    y = a1 * x + b1
    return (x, y)


# First collect all the points that are on the horizontal line
def get_points_on_line(vertical_count: int = 0):
    sorted_points = []
    horizontal_line = b[0] + vertical_count * y_gap[0]
    for i in (-2, -1, 1, 2):
        x_int, _ = intersection(0, horizontal_line, slopes[i], b[i])
        # After we have the x_int, we can get all the points on the line, up to
        # the working range

        points = []
        # Upper half
        points += [
            x_int + x_gap[i] * j
            for j in range(
                int((WORKING_RANGE + 2 * abs(x_gap[i])) / abs(x_gap[i]))
            )
        ]
        # Lower half, without the first point
        points += [
            x_int - x_gap[i] * j
            for j in range(
                1, int((WORKING_RANGE + 2 * abs(x_gap[i])) / abs(x_gap[i]))
            )
        ]
        # We add a tuple of values, that looks like (line_id, x_coordinate)
        sorted_points += [(i, j) for j in points]
    # Sort the points by the x-coordinate
    sorted_points.sort(key=lambda x: x[1])
    return sorted_points


# %%
# angles of the lines (alpha)
angles = {i: i * math.pi / 5 for i in range(-2, 2 + 1)}
# slopes of the lines (a)
slopes = {i: math.tan(angles[i]) for i in (-2, -1, 1, 2)}
# X_GAP is the distance between two intersection points on the x-axis
x_gap = {i: UNIT / (math.sin(angles[i])) for i in (-2, -1, 1, 2)}
# Y_GAP is the distance between two intersection points on the y-axis
y_gap = {i: UNIT / (math.cos(angles[i])) for i in (-2, -1, 0, 1, 2)}

# Generate a random set of 5 intercepts, and scale them depending on the slope
# B are the intercepts of the lines with the y-axis (ax + b = y)
randomized_start = np.random.rand(5) - 0.5
b = {i: y_gap[i] * randomized_start[i] for i in (-2, -1, 0, 1, 2)}

vertical_count = 0
points = get_points_on_line(vertical_count)
points_next = get_points_on_line(vertical_count + 1)


if DRAW:
    plt.figure(figsize=(10, 10))
    plt.axis([-WORKING_RANGE, WORKING_RANGE, -WORKING_RANGE, WORKING_RANGE])

    # Start the plotting of the lines by plotting the grays
    # HOR GRAYS
    gap = y_gap[0]
    cur_y_int = b[0] + gap
    while abs(cur_y_int) < WORKING_RANGE:
        plt.axline((0, cur_y_int), slope=0, color="gray", alpha=0.5)
        cur_y_int += gap
    cur_y_int = b[0] - gap
    while abs(cur_y_int) < WORKING_RANGE:
        plt.axline((0, cur_y_int), slope=0, color="gray", alpha=0.5)
        cur_y_int -= gap

    # VERT GRAYS
    for i in (-2, -1, 1, 2):
        gap = y_gap[i]
        cur_y_int = b[i] + gap
        while True:
            plt.axline(
                (0, cur_y_int), slope=slopes[i], color="gray", alpha=0.5
            )
            x, y = intersection(0, WORKING_RANGE, slopes[i], cur_y_int)
            if slopes[i] > 0:
                if x < -WORKING_RANGE:
                    break
            else:
                if x > WORKING_RANGE:
                    break
            cur_y_int += gap
        cur_y_int = b[i] - gap
        while True:
            plt.axline(
                (0, cur_y_int), slope=slopes[i], color="gray", alpha=0.5
            )
            x, y = intersection(0, -WORKING_RANGE, slopes[i], cur_y_int)
            if slopes[i] > 0:
                if x > WORKING_RANGE:
                    break
            else:
                if x < -WORKING_RANGE:
                    break
            cur_y_int -= gap

    # Plot the horizontal line in red, and all the slopes in blue
    plt.axline((0, b[0]), slope=0, color="red")
    for i in (-2, -1, 1, 2):
        plt.axline((0, b[i]), slope=slopes[i], color="blue")

    # Now start collecting the set of shapes that can be generated. This is done
    # one horizontal line at a time, starting at -working_range, and going to
    # +working_range

    colors = {-2: "red", -1: "orange", 1: "green", 2: "blue"}

    plt.scatter(
        [i[1] for i in points],
        [b[0] + y_gap[0] * vertical_count] * len(points),
        c=[colors[i[0]] for i in points],
        marker="o",
        s=10,
        zorder=2,
    )
    plt.show()

# %%
# Make a second figure under the first one, and plot the points on the second
# horizontal line
plt.figure(figsize=(10, 10))
plt.axis(
    [0, len(points) * UNIT, -len(points) * UNIT / 2, len(points) * UNIT / 2]
)


# Start the plotting of the rhombuses
def plotRhombus(
    line_index: int, top_left_x: int = 0, top_left_y: int = 0, unit: int = 1
):
    # The points are given in the following order:
    # top left, top right, bottom right, bottom left
    if angles[line_index] > 0:
        new_angle = angles[line_index] - math.pi / 2
    else:
        new_angle = angles[line_index] + math.pi / 2
    x, y = unit * math.cos(new_angle), unit * math.sin(new_angle)
    points = [
        (top_left_x, top_left_y),
        (top_left_x + x, top_left_y + y),
        (top_left_x + x, top_left_y + y - unit),
        (top_left_x, top_left_y - unit),
    ]
    polygon = Polygon(points, closed=False, color=np.random.rand(3), alpha=0.5)
    plt.gca().add_patch(polygon)
    return (top_left_x + x, top_left_y + y)


x, y = 0, 0
for i in points:
    x, y = plotRhombus(i[0], x, y, unit=UNIT)
x, y = 0, UNIT
for i in points_next:
    x, y = plotRhombus(i[0], x, y, unit=UNIT)

plt.show()
# %%
