import csv

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal

from database_manager import DatabaseManager

DEFAULT_SQUARE_SIZE = 10


class ConfigDialog(QDialog):
    def __init__(self, previous_start_pos, previous_square_size):
        super(ConfigDialog, self).__init__()
        self.setWindowTitle("Configure Settings")

        self.database = DatabaseManager()
        self.main_layout = QVBoxLayout()

        # Robot select
        self.robot_layout = RobotSelect(self.database)
        self.main_layout.addLayout(self.robot_layout)

        # Room select
        self.room_layout = RoomSelect(self.database, previous_start_pos, self.validate_input)
        self.main_layout.addLayout(self.room_layout)

        # Square size
        self.square_size_layout = QHBoxLayout()
        self.square_size_label = QLabel("Square Size: ")
        self.square_size_text_edit = QLineEdit()
        if previous_square_size is None:
            previous_square_size = DEFAULT_SQUARE_SIZE
        self.square_size_text_edit.setText(str(previous_square_size))

        self.square_size_layout.addWidget(self.square_size_label)
        self.square_size_layout.addWidget(self.square_size_text_edit)
        self.main_layout.addLayout(self.square_size_layout)

        # Done button
        self.done_button = QPushButton("Done")
        self.main_layout.addWidget(self.done_button)
        self.done_button.clicked.connect(self.close)
        self.done_button.setDefault(True)
        self.robot_layout.set_main_button_default.connect(self.done_button.setDefault)
        self.robot_layout.set_main_button_default.connect(self.done_button.repaint)

        # Get all info together for input validation
        self.start_pos_line_edits = self.room_layout.get_start_pos_line_edits()
        self.room_select_dropdown = self.room_layout.room_select_dropdown
        self.robot_select_dropdown = self.robot_layout.robot_select_dropdown

        self.start_pos_line_edits[0].textChanged.connect(self.validate_input)
        self.start_pos_line_edits[1].textChanged.connect(self.validate_input)
        self.room_select_dropdown.currentIndexChanged.connect(self.validate_input)
        self.robot_select_dropdown.currentIndexChanged.connect(self.validate_input)
        self.square_size_text_edit.textChanged.connect(self.validate_input)
        self.validate_input()

        self.setLayout(self.main_layout)

    def validate_input(self):
        start_x = self.start_pos_line_edits[0].text()
        start_y = self.start_pos_line_edits[1].text()
        robot_dropdown_text = self.robot_select_dropdown.currentText()
        room_dropdown_text = self.room_select_dropdown.currentText()
        square_size = self.square_size_text_edit.text()

        valid = self.validate_values(start_x, start_y, robot_dropdown_text, room_dropdown_text, square_size)

        if valid:
            self.done_button.setDisabled(False)
            self.done_button.repaint()
        else:
            self.done_button.setDisabled(True)
            self.done_button.repaint()

    def validate_values(self, x, y, robot_dropdown_text, room_dropdown_text, square_size):
        # room_dropdown_text must not be empty
        if room_dropdown_text == "":
            return False

        # robot_dropdown_text must not be empty
        if robot_dropdown_text == "":
            return False

        width, height = self.database.get_room_width_height_by_room_name(room_dropdown_text)

        # x must be a positive integer between 0 and <width>
        try:
            x = int(x)
        except ValueError:
            return False
        if x <= 0 or x >= width:
            return False

        # y must be a positive integer between 0 and <width>
        try:
            y = int(y)
        except ValueError:
            return False
        if y <= 0 or y >= height:
            return False

        # square_size must be an integer that is a factor of both width and height and < 0
        try:
            square_size = int(square_size)
        except ValueError:
            return False

        if square_size <= 0:
            return False

        if width % square_size != 0:
            return False
        if height % square_size != 0:
            return False

        return True

    def close(self):
        robot_name = self.robot_layout.robot_select_dropdown.currentText()
        room_name = self.room_layout.room_select_dropdown.currentText()

        self.database.update_date_used(("Robot", "Room"), (robot_name, room_name))
        self.database.connection.close()
        self.done(1)


class RobotSelect(QVBoxLayout):
    set_main_button_default = pyqtSignal(bool)

    def __init__(self, database):
        super(RobotSelect, self).__init__()
        self.database = database

        # ----- Select robot from existing list -----
        self.robot_select_layout = QVBoxLayout()
        robot_label = QLabel("Robot:")
        self.robot_select_layout.addWidget(robot_label)

        robot_select_layout = QHBoxLayout()
        self.robot_select_dropdown = QComboBox()
        robot_names = self.database.get_names_in_table("Robot")
        self.robot_select_dropdown.addItems(robot_names)
        self.robot_select_dropdown.setCurrentIndex(0)

        self.robot_delete_button = QPushButton("Delete")
        self.robot_delete_button.clicked.connect(self.delete_record)

        robot_select_layout.addWidget(self.robot_select_dropdown)
        robot_select_layout.addWidget(self.robot_delete_button)
        self.robot_select_layout.addLayout(robot_select_layout)

        self.addLayout(self.robot_select_layout)

        # ----- Create new robot -----
        self.robot_input_form = QVBoxLayout()
        self.form = QFormLayout()
        self.row_line_edits = []

        row_names = ["Name", "Number of Readings", "Distance Sensor Fuzziness", "Angle Sensor Fuzziness", "Distance Moved Fuzziness", "Angle Rotated Fuzziness"]
        for name in row_names:
            line_edit = QLineEdit()
            self.row_line_edits.append(line_edit)
            self.form.addRow(name, line_edit)

        self.add_robot_button = QPushButton("Add")
        self.add_robot_button.clicked.connect(self.add_robot)

        for line_edit in self.row_line_edits:
            line_edit.textChanged.connect(self.validate_input)
        self.validate_input()  # To disable the button from the start

        self.robot_input_form.addLayout(self.form)
        self.robot_input_form.addWidget(self.add_robot_button)

        self.addLayout(self.robot_input_form)

    def validate_input(self):
        # Also change the default button
        self.add_robot_button.setDefault(True)
        self.add_robot_button.repaint()

        name = self.row_line_edits[0].text()
        number_of_readings = self.row_line_edits[1].text()
        fuzziness_values = []
        for fuzziness_line_edit in self.row_line_edits[2:]:
            fuzziness_values.append(fuzziness_line_edit.text())

        valid = self.validate_values(name, number_of_readings, fuzziness_values)
        if valid:
            self.add_robot_button.setDisabled(False)
            self.add_robot_button.repaint()
        else:
            self.add_robot_button.setDisabled(True)
            self.add_robot_button.repaint()

    def validate_values(self, name, number_of_readings, fuzziness_values):
        # Name must have a value
        if name == "":
            return False

        # Number of Readings must be a non-zero positive integer
        try:
            integer = int(number_of_readings)
        except ValueError:
            return False
        else:
            if integer <= 0 or integer > 720:
                return False

        # Each of the fuzziness values must be a positive, including zero, float
        for value in fuzziness_values:
            try:
                number = float(value)
            except ValueError:
                return False
            else:
                if number < 0:
                    return False
        return True

    def add_robot(self):
        """
        Gather data from the text edits and send it to the database
        """
        args = []
        for line_edit in self.row_line_edits:
            args.append(line_edit.text())

        actual_name = self.database.add_robot(*args)
        args[0] = actual_name
        self.robot_select_dropdown.insertItem(0, args[0])
        self.robot_select_dropdown.setCurrentIndex(0)
        self.robot_select_dropdown.repaint()
        self.add_robot_button.setDefault(False)
        self.add_robot_button.repaint()
        self.set_main_button_default.emit(True)

    def delete_record(self):
        to_delete = self.robot_select_dropdown.currentText()
        self.database.delete_robot(to_delete)
        self.robot_select_dropdown.removeItem(self.robot_select_dropdown.currentIndex())


class RoomSelect(QVBoxLayout):
    def __init__(self, database, default_start_pos, validate_start_pos):
        super(RoomSelect, self).__init__()
        self.validate_start_pos = validate_start_pos
        self.database = database

        # ----- Select room from existing list -----
        self.room_select_layout = QVBoxLayout()
        room_label = QLabel("Room:")
        self.room_select_layout.addWidget(room_label)

        drop_down_and_delete_layout = QHBoxLayout()
        self.room_select_dropdown = QComboBox()
        room_names = self.database.get_names_in_table("Room")
        self.room_select_dropdown.addItems(room_names)
        self.room_select_dropdown.currentIndexChanged.connect(self.update_start_pos)
        drop_down_and_delete_layout.addWidget(self.room_select_dropdown)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_record)
        drop_down_and_delete_layout.addWidget(delete_button)
        self.room_select_layout.addLayout(drop_down_and_delete_layout)

        self.addLayout(self.room_select_layout)

        # ----- Select new room file -----
        open_file_button = QPushButton("Open file...")
        open_file_button.clicked.connect(self.open_file)
        self.addWidget(open_file_button)

        start_pos_layout = QHBoxLayout()
        start_pos_layout.addWidget(QLabel("Start position:"))
        self.start_pos_x = QLineEdit()
        self.start_pos_y = QLineEdit()

        start_pos_layout.addWidget(self.start_pos_x)
        start_pos_layout.addWidget(self.start_pos_y)

        # Down here so that the connected slot can change the start pos form
        self.room_select_dropdown.setCurrentIndex(0)
        if default_start_pos is not None:
            self.start_pos_x.setText(str(default_start_pos[0]))
            self.start_pos_y.setText(str(default_start_pos[1]))
        else:
            self.update_start_pos()

        self.addLayout(start_pos_layout)

    def get_start_pos_line_edits(self):
        return self.start_pos_x, self.start_pos_y

    def update_start_pos(self):
        newly_selected_room_name = self.room_select_dropdown.currentText()
        self.width, self.height = self.database.get_room_width_height_by_room_name(newly_selected_room_name)
        if self.width is not None and self.height is not None:
            self.start_pos_x.setText(str(int(self.width // 2)))
            self.start_pos_y.setText(str(int(self.height // 2)))

    def open_file(self):
        filename = QFileDialog.getOpenFileName(filter="Text files (*.csv)")[0]
        if filename == "":
            return
        else:
            filename_end = filename.split("/")[-1].split(".")[0]

            with open(filename) as csvfile:
                is_valid, rects, size = self.extract_file(csvfile)

            if is_valid:
                final_room_name = self.database.add_room(filename_end, size, rects)

                self.room_select_dropdown.insertItem(0, final_room_name)
                self.room_select_dropdown.setCurrentIndex(0)
                self.room_select_dropdown.repaint()

            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText("Invalid file format")
                msg.setWindowTitle("Error")
                msg.exec_()

    def extract_file(self, file):
        """Returns True and the file contents if it is valid; otherwise, returns False and empty lists"""
        reader = list(csv.reader(file))
        if not reader:
            # file is empty
            return False, [], []

        size = reader[0]
        rects = reader[1:]

        if len(size) != 2:
            return False, [], []

        try:
            width = int(size[0])
            height = int(size[1])
        except ValueError:
            return False, [], []

        if width < 10 or height < 10 or width > 800 or height > 800:
            return False, [], []

        for rect in rects:
            if len(rect) != 5:
                return False, [], []

            try:
                rect = list(map(int, rect))
            except ValueError:
                return False, [], []

            for value in rect[:4]:
                if value <= 0:
                    return False, [], []

        return True, rects, (width, height)

    def delete_record(self):
        to_delete = self.room_select_dropdown.currentText()
        self.database.delete_room(to_delete)
        self.room_select_dropdown.removeItem(self.room_select_dropdown.currentIndex())
        self.update_start_pos()
