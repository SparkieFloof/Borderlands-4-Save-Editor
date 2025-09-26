from PySide6 import QtWidgets
from typing import Any, Dict
from .profile_subtab import ProfileSubTab

class ProfileTabV2(QtWidgets.QWidget):
    """
    Profile tab as a container of sub-tabs for profile save sections:
    Preferences, UI Settings, Domains, Progression, Meta
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QtWidgets.QVBoxLayout(self)
        self.subtabs = QtWidgets.QTabWidget()
        v.addWidget(self.subtabs)

        # Define sub-tabs mapping: title -> top-level yaml key
        mapping = [
            ("Preferences", "inputprefs"),
            ("UI Settings", "ui"),
            ("Domains", "domains"),
            ("Progression", "pips"),
            ("Meta", "save_game_header"),
        ]
        self.tabs = {}
        for title, key in mapping:
            tab = ProfileSubTab(title, key)
            self.subtabs.
        # Explicit instantiation of subtabs (Alpha style)
        self.subtab_bank = BankTab(self)
        self.subtab_general = GeneralTab(self)
        self.subtab_stats = StatsTab(self)
        self.subtab_unlocks = UnlockablesTab(self)

        default_subtabs = [
            ("Bank", self.subtab_bank),
            ("General", self.subtab_general),
            ("Stats", self.subtab_stats),
            ("Unlockables", self.subtab_unlocks),
        ]

        import os, json
        subtab_order_file = os.path.expanduser("~/.bl4_editor/subtab_order.json")
        if os.path.exists(subtab_order_file):
            try:
                with open(subtab_order_file, "r", encoding="utf-8") as f:
                    custom_subtabs = json.load(f)
            except Exception:
                custom_subtabs = [name for name, _ in default_subtabs]
        else:
            custom_subtabs = [name for name, _ in default_subtabs]

        for name in custom_subtabs:
            for tab_name, widget in default_subtabs:
                if tab_name == name:
                    self.subtabs.addTab(widget, tab_name)
