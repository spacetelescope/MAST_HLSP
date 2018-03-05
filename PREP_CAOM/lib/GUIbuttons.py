try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

class BlueButton(QPushButton):
    def __init__(self, label, height, width=0):
        super().__init__(label)
        self.setStyleSheet("""
                                QPushButton {
                                    background-color: #42d4f4;
                                    border: 2px solid #005fa3;
                                    border-radius: 8px;
                                    height: """ + str(height) + """;
                                    }
                                  QPushButton:hover {
                                    border: 4px solid #005fa3;
                                    }
                                  QPushButton:pressed {
                                    background-color: #005fa3;
                                    }""")
        if width > 0:
            self.setMaximumWidth(width)

class GreenButton(QPushButton):
    def __init__(self, label, height, width=0):
        super().__init__(label)
        self.setStyleSheet("""
                                QPushButton {
                                    background-color: #7af442;
                                    border: 2px solid #45a018;
                                    border-radius: 8px;
                                    height: """ + str(height) + """;
                                    }
                                  QPushButton:hover {
                                    border: 4px solid #45a018;
                                    }
                                  QPushButton:pressed {
                                    background-color: #45a018;
                                    }""")
        if width > 0:
            self.setMaximumWidth(width)

class GreyButton(QPushButton):
    def __init__(self, label, height, width=0):
        super().__init__(label)
        self.setStyleSheet("""
                                QPushButton {
                                    background-color: #f2f2f2;
                                    border: 2px solid #afafaf;
                                    border-radius: 8px;
                                    height: """ + str(height) + """;
                                    }
                                QPushButton:hover {
                                    border: 4px solid #afafaf;
                                    }
                                QPushButton:pressed {
                                    background-color: #afafaf;
                                    }""")
        if width > 0:
            self.setMaximumWidth(width)

class RedButton(QPushButton):
    def __init__(self, label, height, width=0):
        super().__init__(label)
        self.setStyleSheet("""
                                QPushButton {
                                    background-color: #ffced0;
                                    border: 2px solid #ff9195;
                                    border-radius: 8px;
                                    height: """ + str(height) + """;
                                    }
                                QPushButton:hover {
                                    border: 4px solid #ff9195;
                                    }
                                QPushButton:pressed {
                                    background-color: #ff9195;
                                    }""")
        if width > 0:
            self.setMaximumWidth(width)
