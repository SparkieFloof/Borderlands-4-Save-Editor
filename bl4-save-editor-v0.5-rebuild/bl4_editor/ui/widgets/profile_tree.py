from typing import Any, List
from PySide6 import QtWidgets, QtCore
import traceback


def set_by_path(data: Any, path: List[Any], value: Any) -> bool:
    if data is None or not path:
        return False
    cur = data
    for p in path[:-1]:
        if isinstance(cur, dict):
            cur = cur.setdefault(p, {})
        elif isinstance(cur, list) and isinstance(p, int):
            while p >= len(cur):
                cur.append({})
            cur = cur[p]
        else:
            return False
    last = path[-1]
    if isinstance(cur, dict):
        cur[last] = value
        return True
    if isinstance(cur, list) and isinstance(last, int):
        while last >= len(cur):
            cur.append(None)
        cur[last] = value
        return True
    return False


class ProfileTree(QtWidgets.QTreeWidget):
    """
    QTreeWidget that stores a 'path' in Qt.UserRole for each item,
    allows editing of the value column, and writes changes back via
    callback to the data model using set_by_path.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["Key", "Value"])
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(True)
        self.itemChanged.connect(self._on_item_changed)
        self._editing_disabled = False
        self.data_model = None

    def build_from(self, root_name: str, data_model: Any):
        self.clear()
        self.data_model = data_model
        root = QtWidgets.QTreeWidgetItem([root_name, ""])
        root.setData(0, QtCore.Qt.UserRole, [])
        self.addTopLevelItem(root)
        self._add_children(root, data_model, [])
        self.expandAll()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

    def _add_children(self, parent_item: QtWidgets.QTreeWidgetItem, obj: Any, path: List[Any]):
        try:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    child = QtWidgets.QTreeWidgetItem([str(k), "" if isinstance(v, (dict, list)) else str(v)])
                    p = list(path) + [k]
                    child.setData(0, QtCore.Qt.UserRole, p)
                    if not isinstance(v, (dict, list)):
                        child.setFlags(child.flags() | QtCore.Qt.ItemIsEditable)
                    parent_item.addChild(child)
                    if isinstance(v, (dict, list)):
                        self._add_children(child, v, p)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    child = QtWidgets.QTreeWidgetItem([f"[{i}]", "" if isinstance(v, (dict, list)) else str(v)])
                    p = list(path) + [i]
                    child.setData(0, QtCore.Qt.UserRole, p)
                    if not isinstance(v, (dict, list)):
                        child.setFlags(child.flags() | QtCore.Qt.ItemIsEditable)
                    parent_item.addChild(child)
                    if isinstance(v, (dict, list)):
                        self._add_children(child, v, p)
            else:
                try:
                    parent_item.setText(1, "" if obj is None else str(obj))
                except Exception:
                    pass
        except Exception:
            # keep UI responsive if model is unexpected
            try:
                parent_item.addChild(QtWidgets.QTreeWidgetItem(["<error>", "<error> "]))
            except Exception:
                pass

    def _on_item_changed(self, item: QtWidgets.QTreeWidgetItem, column: int):
        if self._editing_disabled:
            return
        if column != 1:
            return
        path = item.data(0, QtCore.Qt.UserRole)
        if path is None or self.data_model is None:
            return
        new_text = item.text(1)
        value = new_text
        if new_text.lower() in ("true", "false"):
            value = new_text.lower() == "true"
        else:
            try:
                if "." in new_text:
                    value = float(new_text)
                else:
                    value = int(new_text)
            except Exception:
                value = new_text
        try:
            set_by_path(self.data_model, path, value)
        except Exception:
            # swallow errors
            pass
