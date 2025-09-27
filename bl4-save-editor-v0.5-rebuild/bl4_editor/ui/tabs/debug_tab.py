from PySide6 import QtWidgets, QtCore


class DebugTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.text = QtWidgets.QPlainTextEdit(self)
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

    def append_log(self, level: str, msg: str, category: str = None):
        ts = QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        cur = self.text.toPlainText() or ''
        cat = f'[{category}] ' if category else ''
        cur += f'[{ts}] {level.upper()}: {cat}{msg}\n'
        if len(cur) > 20000:
            cur = cur[-20000:]
        self.text.setPlainText(cur)
        self.text.verticalScrollBar().setValue(self.text.verticalScrollBar().maximum())

    def load_data(self, d):
        # Debug has no model to load
        pass

    def save_data(self):
        return {}
