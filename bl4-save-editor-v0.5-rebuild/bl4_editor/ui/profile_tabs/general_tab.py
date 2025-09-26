from PySide6 import QtWidgets

class GeneralTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QFormLayout(self)
        # placeholder fields
        self.layout.addRow('last_played', QtWidgets.QLineEdit())