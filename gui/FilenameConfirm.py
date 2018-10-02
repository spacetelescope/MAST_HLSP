"""
..class:: ClearConfirm
    :synopsis: This is a subclass of the PyQt QDialog class designed as a
    popup dialog to confirm a user's action before execution, specifically in
    the case of resetting GUI forms.
"""

import GUIbuttons as gb

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

# --------------------


class FilenameConfirm(QDialog):
    """ Pop up a confirmation dialog window before clearing all changes to the
    form.
    """

    def __init__(self, hlsp_name):

        super().__init__()

        self.file = ".".join([hlsp_name, "hlsp"])
        prompt = QLabel("Select a file name to use:")
        self.default_button = QRadioButton("Default Name: ")
        self.default_button.setChecked(True)
        default_label = QLabel(self.file)
        self.custom_button = QRadioButton("Custom Name: ")
        self.custom_edit = QLineEdit()

        save_button = gb.GreenButton("Save", 30)
        save_button.clicked.connect(self.save_clicked)
        cancel_button = gb.GreyButton("Cancel", 30)
        cancel_button.clicked.connect(self.cancel_clicked)

        g = QGridLayout()
        g.addWidget(prompt, 0, 0, 1, -1)
        g.addWidget(self.default_button, 1, 0)
        g.addWidget(default_label, 1, 1)
        g.addWidget(self.custom_button, 2, 0)
        g.addWidget(self.custom_edit, 2, 1)
        g.addWidget(save_button, 3, 0)
        g.addWidget(cancel_button, 3, 1)
        self.setLayout(g)
        self.setWindowTitle("Save As")
        self.resize(300, 50)
        self.show()

    def cancel_clicked(self):
        self.file = None
        self.close()

    def save_clicked(self):

        if self.default_button.isChecked():
            self.close()
        else:
            self.file = self.custom_edit.text()
            self.close()
