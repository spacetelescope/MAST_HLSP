import os
import sys
base = sys.path[0]
subdirectories = [x for x in os.listdir(base) if (os.path.isdir(x)
                                                  and x[0] is not ".")
                  ]
subpackages = [os.path.join(base, subdir) for subdir in subdirectories]
sys.path = subpackages + sys.path

from bin.read_yaml import read_yaml
from CHECK_METADATA_FORMAT import select_data_templates_gui
from gui.GUIbuttons import BlueButton, GreenButton, GreyButton, RedButton
from gui.CheckFilenamesGUI import CheckFilenamesGUI
from gui.CheckMetadataGUI import CheckMetadataGUI
from gui.ClearConfirm import ClearConfirm
from gui.MyError import MyError
from lib.HLSPFile import HLSPFile

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

# --------------------


def read_hlsp_file(path):
    hlsp_file = read_yaml(path)

# --------------------


class HLSPGUI(QTabWidget):
    """ Create a tab widget to contain widgets from /gui/ext_generator.py and
    /gui/config_generator.py.  Provide options to quit or open a help dialog.
    """

    def __init__(self):
        super().__init__()
        self.hlsp = HLSPFile()

        load_hlsp = GreyButton("Load an .hlsp File", 60, min_width=150)

        path_label = QLabel("HLSP Data Path: ")
        self.hlsp_path_edit = QLineEdit()
        self.hlsp_path_edit.insert(os.getcwd())

        name_label = QLabel("HLSP Name: ")
        self.hlsp_name_edit = QLineEdit()

        # Set up the tabs contained in this widget
        self.tabs = QTabWidget()
        self.step1 = CheckFilenamesGUI(parent=self)
        self.step2 = CheckMetadataGUI()
        self.tabs.addTab(self.step1, "1: Check Filenames")
        self.tabs.addTab(self.step2, "2: Check Metadata")
        self.tbar = self.tabs.tabBar()
        #self.tbar.setTabTextColor(0, Qt.red)

        self.hlsp_path_edit.textEdited.connect(self.update_hlsp_path)

        self.meta_grid = QGridLayout()
        self.meta_grid.addWidget(load_hlsp, 0, 0, 2, 1)
        self.meta_grid.addWidget(path_label, 0, 1)
        self.meta_grid.addWidget(self.hlsp_path_edit, 0, 2)
        self.meta_grid.addWidget(name_label, 1, 1)
        self.meta_grid.addWidget(self.hlsp_name_edit, 1, 2)
        self.meta_grid.addWidget(self.tabs, 2, 0, 1, -1)

        self.setLayout(self.meta_grid)
        self.resize(1100, 500)

        # Center the window
        qtRectangle = self.frameGeometry()
        screen = QDesktopWidget().availableGeometry()
        x = (screen.width() - qtRectangle.width()) / 2
        y = (screen.height() - qtRectangle.height()) / 2
        self.move(x, y)

        # Name and display the window
        self.setWindowTitle("HLSP Ingestion GUI")
        self.show()

    def closeEvent(self, event):
        """Reset the stdout variable and print a close statement to confirm."""

        save_prompt = ClearConfirm("Save to .hlsp file?")
        save_prompt.exec_()
        if save_prompt.confirm:
            event.accept()
        else:
            event.ignore()

    def update_hlsp_path(self):

        current_path = self.hlsp_path_edit.text()
        self.hlsp.update_filepaths(input=current_path)
        self.hlsp.updated = True

# --------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = HLSPGUI()
    sys.exit(app.exec_())
