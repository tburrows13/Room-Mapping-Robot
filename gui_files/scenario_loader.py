from database_manager import DatabaseManager

from PyQt5.QtWidgets import *

class ScenarioLoader(QDialog):
    def __init__(self):
        super(ScenarioLoader, self).__init__()
        self.setWindowTitle("Load Scenario")


        main_layout = QVBoxLayout()
        self.database = DatabaseManager()

        self.scenario_select = QComboBox()
        scenarios = self.database.get_names_in_table("Scenario")
        self.scenario_select.addItems(scenarios)
        main_layout.addWidget(self.scenario_select)

        self.done_button = QPushButton("Done")
        main_layout.addWidget(self.done_button)
        self.done_button.clicked.connect(self.close)
        self.done_button.setDefault(True)

        self.setLayout(main_layout)

    def close(self):
        scenario_name = self.scenario_select.currentText()
        self.database.update_date_used(("Scenario",),  (scenario_name,))
        self.database.connection.close()
        super(ScenarioLoader, self).close()
