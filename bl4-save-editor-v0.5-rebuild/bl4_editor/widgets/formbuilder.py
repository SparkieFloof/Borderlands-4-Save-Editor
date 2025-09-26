from PySide6 import QtWidgets

class FormBuilder:
    def __init__(self):
        pass

    def build_form(self, form_layout: QtWidgets.QFormLayout, data_dict: dict):
        # create simple widgets for scalar values
        for k, v in data_dict.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                w = QtWidgets.QLineEdit(str(v) if v is not None else '')
                form_layout.addRow(k, w)
