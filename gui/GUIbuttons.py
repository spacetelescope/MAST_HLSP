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
    #from PyQt5.QtCore import *
    from PyQt5.QtWidgets import QPushButton
except ImportError:
    #from PyQt4.QtCore import *
    from PyQt4.QtGui import QPushButton

# --------------------


class MyButton(QPushButton):
    """
    GUI button with user-provided height and optional width
    parameters.
    """

    bkgd_color = "#f2f2f2"
    brdr_color = "#afafaf"

    def __init__(self, label, height, width=0, min_width=0):

        super().__init__(label)
        self.border = float(height * 0.05)
        self.radius = float(height * 0.15)
        self.height = height
        self.__update_style__()

        if width > 0:
            self.setMaximumWidth(width)

        if min_width > 0:
            self.setMinimumWidth(min_width)

    def __update_style__(self):
        self.setStyleSheet(
            """QPushButton {
                    background-color: """ + self.bkgd_color + """;
                    border-width: """ + str(self.border) + """px;
                    border-style: solid;
                    border-color: """ + self.brdr_color + """;
                    border-radius: """ + str(self.radius) + """;
                    height: """ + str(self.height - (self.border * 4)) + """;
                    }
                QPushButton:hover {
                    border-width: """ + str(self.border * 2) + """px;
                    }
                QPushButton:pressed {
                    background-color: """ + self.brdr_color + """;
                    }
                QPushButton:disabled {
                    border: 0px;
                    height: """ + str(self.height) + """;
                    }""")

    def set_style(self, new_class):
        self.bkgd_color = new_class.bkgd_color
        self.brdr_color = new_class.brdr_color
        self.__update_style__()

# --------------------


class BlueButton(MyButton):
    """ Blue GUI button with user-provided height and optional width
    parameters.
    """

    bkgd_color = "#42d4f4"
    brdr_color = "#005fa3"

    def __init__(self, label, height, width=0, min_width=0):
        super().__init__(label, height, width=width, min_width=min_width)

# --------------------


class GreenButton(MyButton):
    """ Green GUI button with user-provided height and optional width
    parameters.
    """

    bkgd_color = "#7af442"
    brdr_color = "#45a018"

    def __init__(self, label, height, width=0, min_width=0):
        super().__init__(label, height, width=width, min_width=min_width)

# --------------------


class GreyButton(MyButton):
    """ Grey GUI button with user-provided height and optional width
    parameters.
    """

    bkgd_color = "#f2f2f2"
    brdr_color = "#afafaf"

    def __init__(self, label, height, width=0, min_width=0):
        super().__init__(label, height, width=width, min_width=min_width)

# --------------------


class RedButton(MyButton):
    """ Red GUI button with user-provided height and optional width
    parameters.
    """

    bkgd_color = "#ffced0"
    brdr_color = "#ff9195"

    def __init__(self, label, height, width=0, min_width=0):
        super().__init__(label, height, width=width, min_width=min_width)
