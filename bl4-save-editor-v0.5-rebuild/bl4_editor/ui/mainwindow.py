# Updated mainwindow.py with proper integration
from PySide6 import QtWidgets, QtGui
import os, re, tempfile, shutil
from bl4_editor.ui.tabs.character_tab import CharacterTab
from bl4_editor.ui.tabs.items_tab import ItemsTab
from bl4_editor.ui.tabs.progression_tab import ProgressionTab
from bl4_editor.ui.tabs.stats_tab import StatsTab
from bl4_editor.ui.tabs.world_tab import WorldTab
from bl4_editor.ui.tabs.unlockables_tab import UnlockablesTab
from bl4_editor.ui.tabs.profile_tab import ProfileTab
from bl4_editor.ui.tabs.yaml_tab import YamlTab
from bl4_editor.ui.tabs.debug_tab import DebugTab
from bl4_editor.ui.tabs.readme_tab import ReadmeTab
from bl4_editor.core.controller import TabController
from bl4_editor.core import fileio
from bl4_editor.core import crypt as crypt_mod
from bl4_editor.core import logger
from bl4_editor.core import settings as core_settings
from bl4_editor.ui.settings_dialog import SettingsDialog
from bl4_editor.ui import default_ui

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BL4 Save Editor - Modular Version')
        self.resize(1200, 800)
        
        # Initialize data attributes
        self.current_yaml_path = None
        # original path (the file the user opened)
        self.current_original_path = None
        self.current_data = None

        # Create tab widget
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tab instances (some are QWidget subclasses, some are logic-only)
        self.character_tab = CharacterTab()
        self.items_tab = ItemsTab()
        self.progression_tab = ProgressionTab()
        self.stats_tab = StatsTab()
        self.world_tab = WorldTab()
        self.unlockables_tab = UnlockablesTab()
        self.profile_tab = ProfileTab()
        self.yaml_tab = YamlTab()
        self.debug_tab = DebugTab()
        self.readme_tab = ReadmeTab()
        # sync suppression flag to avoid back-and-forth updates
        self._yaml_sync_in_progress = False

        # Build display widgets: ensure every entry added to QTabWidget is a QWidget
        def make_display_widget(obj):
            # If object is already a QWidget, return it directly
            if isinstance(obj, QtWidgets.QWidget):
                return obj, obj
            # Otherwise create a simple QWidget container that holds a placeholder
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            lbl = QtWidgets.QLabel(f"{type(obj).__name__} (no GUI)")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)
            layout.addStretch()
            # attach logic object for later use
            container._logic = obj
            return container, obj

        # Prepare display widgets and logic mapping
        self._disp_character, self._logic_character = make_display_widget(self.character_tab)
        self._disp_items, self._logic_items = make_display_widget(self.items_tab)
        self._disp_progression, self._logic_progression = make_display_widget(self.progression_tab)
        self._disp_stats, self._logic_stats = make_display_widget(self.stats_tab)
        self._disp_world, self._logic_world = make_display_widget(self.world_tab)
        self._disp_unlockables, self._logic_unlockables = make_display_widget(self.unlockables_tab)
        self._disp_profile, self._logic_profile = make_display_widget(self.profile_tab)
        self._disp_yaml, self._logic_yaml = make_display_widget(self.yaml_tab)
        self._disp_debug, self._logic_debug = make_display_widget(self.debug_tab)
        self._disp_readme, self._logic_readme = make_display_widget(self.readme_tab)

        # wire logger to debug tab so logs appear in UI
        try:
            # _logic_debug is the actual logic object (DebugTab QWidget)
            logger.set_debug_tab(self._logic_debug)
            logger.info('Debug tab attached to logger')
        except Exception:
            pass

        # ADD TABS TO THE TAB WIDGET (use display widgets)
        self.tabs.addTab(self._disp_character, "Character")
        self.tabs.addTab(self._disp_items, "Items")
        self.tabs.addTab(self._disp_progression, "Progression")
        self.tabs.addTab(self._disp_stats, "Stats")
        self.tabs.addTab(self._disp_world, "World")
        self.tabs.addTab(self._disp_unlockables, "Unlockables")
        self.tabs.addTab(self._disp_profile, "Profile")
        self.tabs.addTab(self._disp_yaml, "YAML")
        self.tabs.addTab(self._disp_debug, "Debug")
        self.tabs.addTab(self._disp_readme, "Readme")

        # Initialize controller with proper tab mapping
        # Tab controller mapping points to logic objects (not necessarily QWidgets)
        self.tab_mapping = {
            'character': self._logic_character,
            'items': self._logic_items,
            'progression': self._logic_progression,
            'stats': self._logic_stats,
            'world': self._logic_world,
            'unlockables': self._logic_unlockables,
            'profile': self._logic_profile,
        }
        self.controller = TabController(self.tab_mapping)

        # crypt wrapper instance
        try:
            exe = os.path.join(os.getcwd(), 'bl4-crypt-cli.exe') if os.path.exists(os.path.join(os.getcwd(),'bl4-crypt-cli.exe')) else 'bl4-crypt-cli'
            self.crypt = crypt_mod.CryptWrapper(exe_path=exe, logger=logger)
        except Exception:
            self.crypt = crypt_mod.CryptWrapper()

        # connect YAML editor changes to a handler that will attempt to parse
        # and apply YAML to the tabs automatically (auto-sync)
        try:
            if hasattr(self.yaml_tab, 'text_changed'):
                self.yaml_tab.text_changed.connect(self._on_yaml_edited)
        except Exception:
            pass

        # Create toolbar and other UI elements
        self._create_toolbar()
        self._load_userid()
        # Apply UI stylesheet and theme from settings
        try:
            self.apply_stylesheet(core_settings.get_setting('custom_stylesheet', ''), core_settings.get_setting('ui_theme', 'System'))
        except Exception:
            pass

    def _create_toolbar(self):
        """Create the main toolbar"""
        # store toolbar as an attribute so we can repolish it after theme changes
        self.toolbar = self.addToolBar('Main')

        open_action = QtGui.QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(open_action)

        save_sav_action = QtGui.QAction('Save as .sav', self)
        save_sav_action.triggered.connect(self.save_as_sav)
        self.toolbar.addAction(save_sav_action)

        save_yaml_action = QtGui.QAction('Save as YAML', self)
        save_yaml_action.triggered.connect(self.save_as_yaml)
        self.toolbar.addAction(save_yaml_action)

        self.toolbar.addSeparator()
        refresh_action = QtGui.QAction('Refresh tabs', self)
        refresh_action.triggered.connect(self.refresh_tabs)
        self.toolbar.addAction(refresh_action)

        # Settings dialog
        settings_action = QtGui.QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings)
        self.toolbar.addAction(settings_action)

        # --- UserID input + save ---
        self.toolbar.addSeparator()
        uid_label = QtWidgets.QLabel('UserID:')
        self.toolbar.addWidget(uid_label)
        self.userid_input = QtWidgets.QLineEdit()
        self.userid_input.setFixedWidth(220)
        self.userid_input.setPlaceholderText('SteamID64 or 32-byte hex')
        # validate on change
        self.userid_input.textChanged.connect(self._on_userid_change)
        self.toolbar.addWidget(self.userid_input)
        self.userid_status = QtWidgets.QLabel('')
        self.toolbar.addWidget(self.userid_status)
        self.userid_save_btn = QtGui.QAction('Save UserID', self)
        self.userid_save_btn.triggered.connect(self.save_userid)
        self.toolbar.addAction(self.userid_save_btn)

    def _load_userid(self):
        # load last_userid from core settings if available
        try:
            uid = core_settings.get_setting('last_userid', '')
            if uid:
                self.current_userid = uid
                self.statusBar().showMessage(f"Loaded userid {uid}")
                # if toolbar exists, set the input and validate
                try:
                    self.userid_input.setText(uid)
                    ok = self._validate_userid(uid)
                    self.userid_status.setText('✅' if ok else '❌')
                except Exception:
                    pass
                return
        except Exception:
            pass
        self.current_userid = None

    def open_settings(self):
        try:
            dlg = SettingsDialog(self, apply_callback=self.apply_stylesheet)
            if dlg.exec() == QtWidgets.QDialog.Accepted:
                # settings are applied live by SettingsTab via core_settings
                logger.info('Settings updated by user')
        except Exception as e:
            logger.error(f'Failed to open settings dialog: {e}')

    def apply_stylesheet(self, css_text, theme_name='System'):
        """Apply a Qt stylesheet and switch theme heuristics.

        css_text: stylesheet string to apply (can be empty)
        theme_name: 'System'|'Light'|'Dark' - used to decide palette tweaks
        """
        try:
            app = QtWidgets.QApplication.instance()
            if not app:
                return
            # Basic theme adjustments: if Dark, set a dark palette
            if theme_name == 'Dark':
                pal = app.palette()
                pal.setColor(QtGui.QPalette.Window, QtGui.QColor('#2b2b2b'))
                pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor('#e6e6e6'))
                pal.setColor(QtGui.QPalette.Base, QtGui.QColor('#1e1e1e'))
                pal.setColor(QtGui.QPalette.Text, QtGui.QColor('#e6e6e6'))
                # Set button text color too from settings, if available
                try:
                    txt = core_settings.get_setting('ui_text_color', '#e6e6e6')
                    pal.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(txt))
                except Exception:
                    pass
                app.setPalette(pal)
            elif theme_name == 'Light':
                app.setPalette(app.style().standardPalette())
            else:
                # System: reset to default
                app.setPalette(app.style().standardPalette())

            # Determine stylesheet to apply (priority: external QSS file -> provided css_text -> stored custom_stylesheet -> built-in defaults)
            qss_path = core_settings.get_setting('qss_path', '')
            applied_css = ''
            try:
                if qss_path and os.path.exists(qss_path):
                    with open(qss_path, 'r', encoding='utf-8') as f:
                        applied_css = f.read()
                elif css_text:
                    applied_css = css_text
                else:
                    stored = core_settings.get_setting('custom_stylesheet', '')
                    if stored:
                        applied_css = stored
                    else:
                        # If theme is Dark and no custom css, use built-in default dark QSS
                        if theme_name == 'Dark':
                            applied_css = default_ui.get_default_stylesheet()
                        else:
                            applied_css = ''
            except Exception:
                applied_css = css_text or ''

            app.setStyleSheet(applied_css or '')
            # repolish toolbar and tabs so colors take effect (if present)
            try:
                if hasattr(self, 'toolbar') and self.toolbar:
                    self.toolbar.style().polish(self.toolbar)
                    self.toolbar.update()
                if hasattr(self, 'tabs') and self.tabs:
                    self.tabs.style().polish(self.tabs)
                    self.tabs.update()
            except Exception:
                pass
        except Exception as e:
            logger.error(f'Failed applying stylesheet: {e}')

    def _validate_userid(self, v):
        v = str(v).strip()
        if v.isdigit() and len(v) == 17:
            return True
        import re
        if re.fullmatch(r'[0-9a-fA-F]{32}', v):
            return True
        return False

    def _on_userid_change(self, text):
        try:
            ok = self._validate_userid(text)
            self.userid_status.setText('✅' if ok else '❌')
            # auto-save when a valid userid is entered and it's different
            if ok:
                v = text.strip()
                if v and v != (self.current_userid or ''):
                    # call save_userid which persists and updates current_userid
                    self.save_userid()
        except Exception:
            self.userid_status.setText('')

    def save_userid(self):
        v = self.userid_input.text().strip()
        try:
            if self._validate_userid(v):
                # persist to example userid.txt and to core settings
                import pathlib
                pathlib.Path('userid.txt').write_text(v)
                core_settings.set_setting('last_userid', v)
                self.current_userid = v
                self.userid_status.setText('✅')
                try:
                    logger.info('UserID saved',)
                except Exception:
                    pass
            else:
                self.userid_status.setText('❌')
                try:
                    logger.error('Invalid UserID attempted to save')
                except Exception:
                    pass
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'UserID', str(e))

    def open_file(self):
        dlg = QtWidgets.QFileDialog(self, 'Open Save or YAML', os.getcwd())
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dlg.setNameFilters(['YAML Files (*.yaml *.yml)', 'Save Files (*.sav)', 'All Files (*)'])
        if not dlg.exec():
            return
        path = dlg.selectedFiles()[0]
        try:
            # fileio.open_file handles .yaml and .sav (requires userid for .sav)
            if path.lower().endswith('.sav') and not self.current_userid:
                # ask for userid if missing
                uid, ok = QtWidgets.QInputDialog.getText(self, 'UserID required', 'Enter Steam/UserID:')
                if not ok or not uid:
                    self.statusBar().showMessage('Open cancelled: UserID required for .sav')
                    return
                self.current_userid = uid
                core_settings.set_setting('last_userid', uid)
            tmp_path, data = fileio.open_file(path, userid=self.current_userid)
            self.current_yaml_path = tmp_path
            self.current_original_path = path
            self.current_data = data
            self._apply_loaded_data(data)
            self.statusBar().showMessage(f'Loaded {os.path.basename(path)}')
            logger.info(f'Opened file: {path}')
        except Exception as e:
            logger.error(f'Error opening file {path}: {e}')
            QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to open file:\n{e}')

    def _apply_loaded_data(self, data):
        # Update YAML tab and other tabs via controller
        try:
            # Prefer to populate tabs first (tabs are authoritative by default)
            try:
                self.controller.load_into_tabs(data)
            except Exception as e:
                logger.warning(f'Controller load warning: {e}')
            # update YAML editor from data but avoid triggering the textChanged handler
            try:
                self._yaml_sync_in_progress = True
                if hasattr(self.yaml_tab, 'set_yaml'):
                    try:
                        # show the merged view
                        self.yaml_tab.set_yaml(data)
                    except Exception:
                        pass
            finally:
                self._yaml_sync_in_progress = False
        except Exception as e:
            logger.error(f'Error applying loaded data: {e}')

    def save_as_yaml(self):
        if not self.current_data:
            QtWidgets.QMessageBox.information(self, 'No data', 'No data loaded to save')
            return
        dlg = QtWidgets.QFileDialog(self, 'Save YAML', os.getcwd())
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dlg.setNameFilters(['YAML Files (*.yaml *.yml)', 'All Files (*)'])
        if not dlg.exec():
            return
        path = dlg.selectedFiles()[0]
        try:
            prefer_tabs = core_settings.get_setting('prefer_tabs_on_save', True)
            # If tabs take priority, collect tab edits into current_data first
            if prefer_tabs:
                try:
                    self.controller.save_from_tabs(self.current_data)
                except Exception:
                    pass
                data_to_write = self.current_data
            else:
                # YAML content takes priority
                try:
                    if hasattr(self.yaml_tab, 'get_yaml'):
                        data_to_write = self.yaml_tab.get_yaml()
                    else:
                        data_to_write = self.current_data
                except ValueError as e:
                    QtWidgets.QMessageBox.warning(self, 'YAML Error', str(e))
                    return

            # use safe writer that disables PyYAML aliases
            # use atomic write and create a timestamped backup if overwriting
            fileio.safe_write_yaml(path, data_to_write, atomic=True, make_backup=True)
            # update current data
            self.current_data = data_to_write
            # reflect merged result in YAML editor
            try:
                self._yaml_sync_in_progress = True
                if hasattr(self.yaml_tab, 'set_yaml'):
                    self.yaml_tab.set_yaml(self.current_data)
            finally:
                self._yaml_sync_in_progress = False

            self.statusBar().showMessage(f'Saved YAML to {path}')
            logger.info(f'Saved YAML: {path}')
            # if user saved back to the original file path, update original with backup
            try:
                if self.current_original_path and os.path.abspath(path) == os.path.abspath(self.current_original_path):
                    # replace the original with this saved file (we already backed it up above)
                    shutil.copy2(path, self.current_original_path)
                    logger.info(f'Committed YAML back to original: {self.current_original_path}')
            except Exception:
                pass
        except Exception as e:
            logger.error(f'Error saving YAML {path}: {e}')
            QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to save YAML:\n{e}')

    def save_as_sav(self):
        if not self.current_data:
            QtWidgets.QMessageBox.information(self, 'No data', 'No data loaded to save')
            return
        dlg = QtWidgets.QFileDialog(self, 'Save .sav', os.getcwd())
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dlg.setNameFilters(['Save Files (*.sav)', 'All Files (*)'])
        if not dlg.exec():
            return
        out_path = dlg.selectedFiles()[0]
        try:
            # determine save precedence
            prefer_tabs = core_settings.get_setting('prefer_tabs_on_save', True)
            if prefer_tabs:
                try:
                    self.controller.save_from_tabs(self.current_data)
                except Exception:
                    pass
                tmp_data = self.current_data
            else:
                if hasattr(self.yaml_tab, 'get_yaml'):
                    try:
                        tmp_data = self.yaml_tab.get_yaml()
                    except ValueError as e:
                        QtWidgets.QMessageBox.warning(self, 'YAML Error', str(e))
                        return
                else:
                    tmp_data = self.current_data

            # write temporary yaml
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
            tmp_path = tmp.name
            tmp.close()
            # use safe writer to avoid aliases (non-atomic temp write)
            fileio.safe_write_yaml(tmp_path, tmp_data, atomic=False, make_backup=False)
            # use crypt wrapper to encrypt
            # if the out file exists, back it up first
            if os.path.exists(out_path):
                try:
                    shutil.copy2(out_path, out_path + '.bak')
                except Exception:
                    pass
            ok = self.crypt.encrypt(tmp_path, out_path, userid=self.current_userid)
            os.unlink(tmp_path)
            if not ok:
                raise RuntimeError('Encryption failed (see logs)')
            self.statusBar().showMessage(f'Saved .sav to {out_path}')
            logger.info(f'Saved .sav: {out_path}')
            # if user originally opened a .sav, and saved to same path, commit by replacing original
            try:
                if self.current_original_path and os.path.abspath(out_path) == os.path.abspath(self.current_original_path):
                    shutil.copy2(out_path, self.current_original_path)
                    logger.info(f'Committed .sav back to original: {self.current_original_path}')
            except Exception:
                pass
        except Exception as e:
            logger.error(f'Error saving .sav {out_path}: {e}')
            QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to save .sav:\n{e}')

    def refresh_tabs(self):
        # simple refresh: reload YAML tab from current_data and call load_into_tabs
        if not self.current_data:
            return
        # reload the YAML editor from current_data then reapply to tabs
        self._apply_loaded_data(self.current_data)

    def commit_to_original(self):
        """Commit the currently edited temp file back to the original file path, making a .bak of the original first."""
        if not self.current_yaml_path or not self.current_original_path:
            QtWidgets.QMessageBox.information(self, 'No original', 'No original file to commit to (open a file first)')
            return
        # confirm with user
        resp = QtWidgets.QMessageBox.question(self, 'Commit', f'Commit changes to original file? This will overwrite:\n{self.current_original_path}\nA .bak will be created.')
        if resp != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            # create backup of original
            try:
                if os.path.exists(self.current_original_path):
                    bak = self.current_original_path + '.bak'
                    shutil.copy2(self.current_original_path, bak)
            except Exception as e:
                logger.warning(f'Failed to create .bak: {e}')

            # If original was a .sav, we need to encrypt current temp yaml to produce a .sav
            if self.current_original_path.lower().endswith('.sav'):
                # write temp yaml from current_data or yaml tab depending on preference
                prefer_tabs = core_settings.get_setting('prefer_tabs_on_save', True)
                if prefer_tabs:
                    try:
                        self.controller.save_from_tabs(self.current_data)
                    except Exception:
                        pass
                    tmp_data = self.current_data
                else:
                    try:
                        tmp_data = self.yaml_tab.get_yaml()
                    except Exception:
                        tmp_data = self.current_data
                # create temporary yaml file
                t = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
                tpath = t.name
                t.close()
                # use safe writer to avoid aliases (non-atomic temp write)
                fileio.safe_write_yaml(tpath, tmp_data, atomic=False, make_backup=False)
                ok = self.crypt.encrypt(tpath, self.current_original_path, userid=self.current_userid)
                os.unlink(tpath)
                if not ok:
                    raise RuntimeError('Encryption failed during commit')
            else:
                # For yaml originals, write current_data or yaml tab content to a temp file then copy over
                prefer_tabs = core_settings.get_setting('prefer_tabs_on_save', True)
                if prefer_tabs:
                    try:
                        self.controller.save_from_tabs(self.current_data)
                    except Exception:
                        pass
                    to_write = self.current_data
                else:
                    try:
                        to_write = self.yaml_tab.get_yaml()
                    except Exception:
                        to_write = self.current_data
                t = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
                tpath = t.name
                t.close()
                fileio.safe_write_yaml(tpath, to_write, atomic=False, make_backup=False)
                # copy temp over original
                shutil.copy2(tpath, self.current_original_path)
                os.unlink(tpath)

            self.statusBar().showMessage(f'Committed changes to {self.current_original_path}')
            logger.info(f'Committed changes to original: {self.current_original_path}')
        except Exception as e:
            logger.error(f'Error committing to original: {e}')
            QtWidgets.QMessageBox.critical(self, 'Commit Failed', str(e))

    def _on_yaml_edited(self):
        # user edited YAML text; attempt to parse and apply into tabs
        if getattr(self, '_yaml_sync_in_progress', False):
            return
        try:
            self._yaml_sync_in_progress = True
            if not hasattr(self.yaml_tab, 'get_yaml'):
                return
            try:
                parsed = self.yaml_tab.get_yaml()
            except ValueError:
                # invalid YAML — don't apply
                return
            # replace current_data and re-load into tabs
            self.current_data = parsed
            try:
                self.controller.load_into_tabs(parsed)
            except Exception as e:
                logger.warning(f'Failed to load YAML edits into tabs: {e}')
        finally:
            self._yaml_sync_in_progress = False