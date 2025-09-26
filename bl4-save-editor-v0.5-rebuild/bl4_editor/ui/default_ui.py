# default_ui.py - fallback stylesheet for BL4 Save Editor

def get_default_stylesheet():
    return """
    QMainWindow {
        background-color: #202020;
        color: #ffffff;
    }

    QTabWidget::pane {
        border: 1px solid #444;
        background-color: #202020;
    }

    QTabBar::tab {
        background: #2b2b2b;
        color: #cccccc;
        padding: 6px 12px;
        margin: 2px;
        border-radius: 4px;
    }

    QTabBar::tab:selected {
        background: #6a1b9a; /* purple highlight */
        color: #ffffff;
    }

    QPushButton {
        background-color: #2b2b2b;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #ffffff;
    }
    QPushButton:hover {
        background-color: #3a3a3a;
    }

    QLineEdit {
        background-color: #2b2b2b;
        border: 1px solid #555;
        color: #ffffff;
        padding: 2px 4px;
        border-radius: 4px;
    }

    /* User ID field validation states */
    QLineEdit#UserIDField[valid="true"] {
        background-color: #d4f8d4; /* soft mint green */
        border: 1px solid #3c763d;
        color: #222222;  /* dark text for readability */
    }

    QLineEdit#UserIDField[valid="false"] {
        background-color: #f8d4d4; /* soft pink */
        border: 1px solid #a94442;
        color: #222222;  /* dark text again */
    }
    """


def apply_default_theme(app):
    """Apply the fallback theme to the whole QApplication."""
    app.setStyleSheet(get_default_stylesheet())
