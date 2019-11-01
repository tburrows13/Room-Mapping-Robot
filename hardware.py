from random import gauss

from utilities.degree_math import sin, cos, tan, sqrt, atan
from utilities.geometry_utils import generate_lines


class Hardware:
    def __init__(self, initial_position, initial_angle, map_size, rects, config_values, position_changed_signal, rotation_changed_signal):
        self.pos = initial_position
        self.rotation = initial_angle

        self.scanner = _Scanner(map_size, rects, self.pos, config_values[0], config_values[1], config_values[2])
        self.odometer = _Odometer(map_size, rects, self.pos, self.rotation, config_values[3], config_values[4])

        self.position_changed_signal = position_changed_signal
        self.rotation_changed_signal = rotation_changed_signal

    def scan(self):
        distances = self.scanner.scan(self.pos)
        return distances

    def move_forward(self, distance):
        distance_moved, actual_distance_moved, self.pos = self.odometer.move_forward(distance)
        self.position_changed_signal.emit(self.pos)

    def rotate(self, angle):
        angle_rotated, actual_angle_rotated, self.rotation = self.odometer.rotate(angle)
        self.rotation_changed_signal.emit(self.rotation)


class _Scanner:
    def __init__(self, room_size, rects, initial_position, number_of_readings, sensor_reading_fuzziness, sensor_angle_fuzziness):
        self.room_size = room_size
        self.position = initial_position
        self.sensor_angle_fuzziness = sensor_angle_fuzziness
        self.sensor_reading_fuzziness = sensor_reading_fuzziness
        self.number_of_readings = number_of_readings

        self.lines = generate_lines(rects, room_size)

    def scan(self, current_position):
        self.position = current_position

        angles_dict = self._find_angles()
        distances_dict = {}
        for i in range(self.number_of_readings):
            angle = i * (360/self.number_of_readings)
            angle = gauss(angle, self.sensor_angle_fuzziness)
            if angle >= 180:
                angle -= 360
            if angle <= -180:
                angle += 360

            distance = self._find_shortest_intersection(angle, angles_dict)
            distances_dict[angle] = distance
        assert len(distances_dict) != 0
        return distances_dict

    def find_angle(self, end):
        """
        Finds the angle between 0˚ and the line from self.position to end
        """
        start = self.position
        while start == end:
            start = start[0] - 0.001, start[1] - 0.001

        if start[0] == end[0]:
            if end[1] > start[1]:
                angle = 90
            else:
                angle = -90
        else:
            angle = atan((end[1] - start[1]) / (end[0] - start[0]))
        if start[0] > end[0]:  # Then it is greater than 90˚ or less than -90˚
            if end[1] >= start[1]:  # Then it is in the 2nd quadrant
                angle += 180
            elif end[1] < start[1]:
                angle -= 180
        return angle

    def _find_angles(self):
        """
        Work out the angle to the start and end of each line in the room
        """
        angles_dict = {}
        for line in self.lines:
            angle1 = self.find_angle(line[0])
            angle2 = self.find_angle(line[1])

            # Swap them around if they are the wrong way around
            if angle2 < angle1:
                angle1, angle2 = angle2, angle1
            angles_dict[line] = (angle1, angle2)

        return angles_dict

    def _find_intersection(self, angle, p1, p2):
        """
        Finds the point on the wall p1 -> p2 that intersects with the incident ray
        from pos at angle theta, and the length of the incident ray
        """
        m_incident = tan(angle)

        # First do edge case where m_wall == infinity
        if p2[0] == p1[0]:
            x = p1[0]

            # y = m(x-x_1) + y_1
            y = m_incident * (x - self.position[0]) + self.position[1]
        else:
            m_wall = (p2[1] - p1[1]) / (p2[0] - p1[0])

            x = (p1[1] - p1[0] * m_wall + self.position[0] * m_incident - self.position[1]) / (m_incident - m_wall)
            y = m_wall * (x - p1[0]) + p1[1]

        length = sqrt((x - self.position[0]) ** 2 + (y - self.position[1]) ** 2)
        length = gauss(length, self.sensor_reading_fuzziness)

        return length

    def _find_shortest_intersection(self, angle, angles_dict):
        lengths = []
        for line in angles_dict:
            angles = angles_dict[line]  # angles is a tuple, length 2

            # Allow for the fact that some angles go over between -180 and 180
            if abs(angles[1] - angles[0]) > 180:
                if angles[0] >= angle or angles[1] <= angle:
                    length_to_line = self._find_intersection(angle, *line)
                    lengths.append(length_to_line)

            elif angles[0] <= angle <= angles[1]:
                length_to_line = self._find_intersection(angle, *line)
                lengths.append(length_to_line)

        if len(lengths) == 0:
            raise ValueError(f"No lines to collide with at angle {angle}")

        return min(lengths)


class _Odometer:
    def __init__(self, room_size, rects, initial_position, initial_rotation, distance_moved_fuzziness, angle_rotated_fuzziness):
        self.room_size = room_size
        self.position = initial_position
        self.rotation = initial_rotation
        self.rects = rects
        self.distance_moved_fuzziness = distance_moved_fuzziness
        self.angle_rotated_fuzziness = angle_rotated_fuzziness

    def move_forward(self, distance):
        distance_moved = distance
        actual_distance_moved = gauss(distance_moved, self.distance_moved_fuzziness)

        new_x = self.position[0] + actual_distance_moved * cos(self.rotation)
        new_y = self.position[1] + actual_distance_moved * sin(self.rotation)

        # Check new_x and new_y against map borders
        if new_x >= self.room_size[0] or new_x <= 0 or new_y >= self.room_size[1] or new_y <= 0:
            distance_moved = 0
            actual_distance_moved = 0
        else:
            self.position = (new_x, new_y)
        return distance_moved, actual_distance_moved, self.position

    def rotate(self, angle):
        angle_rotated = angle
        actual_angle_rotated = gauss(angle_rotated, self.angle_rotated_fuzziness)
        self.rotation += actual_angle_rotated
        return angle_rotated, actual_angle_rotated, self.rotation
