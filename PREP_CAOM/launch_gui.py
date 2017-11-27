import os
import sys
from gui.config_generator import *
from gui.ext_generator import *
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

class HelpPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.helpUI()

    def helpUI(self):
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

class HLSPIngest(QTabWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()
        self.tab1 = ExtGenerator()
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
        self.space = QLabel("")

        self.box = QGridLayout()
        self.box.addWidget(self.tabs, 1, 0, -1, -1)
        self.box.addWidget(self.help, 0, 0)
        self.box.addWidget(self.quit, 0, 1)
        self.box.addWidget(self.space, 0, 2)
        self.setLayout(self.box)
        self.resize(1000,300)
        self.setWindowTitle("ConfigGenerator")
        self.show()

        self.quit.clicked.connect(self.quitClicked)
        self.help.clicked.connect(self.helpClicked)

    def quitClicked(self):
        self.close()

    def helpClicked(self):
        self.helppop = HelpPopup()
        self.helppop.exec_()

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = HLSPIngest()
    sys.exit(app.exec_())
