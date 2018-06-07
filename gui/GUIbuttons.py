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
        self.height = str(height)
        self.setStyleSheet("""
                            QPushButton {
                                background-color: """ + self.bkgd_color + """;
                                border: 2px solid """ + self.brdr_color + """;
                                border-radius: 8px;
                                height: """ + str(height) + """;
                                }
                              QPushButton:hover {
                                border: 4px solid """ + self.brdr_color + """;
                                }
                              QPushButton:pressed {
                                background-color: """ + self.brdr_color + """;
                                }""")

        if width > 0:
            self.setMaximumWidth(width)

        if min_width > 0:
            self.setMinimumWidth(min_width)

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
