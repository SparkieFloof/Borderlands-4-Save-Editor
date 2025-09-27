from PySide6 import QtWidgets
from bl4_editor.core import settings as core_settings
from PySide6 import QtGui
import os


class UISettingsTab(QtWidgets.QWidget):
    """UI settings tab: simplified theme options and color-based QSS builder.

    This tab allows picking hover/tab/text/toolbar colors and can auto-build a QSS
    file from those choices. It calls an optional apply_callback(css, theme)
    for live preview.
    """

    def __init__(self, apply_callback=None):
        super().__init__()
        self.apply_callback = apply_callback
        layout = QtWidgets.QVBoxLayout(self)

        # Theme selector (System or Dark only)
        theme_layout = QtWidgets.QHBoxLayout()
        theme_layout.addWidget(QtWidgets.QLabel('Theme:'))
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(['System', 'Dark'])
        saved = core_settings.get_setting('ui_theme', 'System')
        idx = self.theme_combo.findText(saved)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Stylesheet editor
        layout.addWidget(QtWidgets.QLabel('Custom Qt Stylesheet (live preview)'))
        self.stylesheet_edit = QtWidgets.QPlainTextEdit()
        self.stylesheet_edit.setPlainText(core_settings.get_setting('custom_stylesheet', ''))
        self.stylesheet_edit.setPlaceholderText('Enter Qt stylesheet here (QWidget { background: #fff; })')
        layout.addWidget(self.stylesheet_edit, 1)

        # Buttons: Apply, Save, Reset, Build QSS, Save/Load QSS
        btn_layout = QtWidgets.QHBoxLayout()
        self.apply_btn = QtWidgets.QPushButton('Apply')
        self.save_btn = QtWidgets.QPushButton('Save')
        self.reset_btn = QtWidgets.QPushButton('Reset')
        self.build_qss_btn = QtWidgets.QPushButton('Build QSS from colors')
        self.qss_save_btn = QtWidgets.QPushButton('Save to QSS')
        self.qss_load_btn = QtWidgets.QPushButton('Load QSS')

        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.build_qss_btn)
        btn_layout.addWidget(self.qss_save_btn)
        btn_layout.addWidget(self.qss_load_btn)
        layout.addLayout(btn_layout)

        # Wire buttons
        self.apply_btn.clicked.connect(self.on_apply)
        self.save_btn.clicked.connect(self.on_save)
        self.reset_btn.clicked.connect(self.on_reset)
        self.build_qss_btn.clicked.connect(self._build_qss_from_colors)
        self.qss_save_btn.clicked.connect(self._save_to_qss)
        self.qss_load_btn.clicked.connect(self._load_qss)

        # Color pickers: hover, tab, text, toolbar
        color_grid = QtWidgets.QGridLayout()
        color_grid.addWidget(QtWidgets.QLabel('Hover color:'), 0, 0)
        self.hover_color_btn = QtWidgets.QPushButton('Pick...')
        color_grid.addWidget(self.hover_color_btn, 0, 1)
        color_grid.addWidget(QtWidgets.QLabel('Tab color:'), 0, 2)
        self.tab_color_btn = QtWidgets.QPushButton('Pick...')
        color_grid.addWidget(self.tab_color_btn, 0, 3)

        color_grid.addWidget(QtWidgets.QLabel('Text color:'), 1, 0)
        self.text_color_btn = QtWidgets.QPushButton('Pick...')
        color_grid.addWidget(self.text_color_btn, 1, 1)
        color_grid.addWidget(QtWidgets.QLabel('Toolbar color:'), 1, 2)
        self.toolbar_color_btn = QtWidgets.QPushButton('Pick...')
        color_grid.addWidget(self.toolbar_color_btn, 1, 3)
        # Tab spacing and selected tab color
        color_grid.addWidget(QtWidgets.QLabel('Tab spacing (px):'), 2, 0)
        self.tab_spacing_spin = QtWidgets.QSpinBox()
        self.tab_spacing_spin.setRange(0, 32)
        try:
            self.tab_spacing_spin.setValue(int(core_settings.get_setting('ui_tab_spacing', 6)))
        except Exception:
            self.tab_spacing_spin.setValue(6)
        color_grid.addWidget(self.tab_spacing_spin, 2, 1)
        color_grid.addWidget(QtWidgets.QLabel('Selected tab color:'), 2, 2)
        self.selected_tab_btn = QtWidgets.QPushButton('Pick...')
        color_grid.addWidget(self.selected_tab_btn, 2, 3)
        layout.insertLayout(1, color_grid)

        self.hover_color_btn.clicked.connect(lambda: self._pick_color('hover'))
        self.tab_color_btn.clicked.connect(lambda: self._pick_color('tab'))
        self.text_color_btn.clicked.connect(lambda: self._pick_color('text'))
        self.toolbar_color_btn.clicked.connect(lambda: self._pick_color('toolbar'))
        # selected tab color
        try:
            self.selected_tab_btn.clicked.connect(lambda: self._pick_color('selected'))
        except Exception:
            pass

        # Load persisted UI color settings into the color button tooltips and show color swatches
        try:
            hover = core_settings.get_setting('ui_hover_color', '')
            tabc = core_settings.get_setting('ui_tab_color', '')
            textc = core_settings.get_setting('ui_text_color', '')
            toolc = core_settings.get_setting('ui_toolbar_color', '')
            if hover:
                self.hover_color_btn.setToolTip(hover)
                self.hover_color_btn.setStyleSheet(f'background:{hover}')
            if tabc:
                self.tab_color_btn.setToolTip(tabc)
                self.tab_color_btn.setStyleSheet(f'background:{tabc}')
            if textc:
                self.text_color_btn.setToolTip(textc)
                self.text_color_btn.setStyleSheet(f'background:{textc}')
            if toolc:
                self.toolbar_color_btn.setToolTip(toolc)
                self.toolbar_color_btn.setStyleSheet(f'background:{toolc}')
            try:
                sel = core_settings.get_setting('ui_selected_tab_color', '')
                if sel:
                    self.selected_tab_btn.setToolTip(sel)
                    self.selected_tab_btn.setStyleSheet(f'background:{sel}')
            except Exception:
                pass
            try:
                self.tab_spacing_spin.setValue(int(core_settings.get_setting('ui_tab_spacing', 6)))
            except Exception:
                pass
        except Exception:
            pass

    def on_apply(self):
        css = self.stylesheet_edit.toPlainText()
        if callable(self.apply_callback):
            self.apply_callback(css, self.theme_combo.currentText())

    def on_save(self):
        css = self.stylesheet_edit.toPlainText()
        core_settings.set_setting('custom_stylesheet', css)
        core_settings.set_setting('ui_theme', self.theme_combo.currentText())
        # persist QSS path (if set) and write the css to it
        qss_path = core_settings.get_setting('qss_path', '')
        try:
            if qss_path:
                with open(qss_path, 'w', encoding='utf-8') as f:
                    f.write(css)
        except Exception:
            pass

        # Persist picked colors (read from tooltips)
        try:
            hover = self.hover_color_btn.toolTip() or ''
            tabc = self.tab_color_btn.toolTip() or ''
            textc = self.text_color_btn.toolTip() or ''
            toolc = self.toolbar_color_btn.toolTip() or ''
            if hover:
                core_settings.set_setting('ui_hover_color', hover)
            if tabc:
                core_settings.set_setting('ui_tab_color', tabc)
            if textc:
                core_settings.set_setting('ui_text_color', textc)
            if toolc:
                core_settings.set_setting('ui_toolbar_color', toolc)
            # selected tab color and spacing
            try:
                sel = self.selected_tab_btn.toolTip() if hasattr(self, 'selected_tab_btn') else ''
                if sel:
                    core_settings.set_setting('ui_selected_tab_color', sel)
            except Exception:
                pass
            try:
                spacing = int(self.tab_spacing_spin.value()) if hasattr(self, 'tab_spacing_spin') else None
                if spacing is not None:
                    core_settings.set_setting('ui_tab_spacing', spacing)
            except Exception:
                pass
        except Exception:
            pass

        if callable(self.apply_callback):
            self.apply_callback(css, self.theme_combo.currentText())

    def on_reset(self):
        core_settings.set_setting('custom_stylesheet', '')
        self.stylesheet_edit.setPlainText('')
        core_settings.set_setting('ui_theme', 'System')
        idx = self.theme_combo.findText('System')
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        if callable(self.apply_callback):
            self.apply_callback('', 'System')

    def _live_apply(self):
        # Called as the user edits the stylesheet or changes theme
        css = self.stylesheet_edit.toPlainText()
        theme = self.theme_combo.currentText()
        if callable(self.apply_callback):
            try:
                self.apply_callback(css, theme)
            except Exception:
                # Ignore exceptions from faulty styles during live preview
                pass

    def _build_qss_from_colors(self):
        # Read colors from tooltips and construct a minimal QSS
        hover = core_settings.get_setting('ui_hover_color', '') or self.hover_color_btn.toolTip() or '#3a3a3a'
        tabc = core_settings.get_setting('ui_tab_color', '') or self.tab_color_btn.toolTip() or '#2b2b2b'
        textc = core_settings.get_setting('ui_text_color', '') or self.text_color_btn.toolTip() or '#e6e6e6'
        toolc = core_settings.get_setting('ui_toolbar_color', '') or self.toolbar_color_btn.toolTip() or '#272727'
        selc = core_settings.get_setting('ui_selected_tab_color', '') or (self.selected_tab_btn.toolTip() if hasattr(self, 'selected_tab_btn') else '') or '#3d7bd9'
        spacing = core_settings.get_setting('ui_tab_spacing', None)
        try:
            if spacing is None:
                spacing = self.tab_spacing_spin.value() if hasattr(self, 'tab_spacing_spin') else 6
            spacing = int(spacing)
        except Exception:
            spacing = 6

        qss = []
        # Toolbar
        qss.append(f"QToolBar {{ background: {toolc}; color: {textc}; }}")
        qss.append(f"QToolButton, QPushButton {{ color: {textc}; }}")
        # Tabs
        qss.append(f"QTabBar::tab {{ background: {tabc}; color: {textc}; padding-left: {spacing}px; padding-right: {spacing}px; }}")
        qss.append(f"QTabBar::tab:selected {{ background: {selc}; }}")
        # Hover
        qss.append(f"QToolButton:hover, QPushButton:hover {{ background: {hover}; }}")
        # General widget text
        qss.append(f"QWidget {{ color: {textc}; }}")

        built = '\n'.join(qss)
        self.stylesheet_edit.setPlainText(built)
        # Apply live
        if callable(self.apply_callback):
            self.apply_callback(built, self.theme_combo.currentText())
        # Also update tooltips and style previews on buttons
        try:
            self.hover_color_btn.setToolTip(hover)
            self.hover_color_btn.setStyleSheet(f'background:{hover}')
            self.tab_color_btn.setToolTip(tabc)
            self.tab_color_btn.setStyleSheet(f'background:{tabc}')
            self.text_color_btn.setToolTip(textc)
            self.text_color_btn.setStyleSheet(f'background:{textc}')
            self.toolbar_color_btn.setToolTip(toolc)
            self.toolbar_color_btn.setStyleSheet(f'background:{toolc}')
        except Exception:
            pass

    def _save_to_qss(self):
        # write current stylesheet to qss file specified in settings (or ask)
        css = self.stylesheet_edit.toPlainText()
        qss_path = core_settings.get_setting('qss_path', '')
        if not qss_path:
            qss_path, ok = QtWidgets.QInputDialog.getText(self, 'QSS Path', 'Enter path for QSS file (relative to cwd):', text='app_custom.qss')
            if not ok or not qss_path:
                return
            core_settings.set_setting('qss_path', qss_path)
        try:
            with open(qss_path, 'w', encoding='utf-8') as f:
                f.write(css)
            QtWidgets.QMessageBox.information(self, 'Saved', f'Wrote QSS to {qss_path}')
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Save failed', str(e))

    def _load_qss(self):
        qss_path = core_settings.get_setting('qss_path', '')
        if not qss_path or not os.path.exists(qss_path):
            qss_path, ok = QtWidgets.QFileDialog.getOpenFileName(self, 'Open QSS', os.getcwd(), 'QSS Files (*.qss);;All Files (*)')
            if not qss_path:
                return
            core_settings.set_setting('qss_path', qss_path)
        try:
            with open(qss_path, 'r', encoding='utf-8') as f:
                css = f.read()
            self.stylesheet_edit.setPlainText(css)
            if callable(self.apply_callback):
                self.apply_callback(css, self.theme_combo.currentText())
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Load failed', str(e))

    def _pick_color(self, which: str):
        dlg = QtWidgets.QColorDialog(self)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        col = dlg.selectedColor()
        if not col.isValid():
            return
        hexcol = col.name()

        # Map which -> button so we can update tooltip and preview
        try:
            if which == 'hover':
                btn = self.hover_color_btn
                core_settings.set_setting('ui_hover_color', hexcol)
            elif which == 'tab':
                btn = self.tab_color_btn
                core_settings.set_setting('ui_tab_color', hexcol)
            elif which == 'text':
                btn = self.text_color_btn
                core_settings.set_setting('ui_text_color', hexcol)
            elif which == 'toolbar':
                btn = self.toolbar_color_btn
                core_settings.set_setting('ui_toolbar_color', hexcol)
            else:
                btn = None
        except Exception:
            btn = None

        # Update the button UI (tooltip + swatch)
        try:
            if btn is not None:
                btn.setToolTip(hexcol)
                btn.setStyleSheet(f'background:{hexcol}')
        except Exception:
            pass

        # Rebuild the QSS from current colors and apply for live preview
        try:
            self._build_qss_from_colors()
        except Exception:
            # Fallback: append a minimal rule into the editor and apply
            try:
                rule = f"QWidget {{ background-color: {hexcol}; }}\n" if which == 'background' else f"QPushButton {{ background-color: {hexcol}; }}\n"
                current = self.stylesheet_edit.toPlainText()
                self.stylesheet_edit.setPlainText(current + "\n" + rule)
                if callable(self.apply_callback):
                    try:
                        self.apply_callback(self.stylesheet_edit.toPlainText(), self.theme_combo.currentText())
                    except Exception:
                        pass
            except Exception:
                pass


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog. Optionally accepts apply_callback(css, theme) for live preview."""

    def __init__(self, parent=None, apply_callback=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.resize(800, 600)
        layout = QtWidgets.QVBoxLayout(self)

        self.tabs = QtWidgets.QTabWidget()
        # General settings tab uses existing SettingsTab if present
        try:
            from .tabs.settings_tab import SettingsTab

            self.general_tab = SettingsTab()
            self.tabs.addTab(self.general_tab, 'General')
        except Exception:
            # If the project's SettingsTab isn't available, skip it
            pass

        self.ui_tab = UISettingsTab(apply_callback=apply_callback)
        self.tabs.addTab(self.ui_tab, 'UI')
        layout.addWidget(self.tabs)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        btns.clicked.connect(self._on_btn)
        layout.addWidget(btns)

    def _on_btn(self, btn):
        # Ensure close works
        sender = self.sender()
        try:
            if isinstance(sender, QtWidgets.QDialogButtonBox):
                role = sender.buttonRole(btn)
            else:
                role = None
        except Exception:
            role = None

        if role == QtWidgets.QDialogButtonBox.RejectRole:
            self.reject()
