"""
The classes defined here will create a GUI to handle two custom PyQt widgets
inside a QTabWidget.  This GUI will contain any meta-level user functions
(launch a help window, quit the program), and a tabs frame to allow the user to switch back and forth between widgets.

..class:: HelpPopup
    :synopsis: This class creates a simple popup GUI with a text edit window
    and a button to close the popup.  The text edit portion is not editable
    by the user, but rather gets populated from a .txt file.

..class:: HLSPIngest
    :synopsis: This class launches a PyQt window with two buttons: Help, which
    launches a HelpPopup class object, and Quit, which closes this window.
    This class also contains a QTabWidget with two tabs: one containing an
    ExtGenerator class object, the other containing a ConfigGenerator class
    object
"""

import os
import sys
from gui.config_generator import *
from gui.ext_generator import *
from gui.select_files import *
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

#--------------------

class HelpPopup(QDialog):
    """
    Define the help popup window that appears when the user clicks the 'Help'
    button.
    """

    def __init__(self):
        super().__init__()
        self.helpUI()

    def helpUI(self):
        #Get the help text from a .txt file.
        path = "gui/help.txt"
        help_path = os.path.abspath(path)
        self.helpbox = QTextEdit()
        self.helpbox.setReadOnly(True)
        self.helpbox.setLineWrapMode(QTextEdit.NoWrap)
        with open(help_path, "r") as helpfile:
            for line in helpfile.readlines():
                raw_line = line.strip("\n")
                self.helpbox.append(raw_line)
            helpfile.close()

        self.closebutton = QPushButton("Close")
        self.closebutton.clicked.connect(self.closeClicked)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.helpbox)
        self.vbox.addWidget(self.closebutton)
        self.setLayout(self.vbox)
        self.setWindowTitle("ConfigGenerator Help")
        self.resize(600, 600)
        self.show()

    def closeClicked(self):
        self.close()

#--------------------

class CAOMPopup(QDialog):
    """
    Define the help popup window that appears when the user clicks the 'Help'
    button.
    """

    def __init__(self):
        super().__init__()
        self.caomUI()

    def caomUI(self):
        #Get the help text from a .txt file.
        path = "gui/caom_parameters.txt"
        caom_path = os.path.abspath(path)
        self.caombox = QTextEdit()
        self.caombox.setReadOnly(True)
        self.caombox.setLineWrapMode(QTextEdit.NoWrap)
        with open(caom_path, "r") as caomfile:
            for line in caomfile.readlines():
                raw_line = line.strip("\n")
                self.caombox.append(raw_line)
            caomfile.close()

        self.closebutton = QPushButton("Close")
        self.closebutton.clicked.connect(self.closeClicked)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.caombox)
        self.vbox.addWidget(self.closebutton)
        self.setLayout(self.vbox)
        self.setWindowTitle("CAOM Parameters")
        self.resize(600, 600)
        self.show()

    def closeClicked(self):
        self.close()

#--------------------

class HLSPIngest(QTabWidget):
    """
    Create a tab widget to contain widgets from /gui/ext_generator.py and
    /gui/config_generator.py.  Provide options to quit or open a help dialog.
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()
        self.tab1 = SelectFiles()
        self.tab2 = ConfigGenerator()
        self.tabs.addTab(self.tab1, "Enter File Descriptions")
        self.tabs.addTab(self.tab2, "Make Config File")

        self.help = QPushButton("Help")
        self.help.setMaximumWidth(75)
        self.help.setStyleSheet("""
                                QPushButton {
                                    background-color: #f2f2f2;
                                    border: 2px solid #afafaf;
                                    border-radius: 8px;
                                    height: 20px
                                    }
                                QPushButton:hover {
                                    border: 4px solid #afafaf;
                                    }
                                QPushButton:pressed {
                                    background-color: #afafaf;
                                    }""")
        self.caom = QPushButton("CAOM")
        self.caom.setMaximumWidth(75)
        self.caom.setStyleSheet("""
                                QPushButton {
                                    background-color: #f2f2f2;
                                    border: 2px solid #afafaf;
                                    border-radius: 8px;
                                    height: 20px
                                    }
                                QPushButton:hover {
                                    border: 4px solid #afafaf;
                                    }
                                QPushButton:pressed {
                                    background-color: #afafaf;
                                    }""")
        self.quit = QPushButton("Quit")
        self.quit.setMaximumWidth(75)
        self.quit.setStyleSheet("""
                                QPushButton {
                                    background-color: #ffced0;
                                    border: 2px solid #ff9195;
                                    border-radius: 8px;
                                    height: 20px
                                    }
                                QPushButton:hover {
                                    border: 4px solid #ff9195;
                                    }
                                QPushButton:pressed {
                                    background-color: #ff9195;
                                    }""")

        #Create a third column to stretch so the Help and Quit buttons
        #remain over to the left.
        self.space = QLabel("")
        self.space.setMinimumWidth(500)

        """
        self.file_count = QTextEdit()
        self.file_count.setReadOnly(True)
        self.file_count.setLineWrapMode(QTextEdit.NoWrap)
        self.file_count.setStyleSheet("border-style: solid; \
                                  border-width: 0px; \
                                  background: rgba(235,235,235,0%); \
                                  text-align: right;")
        self.file_count.setText("Hi")
        """
        self.file_count = QLabel("No file types selected")
        self.file_count.setAlignment(Qt.AlignRight)

        self.box = QGridLayout()
        self.box.addWidget(self.tabs, 1, 0, -1, -1)
        self.box.addWidget(self.help, 0, 0)
        self.box.addWidget(self.caom, 0, 1)
        self.box.addWidget(self.quit, 0, 2)
        self.box.addWidget(self.space, 0, 3)
        self.box.addWidget(self.file_count, 0, 4)
        self.setLayout(self.box)
        self.resize(1000,300)
        self.setWindowTitle("ConfigGenerator")
        self.show()

        self.quit.clicked.connect(self.quitClicked)
        self.help.clicked.connect(self.helpClicked)
        self.caom.clicked.connect(self.caomClicked)
        self.tab1.save.clicked.connect(self.selectClicked)

    def quitClicked(self):
        self.close()

    def helpClicked(self):
        self.helppop = HelpPopup()
        self.helppop.exec_()

    def caomClicked(self):
        self.caompop = CAOMPopup()
        self.caompop.exec_()

    def selectClicked(self):
        self.tab2.file_types = self.tab1.selected_files
        n_selected = str(len(self.tab1.selected_files))
        self.file_count.setText("{0} file types selected".format(n_selected))


#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = HLSPIngest()
    sys.exit(app.exec_())
