import os.path
import json

import sqlite3

DATABASE_FILE = "database.db"
SETUP_FILE = "database_setup.sql"


class DatabaseManager:
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_FILE)  # Will automatically create the database if it doesn't exist

        setup_needed = True if not os.path.isfile(DATABASE_FILE) else False

        if setup_needed:
            self.setup_database()

    def setup_database(self):
        """
        WARNING:
        Will completely wipe the database, and create it afresh
        """
        print("Setting up database")
        with open(SETUP_FILE) as file:
            commands = file.read()
        self.connection.executescript(commands)
        self.connection.commit()

    def add_robot(self, name, number_of_readings, distance_sensor_fuzziness, angle_sensor_fuzziness, distance_moved_fuzziness, angle_rotated_fuzziness):
        command = "INSERT INTO Robot VALUES (Null, ?, ?, ?, ?, ?, ?, DATETIME('now'));"
        try:
            self.connection.execute(command, (name, number_of_readings, distance_sensor_fuzziness, angle_sensor_fuzziness, distance_moved_fuzziness, angle_rotated_fuzziness))
        except sqlite3.IntegrityError:
            # Robot Name already exists, so add a number in brackets after the name, until a non-duplicate is accepted
            iteration = 2

            while True:
                extended_name = name + f"({iteration})"
                try:
                    self.connection.execute(command, (extended_name, number_of_readings, distance_sensor_fuzziness, angle_sensor_fuzziness, distance_moved_fuzziness, angle_rotated_fuzziness))
                except sqlite3.IntegrityError:
                    iteration += 1
                else:
                    name = extended_name
                    break

        self.connection.commit()
        return name

    def get_robot_by_name(self, name):
        command = "SELECT NumberOfReadings, DistanceSensorFuzziness, AngleSensorFuzziness, DistanceMovedFuzziness, AngleRotatedFuzziness " \
                  "FROM Robot WHERE Name=?"
        robot_data = self.connection.execute(command, (name,)).fetchone()
        return robot_data

    def add_room(self, room_name, size, rects):
        room_insert_command = "INSERT INTO Room VALUES (Null, ?, ?, ?, DATETIME('now'));"
        try:
            self.connection.execute(room_insert_command, (room_name, size[0], size[1]))
        except sqlite3.IntegrityError:
            # Room Name already exists, so add a number in brackets after the name, until a non-duplicate is accepted
            iteration = 2

            while True:
                extended_room_name = room_name + f"({iteration})"
                try:
                    self.connection.execute(room_insert_command, (extended_room_name, size[0], size[1]))
                except sqlite3.IntegrityError:
                    iteration += 1
                else:
                    room_name = extended_room_name
                    break

        get_room_id_command = "SELECT RoomID FROM Room WHERE NAME = ?;"
        room_id = self.connection.execute(get_room_id_command, (room_name,)).fetchone()[0]

        if rects:
            # Build up the INSERT statement, and flatten the list of rects into a single list
            rect_insert_command = "INSERT INTO Rectangle VALUES "
            flat_rect_list = []
            for rect in rects:
                rect_insert_command += "(Null, ?, ?, ?, ?, ?, ?), "
                flat_rect_list += rect + [room_id]
            rect_insert_command = rect_insert_command[:-2] + ";"

            self.connection.execute(rect_insert_command, flat_rect_list)

        self.connection.commit()
        return room_name

    def add_scenario(self, scenario_name, room_name, robot_name, square_size, cartographer_grid, robot_x, robot_y, robot_angle):
        command = "INSERT INTO Scenario VALUES (Null, ?," \
                  "(SELECT RoomID FROM Room WHERE Name=?)," \
                  "(SELECT RobotID FROM Robot WHERE Name=?)," \
                  "?, ?, ?, ?, ?, DATETIME('now'));"
        try:
            self.connection.execute(command, (scenario_name, room_name, robot_name, square_size, json.dumps(cartographer_grid), robot_x, robot_y, robot_angle))
        except sqlite3.IntegrityError:
            iteration = 2
            while True:
                extended_scenario_name = scenario_name + f"({iteration})"
                try:
                    self.connection.execute(command, (extended_scenario_name, room_name, robot_name, square_size, json.dumps(cartographer_grid), robot_x, robot_y, robot_angle))
                except sqlite3.IntegrityError:
                    iteration += 1

        self.connection.commit()

    def get_rects_by_room_name(self, name):
        command = "SELECT Rectangle.X, Rectangle.Y, Rectangle.Width, Rectangle.Height, Rectangle.Angle " \
                  "FROM Rectangle INNER JOIN Room ON Rectangle.RoomID=Room.RoomID " \
                  "WHERE Room.Name=?;"
        rect_cursor = self.connection.execute(command, (name,))
        rects = rect_cursor.fetchall()
        return rects

    def get_room_width_height_by_room_name(self, name):
        command = "SELECT Width, Height FROM Room WHERE Name = ?"
        returned = self.connection.execute(command, (name,)).fetchone()
        if returned is None:
            width, height = None, None
        else:
            width, height = returned
        return width, height

    def get_names_in_table(self, table_name):
        command = "SELECT Name FROM ? ORDER BY DateUsed DESC;"
        # Can't use normal SQL parameters, as ? is an SQL object in this case. `column_name` is not user input anyway
        command = command.replace("?", table_name)
        cursor = self.connection.execute(command)
        names = cursor.fetchall()
        get_first_item = lambda li: li[0]
        names = map(get_first_item, names)
        return names

    def get_scenario_by_name(self, scenario_name):
        command = "SELECT Robot.Name, Room.Name, Scenario.SquareSize, " \
                  "Scenario.CartographerGrid, Scenario.RobotPosX, " \
                  "Scenario.RobotPosY, Scenario.RobotAngle " \
                  "FROM Scenario " \
                  "INNER JOIN Robot on Robot.RobotID=Scenario.RobotID " \
                  "INNER JOIN Room on Room.RoomID=Scenario.RoomID " \
                  "WHERE Scenario.Name = ?;"

        scenario_data = self.connection.execute(command, (scenario_name,)).fetchone()
        return scenario_data

    def update_date_used(self, tables, names):
        for table, name in zip(tables, names):
            robot_command = "UPDATE <table> SET DateUsed=DATETIME('now') WHERE Name = ?"
            robot_command = robot_command.replace("<table>", table)
            self.connection.execute(robot_command, (name,))

        self.connection.commit()

    def delete_robot(self, name):
        command = "DELETE FROM Robot WHERE Name = ?;"
        self.connection.execute(command, (name,))
        self.connection.commit()

    def delete_room(self, name):
        command = "DELETE FROM Rectangle WHERE RoomID =" \
                  " (SELECT RoomID FROM Room WHERE Name = ?);"
        self.connection.execute(command, (name,))

        command = "DELETE FROM Room WHERE Name = ?;"
        self.connection.execute(command, (name,))
        self.connection.commit()

    def delete_scenario(self, name):
        command = "DELETE FROM Scenario WHERE Name = ?;"
        self.connection.execute(command, (name,))

        self.connection.commit()

if __name__ == '__main__':
    d = DatabaseManager()
    d.setup_database()