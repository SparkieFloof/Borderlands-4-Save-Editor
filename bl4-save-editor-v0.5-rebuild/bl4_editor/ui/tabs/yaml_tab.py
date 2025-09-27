from PySide6 import QtWidgets, QtGui, QtCore
import yaml


class YAMLSyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        # comment
        fmt_comment = QtGui.QTextCharFormat()
        fmt_comment.setForeground(QtGui.QColor('#6a9955'))
        self._rules.append((QtCore.QRegularExpression(r'#.*'), fmt_comment))

        # keys (start of line, up to colon)
        fmt_key = QtGui.QTextCharFormat()
        fmt_key.setForeground(QtGui.QColor('#9cdcfe'))
        fmt_key.setFontWeight(QtGui.QFont.Bold)
        self._rules.append((QtCore.QRegularExpression(r'^\s*[^:\n]+(?=:)'), fmt_key))

        # strings in quotes
        fmt_string = QtGui.QTextCharFormat()
        fmt_string.setForeground(QtGui.QColor('#ce9178'))
        self._rules.append((QtCore.QRegularExpression(r'".*?"'), fmt_string))
        self._rules.append((QtCore.QRegularExpression(r"'.*?'"), fmt_string))

        # booleans/null
        fmt_bool = QtGui.QTextCharFormat()
        fmt_bool.setForeground(QtGui.QColor('#569cd6'))
        self._rules.append((QtCore.QRegularExpression(r'\b(true|false|null)\b'), fmt_bool))

        # numbers
        fmt_num = QtGui.QTextCharFormat()
        fmt_num.setForeground(QtGui.QColor('#b5cea8'))
        self._rules.append((QtCore.QRegularExpression(r'\b[-+]?[0-9]+(\.[0-9]+)?\b'), fmt_num))


    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                start = m.capturedStart()
                length = m.capturedLength()
                self.setFormat(start, length, fmt)


class YamlTab(QtWidgets.QWidget):
    """A simple YAML editor tab that shows raw YAML and can parse it back.

    Methods:
    - set_yaml(data): populate the editor with YAML text for `data`
    - get_yaml(): parse and return Python object (dict/list) from editor text
    """
    # signal emitted when user edits YAML (after Qt's textChanged)
    text_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = QtWidgets.QPlainTextEdit()
        self.editor.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.editor.setFont(font)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6,6,6,6)
        layout.addWidget(self.editor)
        # syntax highlighter
        self._highlighter = YAMLSyntaxHighlighter(self.editor.document())

        # relay editor changes
        self.editor.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        # emit a simple notification; parsing is left to caller
        try:
            self.text_changed.emit()
        except Exception:
            pass

    def set_yaml(self, data):
        try:
            text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
        except Exception:
            # fallback to a repr
            text = repr(data)
        self.editor.setPlainText(text)

    def get_yaml(self):
        text = self.editor.toPlainText()
        if not text.strip():
            return {}
        try:
            return yaml.safe_load(text)
        except Exception as e:
            # re-raise with context so callers can show a message box
            raise ValueError(f'Invalid YAML: {e}')
