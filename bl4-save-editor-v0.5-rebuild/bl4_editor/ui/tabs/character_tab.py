# Updated bl4_editor/ui/tabs/character_tab.py
from PySide6 import QtWidgets, QtCore
from typing import Any, Dict

class CharacterTab(QtWidgets.QWidget):
    """Character editing tab with form-based UI similar to your alpha build"""
    
    def __init__(self):
        super().__init__()
        self.data = {}
        self.form_widgets = {}  # Track form widgets for data binding
        self.setup_ui()
    
    def setup_ui(self):
        """Setup character tab UI with form layout"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Scrollable form area
        scroll = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        self.form_layout = QtWidgets.QFormLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Initially show placeholder
        self.form_layout.addRow(QtWidgets.QLabel("No character data loaded"))
    
    def load_data(self, data: Dict[str, Any]):
        """Load character data and build dynamic form"""
        self.data = data if data else {}
        self.rebuild_form()
    
    def rebuild_form(self):
        """Rebuild form based on current data"""
        # Clear existing form
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)
        self.form_widgets.clear()
        
        if not self.data:
            self.form_layout.addRow(QtWidgets.QLabel("No character data available"))
            return
        
        # Build form from data structure (similar to your alpha)
        state = self.data.get('state', {})
        if not state:
            self.form_layout.addRow(QtWidgets.QLabel("No character state present"))
            return
        
        # Basic character info
        for key, value in state.items():
            if isinstance(value, (dict, list)):
                continue  # Skip complex structures for now
            
            widget = self._create_widget_for_value(key, value)
            if widget:
                label = QtWidgets.QLabel(str(key).replace('_', ' ').title() + ':')
                self.form_layout.addRow(label, widget)
                self.form_widgets[key] = widget
        
        # Special handling for currencies
        currencies = state.get('currencies', {})
        if isinstance(currencies, dict) and currencies:
            self.form_layout.addRow(QtWidgets.QLabel(''), QtWidgets.QLabel('<b>Currencies</b>'))
            for key, value in currencies.items():
                widget = self._create_widget_for_value(f'currencies.{key}', value)
                if widget:
                    label = QtWidgets.QLabel(str(key).replace('_', ' ').title() + ':')
                    self.form_layout.addRow(label, widget)
                    self.form_widgets[f'currencies.{key}'] = widget
        
        # Experience handling
        experience = state.get('experience', [])
        if isinstance(experience, list) and experience:
            self.form_layout.addRow(QtWidgets.QLabel(''), QtWidgets.QLabel('<b>Experience</b>'))
            for idx, exp_entry in enumerate(experience):
                if isinstance(exp_entry, dict):
                    exp_type = exp_entry.get('type', f'Experience {idx}')
                    container = QtWidgets.QWidget()
                    h_layout = QtWidgets.QHBoxLayout(container)
                    
                    # Level widget
                    level_widget = QtWidgets.QSpinBox()
                    level_widget.setRange(0, 9999)
                    level_widget.setValue(int(exp_entry.get('level', 0)))
                    level_widget.valueChanged.connect(
                        lambda val, i=idx: self._update_experience_value(i, 'level', val)
                    )
                    h_layout.addWidget(QtWidgets.QLabel('Level:'))
                    h_layout.addWidget(level_widget)
                    
                    # Points widget
                    if 'points' in exp_entry or 'xp' in exp_entry:
                        points_widget = QtWidgets.QSpinBox()
                        points_widget.setRange(0, 2_000_000_000)
                        points_widget.setValue(int(exp_entry.get('points', exp_entry.get('xp', 0))))
                        points_widget.valueChanged.connect(
                            lambda val, i=idx: self._update_experience_value(i, 'points', val)
                        )
                        h_layout.addWidget(QtWidgets.QLabel('Points:'))
                        h_layout.addWidget(points_widget)
                    
                    h_layout.addStretch()
                    self.form_layout.addRow(QtWidgets.QLabel(exp_type + ':'), container)
    
    def _create_widget_for_value(self, key: str, value: Any) -> QtWidgets.QWidget:
        """Create appropriate widget for a value type"""
        if isinstance(value, bool):
            widget = QtWidgets.QCheckBox()
            widget.setChecked(value)
            widget.stateChanged.connect(
                lambda state, k=key: self._update_data_value(k, state == QtCore.Qt.Checked)
            )
            return widget
        elif isinstance(value, int):
            widget = QtWidgets.QSpinBox()
            widget.setRange(-2_000_000_000, 2_000_000_000)
            widget.setValue(value)
            widget.valueChanged.connect(
                lambda val, k=key: self._update_data_value(k, val)
            )
            return widget
        elif isinstance(value, float):
            widget = QtWidgets.QDoubleSpinBox()
            widget.setRange(-1e9, 1e9)
            widget.setDecimals(6)
            widget.setValue(value)
            widget.valueChanged.connect(
                lambda val, k=key: self._update_data_value(k, val)
            )
            return widget
        else:
            widget = QtWidgets.QLineEdit(str(value))
            widget.editingFinished.connect(
                lambda k=key, w=widget: self._update_data_value(k, w.text())
            )
            return widget
    
    def _update_data_value(self, key: str, value: Any):
        """Update data value when widget changes"""
        if '.' in key:
            # Handle nested keys like 'currencies.money'
            parts = key.split('.')
            current = self.data.get('state', {})
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = value
        else:
            # Direct key in state
            if 'state' not in self.data:
                self.data['state'] = {}
            self.data['state'][key] = value
    
    def _update_experience_value(self, index: int, field: str, value: Any):
        """Update experience array values"""
        if 'state' not in self.data:
            self.data['state'] = {}
        if 'experience' not in self.data['state']:
            self.data['state']['experience'] = []
        
        exp_list = self.data['state']['experience']
        while len(exp_list) <= index:
            exp_list.append({})
        
        exp_list[index][field] = value
    
    def save_data(self) -> Dict[str, Any]:
        """Return current character data"""
        return self.data