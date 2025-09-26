from PySide6 import QtWidgets
from typing import Any, Dict
from bl4_editor.ui.profile_tab import ProfileTree

class ProfileSubTab(QtWidgets.QWidget):
    def __init__(self, title: str, key: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.title = title
        v = QtWidgets.QVBoxLayout(self)
        self.tree = ProfileTree()
        v.addWidget(self.tree)
        self.data = {}

    def load_data(self, data: Dict[str, Any]):
        self.data = data or {}
        sub = self.data.get(self.key, {})
        if sub is None:
            sub = {}
        self.tree.build_from(self.key, sub)