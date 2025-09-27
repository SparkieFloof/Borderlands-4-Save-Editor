from PySide6 import QtWidgets
from bl4_editor.core import settings as core_settings

class SettingsTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)

        # Explicit save checkbox
        self.explicit_save_chk = QtWidgets.QCheckBox("Require explicit save")
        self.explicit_save_chk.setChecked(core_settings.get_setting("require_explicit_save", True))
        self.explicit_save_chk.stateChanged.connect(self.toggle_explicit_save)
        layout.addWidget(self.explicit_save_chk)

        # Backups checkbox
        self.backup_chk = QtWidgets.QCheckBox("Create backups when saving")
        self.backup_chk.setChecked(core_settings.get_setting("make_backups", True))
        self.backup_chk.stateChanged.connect(self.toggle_backups)
        layout.addWidget(self.backup_chk)

        # Save precedence: tabs vs raw YAML
        self.save_precedence_chk = QtWidgets.QCheckBox("Prefer tabs over raw YAML when saving")
        # default: prefer tabs
        self.save_precedence_chk.setChecked(core_settings.get_setting("prefer_tabs_on_save", True))
        self.save_precedence_chk.stateChanged.connect(self.toggle_save_precedence)
        layout.addWidget(self.save_precedence_chk)

        # Log retention spinbox
        retention_layout = QtWidgets.QHBoxLayout()
        retention_label = QtWidgets.QLabel("Log retention (minutes):")
        self.retention_spin = QtWidgets.QSpinBox()
        self.retention_spin.setRange(1, 1440)
        self.retention_spin.setValue(core_settings.get_setting("log_retention", 10))
        self.retention_spin.valueChanged.connect(self.change_retention)
        retention_layout.addWidget(retention_label)
        retention_layout.addWidget(self.retention_spin)
        layout.addLayout(retention_layout)

        layout.addStretch()

    def toggle_explicit_save(self, state):
        core_settings.set_setting("require_explicit_save", bool(state))

    def toggle_backups(self, state):
        core_settings.set_setting("make_backups", bool(state))

    def toggle_save_precedence(self, state):
        core_settings.set_setting("prefer_tabs_on_save", bool(state))

    def change_retention(self, val):
        core_settings.set_setting("log_retention", int(val))
