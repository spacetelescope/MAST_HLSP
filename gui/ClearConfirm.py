"""
..class:: ClearConfirm
    :synopsis: This is a subclass of the PyQt QDialog class designed as a
    popup dialog to confirm a user's action before execution, specifically in
    the case of resetting GUI forms.
"""

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

#--------------------

class ClearConfirm(QDialog):
    """ Pop up a confirmation dialog window before clearing all changes to the
    form.
    """

    def __init__(self, dialog):
        super().__init__()
        self.confirmUI(dialog)

    def confirmUI(self, dialog):
        self.confirm = False
        label = QLabel(dialog)
        label.setAlignment(Qt.AlignHCenter)
        yes = QPushButton("Yes")
        no = QPushButton("No")

        g = QGridLayout()
        g.addWidget(label, 0, 0, 1, -1)
        g.addWidget(yes, 1, 0)
        g.addWidget(no, 1, 1)
        self.setLayout(g)
        self.setWindowTitle("Confirm Clear")
        self.resize(300, 50)
        self.show()

        yes.clicked.connect(self.yesClicked)
        no.clicked.connect(self.noClicked)

    def yesClicked(self):
        self.confirm = True
        self.close()

    def noClicked(self):
        self.confirm = False
        self.close()
