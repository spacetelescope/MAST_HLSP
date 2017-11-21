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

        self.box = QHBoxLayout()
        self.box.addWidget(self.tabs)
        self.setLayout(self.box)
        self.resize(900,300)
        self.setWindowTitle("ConfigGenerator")
        self.show()

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = HLSPIngest()
    sys.exit(app.exec_())
