from typing import Any
from PySide6 import QtWidgets, QtCore
from ..widgets.profile_tree import ProfileTree
import ast


class ProfileTab(QtWidgets.QWidget):
    """Profile tab UI: left side is a ProfileTree, right side shows grouped details.

    - load_data(data): load the profile dict
    - save_data(): return the possibly-updated profile dict
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        self._setup_ui()

    def _setup_ui(self):
        lay = QtWidgets.QHBoxLayout(self)

        # Left: tree
        self.tree = ProfileTree()
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        lay.addWidget(self.tree, 1)
        # Right: simple details pane (placeholder + editors)
        self.right = QtWidgets.QStackedWidget()
        self.right_placeholder = QtWidgets.QLabel('Select a node to edit its value')
        self.right_placeholder.setWordWrap(True)
        p = QtWidgets.QWidget()
        p_l = QtWidgets.QVBoxLayout(p)
        p_l.addWidget(self.right_placeholder)
        p_l.addStretch()
        self.right.addWidget(p)
        lay.addWidget(self.right, 2)

    def load_data(self, data: Any):
        """Populate the ProfileTree from data and build grouping pages."""
        # Accept multiple payload shapes: data may be the profile dict, or may be a larger save
        if data is None:
            data = {}

        # Try to find the profile dict in common locations
        profile_candidate = None
        if isinstance(data, dict) and any(k in data for k in ('inputprefs', 'ui', 'onlineprefs', 'shared')):
            profile_candidate = data
        # domains.local.shared
        if profile_candidate is None and isinstance(data, dict) and 'domains' in data:
            try:
                local = data['domains'].get('local', {})
                if isinstance(local, dict) and 'shared' in local:
                    profile_candidate = local['shared']
            except Exception:
                pass
        # state.profile
        if profile_candidate is None and isinstance(data, dict) and 'state' in data:
            st = data.get('state', {})
            if isinstance(st, dict) and 'profile' in st:
                profile_candidate = st.get('profile')

        # fallback to top-level 'shared' if that's the actual profile container
        if profile_candidate is None and isinstance(data, dict) and 'shared' in data:
            profile_candidate = data.get('shared')

        if profile_candidate is None:
            profile_candidate = data

        self.data = profile_candidate

        # Build tree rooted at 'Profile', but exclude the domains.local.shared.inventory.items.bank subtree
        try:
            tree_data = self._profile_tree_copy(self.data)
            self.tree.build_from('Profile', tree_data)
        except Exception:
            # fallback: just clear
            self.tree.clear()

        # Build group pages for each top-level key for quick navigation
        # Rebuild the right-side pages and pref subtabs
        self.right.clear()
        # ensure placeholder is present
        placeholder_page = QtWidgets.QWidget()
        ph_l = QtWidgets.QVBoxLayout(placeholder_page)
        ph_l.addWidget(self.right_placeholder)
        ph_l.addStretch()
        self.right.addWidget(placeholder_page)

        # (prefs UI removed; profile shows a compact navigation + editable details on selection)

        # Build quick navigation pages for top-level groups (excluding bank which is handled by ItemsTab)
        if isinstance(self.data, dict):
            for k in self.data.keys():
                page = QtWidgets.QWidget()
                vlay = QtWidgets.QVBoxLayout(page)
                label = QtWidgets.QLabel(f'Group: {k}')
                label.setStyleSheet('font-weight: bold;')
                vlay.addWidget(label)
                # quick list of subkeys
                if isinstance(self.data[k], dict):
                    for subk in self.data[k].keys():
                        btn = QtWidgets.QPushButton(str(subk))
                        # clicking will select that path in the tree
                        def make_handler(top=k, sub=subk):
                            def h():
                                # find the item by path and select it
                                self._select_path([top, sub])

                            return h

                        btn.clicked.connect(make_handler())
                        vlay.addWidget(btn)
                vlay.addStretch()
                self.right.addWidget(page)

    def save_data(self):
        return self.data

    def _profile_tree_copy(self, src):
        """Return a copy of src suitable for the ProfileTree: strip out domains.local.shared.inventory.items.bank to avoid duplicate bank display."""
        try:
            import copy
            s = copy.deepcopy(src)
            # remove domains.local.shared.inventory.items.bank
            try:
                if isinstance(s, dict) and 'domains' in s:
                    local = s['domains'].get('local', {})
                    if isinstance(local, dict) and 'shared' in local:
                        shared = local['shared']
                        if isinstance(shared, dict):
                            inv = shared.get('inventory', {})
                            if isinstance(inv, dict):
                                items = inv.get('items', {})
                                if isinstance(items, dict) and 'bank' in items:
                                    del items['bank']
            except Exception:
                pass

            # also remove top-level shared.inventory.items.bank if present
            try:
                if isinstance(s, dict) and 'shared' in s and isinstance(s['shared'], dict):
                    inv = s['shared'].get('inventory', {})
                    if isinstance(inv, dict):
                        items = inv.get('items', {})
                        if isinstance(items, dict) and 'bank' in items:
                            del items['bank']
            except Exception:
                pass

            return s
        except Exception:
            return src

    def _write_pref_value(self, section, key, value):
        try:
            if not isinstance(self.data, dict):
                self.data = {}
            if section not in self.data or not isinstance(self.data[section], dict):
                self.data[section] = {}
            self.data[section][key] = value
            # refresh tree view to reflect change
            try:
                self.tree.build_from('Profile', self.data)
            except Exception:
                pass
        except Exception:
            pass

    def _apply_line_edit(self, section, key, widget):
        try:
            text = widget.text()
            # try to parse basic literals
            try:
                val = ast.literal_eval(text)
            except Exception:
                val = text
            self._write_pref_value(section, key, val)
        except Exception:
            pass

    def _on_selection_changed(self):
        sel = self.tree.selectedItems()
        if not sel:
            self.right.setCurrentIndex(0)
            return
        item = sel[0]
        path = item.data(0, QtCore.Qt.UserRole)
        if not path:
            self.right.setCurrentIndex(0)
            return
        # show a small editor panel for the selected item
        editor = QtWidgets.QWidget()
        el = QtWidgets.QFormLayout(editor)
        key_label = QtWidgets.QLabel(str(path[-1]))
        value_edit = QtWidgets.QLineEdit(str(item.text(1)))

        def commit():
            # update the tree item text to trigger the ProfileTree set_by_path
            item.setText(1, value_edit.text())

        save_btn = QtWidgets.QPushButton('Save')
        save_btn.clicked.connect(commit)
        el.addRow('Key', key_label)
        el.addRow('Value', value_edit)
        el.addRow(save_btn)
        # replace temporary editor widget in the stack
        # keep index 0 as placeholder
        if self.right.count() > 1:
            # insert editor at position 1 and show it
            # remove any previous editor at index 1 first
            try:
                prev = self.right.widget(1)
                self.right.removeWidget(prev)
                prev.deleteLater()
            except Exception:
                pass
            self.right.insertWidget(1, editor)
            self.right.setCurrentIndex(1)
        else:
            self.right.addWidget(editor)
            self.right.setCurrentIndex(self.right.count() - 1)

    def _select_path(self, path_list):
        # traverse tree to find item by matching UserRole path
        def walk(parent):
            for i in range(parent.childCount()):
                ch = parent.child(i)
                p = ch.data(0, QtCore.Qt.UserRole)
                if p == path_list:
                    self.tree.setCurrentItem(ch)
                    return True
                if ch.childCount() and walk(ch):
                    return True
            return False

        for i in range(self.tree.topLevelItemCount()):
            root = self.tree.topLevelItem(i)
            if walk(root):
                return
