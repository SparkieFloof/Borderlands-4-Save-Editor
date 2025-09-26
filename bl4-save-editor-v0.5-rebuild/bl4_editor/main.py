from PySide6 import QtWidgets
from pathlib import Path
from bl4_editor.ui.mainwindow import MainWindow
from bl4_editor.ui import default_ui

def load_theme(app):
    qss_path = Path("qss/example-purple.qss")
    if qss_path.exists():
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            return
        except Exception:
            pass
    # fallback
    default_ui.apply_default_theme(app)

def main():
    app = QtWidgets.QApplication([])
    load_theme(app)
    win = MainWindow()
    win.show()
    app.exec()

if __name__ == "__main__":
    main()