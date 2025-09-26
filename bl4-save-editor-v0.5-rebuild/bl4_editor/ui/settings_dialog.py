from PySide6 import QtWidgets
from bl4_editor.core import settings

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        layout = QtWidgets.QFormLayout(self)

        self.backup_chk = QtWidgets.QCheckBox()
        self.backup_chk.setChecked(settings.get_setting('backup_on_save', True))
        layout.addRow('Backup on save', self.backup_chk)

        self.retention_spin = QtWidgets.QSpinBox()
        self.retention_spin.setRange(1, 1440)
        self.retention_spin.setValue(settings.get_setting('log_retention_minutes', 10))
        layout.addRow('Log retention (minutes)', self.retention_spin)

        self.yaml_chk = QtWidgets.QCheckBox()
        self.yaml_chk.setChecked(settings.get_setting('yaml_as_source', False))
        layout.addRow('YAML as Source (Advanced)', self.yaml_chk)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def save(self):
        settings.set_setting('backup_on_save', bool(self.backup_chk.isChecked()))
        settings.set_setting('log_retention_minutes', int(self.retention_spin.value()))
        settings.set_setting('yaml_as_source', bool(self.yaml_chk.isChecked()))
        self.accept()
