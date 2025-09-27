from PySide6 import QtWidgets
from bl4_editor.ui.widgets.profile_tree import ProfileTree


class UnlockablesTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        layout = QtWidgets.QVBoxLayout(self)
        self.tree = ProfileTree(self)
        layout.addWidget(self.tree)

    def load_data(self, d):
        self.data = d or {}
        self.tree.build_from('unlockables', self.data)

    def save_data(self):
        return self.data
