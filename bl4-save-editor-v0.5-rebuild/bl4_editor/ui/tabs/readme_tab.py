from PySide6 import QtWidgets
import os


class ReadmeTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.view = QtWidgets.QTextBrowser(self)
        layout.addWidget(self.view)

    def _read_readme_from_project(self) -> str:
        """Attempt to find and read a top-level README.md in the project root.
        Falls back to an empty string on failure."""
        # Try a few likely locations relative to this file
        candidate = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'README.md'))
        if not os.path.exists(candidate):
            # also try workspace root (two levels up from project package)
            candidate = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'README.md'))
        try:
            if os.path.exists(candidate):
                with open(candidate, 'r', encoding='utf-8') as fh:
                    return fh.read()
        except Exception:
            pass
        return ''

    def load_data(self, text=None):
        """Load provided markdown text or, if none provided, load README.md from the project root."""
        if not text:
            text = self._read_readme_from_project()

        try:
            self.view.setMarkdown(text if isinstance(text, str) else str(text))
        except Exception:
            self.view.setPlainText(text if isinstance(text, str) else str(text))

    def save_data(self):
        return None
