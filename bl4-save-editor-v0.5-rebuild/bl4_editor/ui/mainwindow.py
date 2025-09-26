from PySide6 import QtWidgets, QtGui
import os, re
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

# Import your controller and fileio modules
# from bl4_editor.core.controller import Controller  # Uncomment when available
# from bl4_editor.core import fileio  # Uncomment when available

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BL4 Save Editor')
        self.resize(1200, 800)
        
        # Initialize data attributes
        self.current_yaml_path = None
        self.current_data = None

        # Create tab widget
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tab instances
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

        # ADD TABS TO THE TAB WIDGET - This was missing!
        self.tabs.addTab(self.character_tab, "Character")
        self.tabs.addTab(self.items_tab, "Items")
        self.tabs.addTab(self.progression_tab, "Progression")
        self.tabs.addTab(self.stats_tab, "Stats")
        self.tabs.addTab(self.world_tab, "World")
        self.tabs.addTab(self.unlockables_tab, "Unlockables")
        self.tabs.addTab(self.profile_tab, "Profile")
        self.tabs.addTab(self.yaml_tab, "YAML")
        self.tabs.addTab(self.debug_tab, "Debug")
        self.tabs.addTab(self.readme_tab, "Readme")

        # Initialize controller - uncomment when you have the controller module
        # self.controller = Controller()

        # Create toolbar
        self._create_toolbar()

        # Load userid.txt if present
        self._load_userid()

    def _create_toolbar(self):
        """Create the main toolbar with better organization"""
        tb = self.addToolBar('Main')
        
        # File operations
        open_action = QtGui.QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        tb.addAction(open_action)
        
        save_sav_action = QtGui.QAction('Save as .sav', self)
        save_sav_action.triggered.connect(self.save_as_sav)
        tb.addAction(save_sav_action)
        
        save_yaml_action = QtGui.QAction('Save as .yaml', self)
        save_yaml_action.triggered.connect(self.save_as_yaml)
        tb.addAction(save_yaml_action)

        # User ID section
        tb.addSeparator()
        tb.addWidget(QtWidgets.QLabel('User ID:'))
        
        self.user_edit = QtWidgets.QLineEdit()
        self.user_edit.setMaximumWidth(240)
        self.user_edit.textChanged.connect(self._on_userid_changed)  # Added validation on change
        tb.addWidget(self.user_edit)
        
        self.user_status = QtWidgets.QLabel('⚪')
        tb.addWidget(self.user_status)

    def _on_userid_changed(self, text):
        """Update user status when UserID text changes"""
        self._update_user_status(text.strip())

    def _load_userid(self):
        """Load UserID from userid.txt file if it exists"""
        userid_path = os.path.join(os.getcwd(), 'userid.txt')
        if os.path.exists(userid_path):
            try:
                with open(userid_path, 'r', encoding='utf-8') as f:
                    txt = f.read().strip()
                self.user_edit.setText(txt)
                self._update_user_status(txt)
                self.debug_tab.log('UserID loaded from userid.txt', level='info')
            except Exception as e:
                self.debug_tab.log(f'Failed to read userid.txt: {e}', level='error')
                self.user_status.setText('🟡')
        else:
            self.user_status.setText('🟡')

    def _update_user_status(self, txt):
        """Update the user status indicator based on UserID validity"""
        if not txt:
            self.user_status.setText('⚪')
            return False
        
        # Check for valid UserID formats (17 digits or 32 hex chars)
        if re.fullmatch(r"[0-9]{17}", txt) or re.fullmatch(r"[0-9a-fA-F]{32}", txt):
            self.user_status.setText('✅')
            return True
        
        self.user_status.setText('❌')
        return False

    def open_file(self):
        """Open a save file or YAML file"""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open Save or YAML', '', 'Saves (*.sav *.yaml *.yml)'
        )
        if not path:
            return

        userid = self.user_edit.text().strip()
        
        # Check if UserID is required for .sav files
        if path.lower().endswith('.sav') and not self._update_user_status(userid):
            QtWidgets.QMessageBox.warning(
                self, 'UserID required', 
                'A valid UserID is required to open .sav files'
            )
            self.debug_tab.log('Attempted to open .sav without UserID', level='error')
            return

        try:
            # TODO: Uncomment when fileio module is available
            # yaml_path, data = fileio.open_file(
            #     path, userid=userid if path.lower().endswith('.sav') else None
            # )
            
            # Temporary placeholder - replace with actual file loading
            yaml_path = path
            data = {}  # This should be your parsed save data
            
            self.current_yaml_path = yaml_path
            self.current_data = data
            
            # Populate tabs via controller
            # TODO: Uncomment when controller is available
            # self.controller.load_into_tabs(data)
            
            # Update YAML editor
            self.yaml_tab.set_yaml(data)
            
            # Adjust tab visibility based on data
            self._adjust_tabs(data)
            
            self.debug_tab.log(f'Opened: {path}', level='info')
            
        except Exception as e:
            self.debug_tab.log(f'Open failed: {e}', level='error')
            QtWidgets.QMessageBox.critical(
                self, 'Open failed', f'Failed to open file:\n{e}'
            )

    def save_as_sav(self):
        """Save the current data as a .sav file"""
        if not hasattr(self, 'current_data') or self.current_data is None:
            QtWidgets.QMessageBox.warning(self, 'No data', 'No file loaded to save.')
            return
            
        userid = self.user_edit.text().strip()
        if not self._update_user_status(userid):
            QtWidgets.QMessageBox.warning(
                self, 'UserID required', 'Valid UserID required to save .sav'
            )
            return

        try:
            # Get save path
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save as .sav', '', 'Save files (*.sav)'
            )
            if not path:
                return

            # Collect data from tabs
            data = self.current_data.copy()  # Make a copy to avoid modifying original
            # TODO: Uncomment when controller is available
            # self.controller.save_from_tabs(data)
            
            # TODO: Uncomment when fileio module is available
            # fileio.save_sav_file(path, data, userid=userid, make_backup=True)
            
            self.debug_tab.log(f'Saved .sav to: {path}', level='info')
            QtWidgets.QMessageBox.information(self, 'Success', f'File saved successfully to:\n{path}')
            
        except Exception as e:
            self.debug_tab.log(f'Save .sav failed: {e}', level='error')
            QtWidgets.QMessageBox.critical(self, 'Save failed', f'Failed to save .sav:\n{e}')

    def save_as_yaml(self):
        """Save the current data as a YAML file"""
        if not hasattr(self, 'current_data') or self.current_data is None:
            QtWidgets.QMessageBox.warning(self, 'No data', 'No file loaded to save.')
            return

        try:
            # Get save path
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save as YAML', '', 'YAML files (*.yaml *.yml)'
            )
            if not path:
                return

            # Collect data from tabs
            data = self.current_data.copy()
            # TODO: Uncomment when controller is available
            # self.controller.save_from_tabs(data)
            
            # TODO: Uncomment when fileio module is available
            # fileio.save_yaml_file(path, data, make_backup=True)
            
            self.debug_tab.log(f'Saved YAML to: {path}', level='info')
            QtWidgets.QMessageBox.information(self, 'Success', f'File saved successfully to:\n{path}')
            
        except Exception as e:
            self.debug_tab.log(f'Save YAML failed: {e}', level='error')
            QtWidgets.QMessageBox.critical(self, 'Save failed', f'Failed to save YAML:\n{e}')

    def _adjust_tabs(self, data):
        """Show/hide tabs based on available data"""
        if not isinstance(data, dict):
            return
            
        # Mapping of tab names to data keys
        tab_mapping = {
            'Character': 'character',
            'Items': ['backpack', 'equipped', 'bank'],  # Items tab visible if any of these present
            'Progression': 'progression',
            'Stats': 'stats',
            'World': 'world',
            'Unlockables': 'unlockables',
            'Profile': 'profile',
        }
        
        for i in range(self.tabs.count()):
            tab_name = self.tabs.tabText(i)
            
            # Always show these tabs
            if tab_name in ('YAML', 'Debug', 'Readme'):
                self.tabs.setTabVisible(i, True)
                continue
                
            # Check if tab should be visible based on data
            keys = tab_mapping.get(tab_name)
            if keys is None:
                continue
                
            visible = False
            if isinstance(keys, list):
                # Multiple possible keys (like Items tab)
                visible = any(k in data and data.get(k) not in (None, {}, []) for k in keys)
            else:
                # Single key
                visible = keys in data and data.get(keys) not in (None, {}, [])
            
            # Set tab visibility
            try:
                self.tabs.setTabVisible(i, visible)
            except AttributeError:
                # Fallback for older Qt versions
                widget = self.tabs.widget(i)
                if widget:
                    widget.setVisible(visible)