from utilities.degree_math import sin, cos


def mirror_y(point, height):
    """
    Converts a point from standard cartesian to graphics cartesian for use by GUI just before drawing to the screen,
    as the QGraphicsScene has (0,0) in the top left
    """
    return point[0], height-point[1]


def rect_to_points(x, y, w, h, t):
    """
    Converts a rectangle of the form x, y, width, height, theta into 4 points
    """
    points = list()
    points.append((x, y))
    points.append((x + h*sin(t), y + h*cos(t)))
    points.append((x + h*sin(t) + w*cos(t), y + h*cos(t) - w*sin(t)))
    points.append((x + w*cos(t), y - w*sin(t)))
    return points


def generate_lines(rects, room):
    """
    Converts a list of rects each containing x, y, width, height, theta into a list of
    lines (each rect has 4 lines)
    room is (width, height) of surrounding room
    returns list of lines, each line is 2 points
    """
    # x, y, w, h, angle

    rects.append([0, 0, room[0], room[1], 0])  # The whole room
    lines = []
    for rect in rects:
        points = rect_to_points(*rect)
        # Now we have the 4 points on the rect. Form 4 lines from them
        for i in range(4):
            lines.append((points[i], points[(i+1) % 4]))
    return lines

