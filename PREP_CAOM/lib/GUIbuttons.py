"""
All classes contained here are PyQt QPushButton subclasses with specific
formatting applied to maintain consistency throughout GUI forms.

..class::  BlueButton
    :synopsis: Light blue background, dark blue border, border thickness on
    hover, and dark blue fill-in on click.

..class:: GreenButton
    :synopsis: Light green background, dark green border, border thickness on
    hover, and dark green fill-in on click.

..class:: GreyButton
    :synopsis: Light grey background, dark grey border, border thickness on
    hover, and dark grey fill-in on click.

..class:: RedButton
    :synopsis: Light red background, dark red border, border thickness on
    hover, and dark red fill-in on click.
"""

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

#--------------------

class BlueButton(QPushButton):
    """ Blue GUI button with user-provided height and optional width
    parameters.
    """

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

#--------------------

class GreenButton(QPushButton):
    """ Green GUI button with user-provided height and optional width
    parameters.
    """

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

#--------------------

class GreyButton(QPushButton):
    """ Grey GUI button with user-provided height and optional width
    parameters.
    """

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

#--------------------

class RedButton(QPushButton):
    """ Red GUI button with user-provided height and optional width
    parameters.
    """

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
