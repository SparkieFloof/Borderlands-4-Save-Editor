from PySide6 import QtWidgets

class ProfileStatsTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QFormLayout(self)
        self.layout.addRow('play_time', QtWidgets.QLineEdit())