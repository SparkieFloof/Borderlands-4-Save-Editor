from PySide6 import QtWidgets, QtCore
from pathlib import Path

class ThemeTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QtWidgets.QVBoxLayout(self)
        h = QtWidgets.QHBoxLayout()
        self.combo = QtWidgets.QComboBox(); self.combo.addItems(["Dark","Light","Load .qss"]); h.addWidget(self.combo)
        self.btn_load = QtWidgets.QPushButton("Load .qss"); h.addWidget(self.btn_load)
        v.addLayout(h)
        self.btn_load.clicked.connect(self.load_qss)
        self.example_qss = Path.cwd() / "example-purple.qss"

    def load_qss(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load .qss", filter="Stylesheet (*.qss);;All Files (*)")
        if not p: return
        try:
            txt = Path(p).read_text(encoding="utf-8", errors="ignore")
            QtWidgets.QApplication.instance().setStyleSheet(txt)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Theme load failed", str(e))