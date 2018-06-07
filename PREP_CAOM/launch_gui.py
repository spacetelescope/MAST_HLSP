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
from hlsp_to_xml import hlsp_to_xml

import lib.GUIbuttons as gb
from lib.ClearConfirm import ClearConfirm
from lib.MyError import MyError

from gui.config_generator import *
from gui.select_files import *

from util.read_yaml import read_yaml

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

#--------------------

def get_file_to_load(parent, prompt):
    """ Use a file dialog pop up to get a user-determined filename for file
    creation and saving.

    :param prompt:  The text to use in the dialog pop up window.
    :type prompt:  str
    """

    loadit = QFileDialog.getOpenFileName(parent, prompt, ".")
    filename = loadit[0]

    if filename == "":
        return None
    else:
        return filename

#--------------------

class HelpPopup(QDialog):
    """ Define the help popup window that appears when the user clicks the
    'Help' button.
    """

    def __init__(self):
        super().__init__()
        self.helpUI()

    def helpUI(self):
        # Get the help text from a .txt file.
        path = "gui/help.txt"
        help_path = os.path.abspath(path)
        help_box = QTextEdit()
        help_box.setReadOnly(True)
        help_box.setLineWrapMode(QTextEdit.NoWrap)
        with open(help_path, "r") as helpfile:
            for line in helpfile.readlines():
                raw_line = line.strip("\n")
                help_box.append(raw_line)
            helpfile.close()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.closeClicked)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(help_box)
        self.vbox.addWidget(self.close_button)
        self.setLayout(self.vbox)
        self.setWindowTitle("ConfigGenerator Help")
        self.resize(600, 600)
        self.show()

    def closeClicked(self):
        self.close()

#--------------------

class HLSPIngest(QTabWidget):
    """ Create a tab widget to contain widgets from /gui/ext_generator.py and
    /gui/config_generator.py.  Provide options to quit or open a help dialog.
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # Set up the tabs contained in this widget
        self.tabs = QTabWidget()
        self.tab1 = SelectFiles()
        self.tab2 = ConfigGenerator()
        self.tabs.addTab(self.tab1, "Select File Types")
        self.tabs.addTab(self.tab2, "Make Config File")

        # Initialize the file_types variable to None
        self.file_types = None

        # Use the GUIbuttons classes to make all necessary buttons, then
        # create a space label to separate buttons on the right and left sides.
        # Make a Layout for the buttons along the top row.
        height = 30
        big_width = 160
        small_width = 120
        space_width = 200
        load_param = gb.GreyButton("Load .param File", height, big_width)
        load_config = gb.GreyButton("Load .config File", height, big_width)
        reset_button = gb.RedButton("Reset Forms", height, big_width)
        help_button = gb.GreyButton("Help", height, small_width)
        quit_button = gb.RedButton("Quit", height, small_width)
        space_label = QLabel("")
        space_label.setMinimumWidth(space_width)
        self.buttons_grid = QGridLayout()
        self.buttons_grid.addWidget(load_param, 0, 0)
        self.buttons_grid.addWidget(load_config, 0, 1)
        self.buttons_grid.addWidget(reset_button, 0, 2)
        self.buttons_grid.addWidget(help_button, 0, 4)
        self.buttons_grid.addWidget(quit_button, 0, 5)
        self.buttons_grid.addWidget(space_label, 0, 3)

        # Make a Layout for the file_types display along the right side.
        filetypes_label = QLabel("File types selected: ")
        filetypes_label.setMaximumWidth(125)
        self.filetypes_display = QTextEdit()
        self.filetypes_display.setMaximumWidth(200)
        self.filetypes_display.setReadOnly(True)
        self.filetypes_display.setLineWrapMode(QTextEdit.NoWrap)
        self.filetypes_display.setStyleSheet("background: \
                                             rgba(235,235,235,0%);")
        filetypes_font = QFont()
        filetypes_font.setPointSize(16)
        self.filetypes_display.setFont(filetypes_font)
        self.filetypes_display.setMinimumWidth(150)
        self.filetypes_display.setTextColor(Qt.red)
        self.filetypes_display.append("No file types selected")
        self.filetypes_grid = QGridLayout()
        self.filetypes_grid.addWidget(filetypes_label, 0, 0)
        self.filetypes_grid.addWidget(self.filetypes_display, 1, 0)

        # Make a read-only text box to display status messages
        messages_label = QLabel("Messages:")
        messages_label.setAlignment(Qt.AlignHCenter)
        self.messages_display = QTextEdit()
        self.messages_display.setReadOnly(True)
        self.messages_display.setLineWrapMode(QTextEdit.NoWrap)
        self.messages_display.setStyleSheet("border-style: solid; \
                                            border-width: 1px; \
                                            background: rgba(235,235,235,0%);")
        self.messages_grid = QGridLayout()
        self.messages_grid.addWidget(messages_label, 0, 0)
        self.messages_grid.addWidget(self.messages_display, 1, 0)

        # Make a Layout for the two big "Generate" buttons at the bottom-right
        self.generate = gb.GreenButton("Generate .config File", 40)
        self.run = gb.BlueButton("Generate .config and Run Script", 40)
        self.generate.setMinimumWidth(250)
        self.run.setMinimumWidth(250)
        self.action_grid = QGridLayout()
        self.action_grid.addWidget(space_label, 0, 0)
        self.action_grid.addWidget(self.generate, 1, 0)
        self.action_grid.addWidget(self.run, 2, 0)
        self.action_grid.setRowStretch(0, 1)
        self.action_grid.setRowStretch(1, 0)
        self.action_grid.setRowStretch(2, 0)

        # Add all sub-layouts and the tabs widget to the overall Layout
        self.meta_grid = QGridLayout()
        self.meta_grid.addLayout(self.buttons_grid, 0, 0, 1, -1)
        self.meta_grid.addWidget(self.tabs, 2, 0)
        self.meta_grid.addLayout(self.filetypes_grid, 2, 1)
        self.meta_grid.addLayout(self.messages_grid, 3, 0)
        self.meta_grid.addLayout(self.action_grid, 3, 1)
        self.setLayout(self.meta_grid)
        self.resize(1100,500)

        # Center the window
        qtRectangle = self.frameGeometry()
        screen = QDesktopWidget().availableGeometry()
        x = (screen.width() - qtRectangle.width()) / 2
        y = (screen.height() - qtRectangle.height()) / 2
        self.move(x, y)

        # Name and display the window
        self.setWindowTitle("ConfigGenerator")
        self.show()

        # Connect all the buttons
        quit_button.clicked.connect(self.quitClicked)
        help_button.clicked.connect(self.helpClicked)
        load_param.clicked.connect(self.loadHLSPClicked)
        load_config.clicked.connect(self.loadConfigClicked)
        reset_button.clicked.connect(lambda: self.resetClicked(confirm=True))
        self.generate.clicked.connect(self.genClicked)
        self.run.clicked.connect(self.genAndRunClicked)
        self.tab1.select_signal.connect(self.selectClicked)

    def badMessage(self, msg):
        self.messages_display.setTextColor(Qt.red)
        self.messages_display.append(str(msg))

    def goodMessage(self, msg):
        self.messages_display.setTextColor(Qt.darkGreen)
        self.messages_display.append(str(msg))

    def neutralMessage(self, msg):
        self.messages_display.setTextColor(Qt.black)
        self.messages_display.append(str(msg))

    def loadHLSPClicked(self):
        filename = get_file_to_load(self, "Load an .hlsp file")
        if filename is None:
            return

        try:
            self.hlsp_yaml = read_yaml(filename)
        except TypeError as err:
            self.badMessage(err)
            return

        try:
            file_paths = self.hlsp_yaml["FilePaths"]
        except KeyError:
            file_paths = None
        else:
            self.tab2.loadConfigPaths(file_paths)

        try:
            file_types = self.hlsp_yaml["FileTypes"]
            data_product_type = []
            standard = []
            for ftype, params in file_types.items():
                pt = params["ProductType"]
                std = params["Standard"]
                if pt not in data_product_type and pt != "none":
                    data_product_type.append(params["ProductType"])
                if std not in standard and std != "none":
                    standard.append(params["Standard"])
            if len(data_product_type) == 1:
                data_product_type = data_product_type[0]
            else:
                data_product_type = None
                self.badMessage("Multiple data product types found in the "
                                ".hlsp file!")
            if len(standard) == 1:
                standard = standard[0]
            else:
                standard = None
                self.badMessage("Multiple .fits header standards found in "
                                "the .hlsp file!")
        except KeyError:
            data_product_type = None
            file_types = None
            standard = None
        else:
            self.tab1.loadFileTypes(file_types)
            self.tab2.setProductType(data_product_type)
            self.tab2.setHeaderStandard(standard)
            self.selectClicked()

        try:
            key_updates = self.hlsp_yaml["KeywordUpdates"]
        except KeyError:
            key_updates = None

        try:
            new_parameters = self.hlsp_yaml["UniqueParameters"]
        except KeyError:
            new_parameters = None

        #self.tab2.loadConfigInfo(file_paths, )

    def loadParamClicked(self):
        """ Load a dictionary of file extensions into the tab1 Select File
        Types widget using a tab1 module.
        """

        # Get a file name using a dialog and skip if None is returned
        filename = get_file_to_load(self, "Load YAML File")
        if filename is None:
            return

        # Use the loadExtensionsYAML module to load values into the tab1
        # widget.  Automatically select these loaded entries and inidicate
        # they've been selected.
        try:
            self.tab1.loadExtensionsYAML(filename=filename)
            self.tab1.saveClicked()
            self.selectClicked()
            self.tab2.loadParamFile(filename)
            self.goodMessage("Loaded {0}".format(filename))

        # Catch any MyError instances and write them to the status box.
        except MyError as err:
            self.badMessage(err.message)

    def loadConfigClicked(self):
        """ Get a YAML config file name and pass it to both tab1 and tab2
        modules to load the information.
        """

        # Get a file name using a dialog and skip if None is returned
        filename = get_file_to_load(self, "Load YAML File")
        if filename is None:
            return

        # Use the loadConfigYAML and loadFromYAML modules in tab1 and tab2
        # to load parameters from filename.  Select the loaded file types and
        # display them.
        try:
            self.tab1.loadConfigYAML(filename=filename)
            self.tab1.saveClicked()
            self.selectClicked()
            self.tab2.loadFromYAML(filename=filename)
            self.goodMessage("Loaded {0}".format(filename))

        # Catch any MyError instances and write them to the status box.
        except MyError as err:
            self.badMessage(err.message)

    def resetClicked(self, confirm=True):
        """ Open a confirmation popup before clearing both tabs.
        """

        # Open a confirmation popup window
        if confirm:
            self.cc = ClearConfirm("Reset all entries on both forms?")
            self.cc.exec_()
            if not self.cc.confirm:
                return

        # Execute reset modules for both tabs if confirmed
        self.tab1.clearClicked(confirm=False)
        self.tab2.resetClicked()
        self.resize(1100,500)
        self.neutralMessage("Forms reset")

    def collectAndSaveTabInputs(self):
        """ Collect all the inputs from tab2 and add the file_types list to
        the dictionary.  Then save it to a .config YAML file.
        """

        # Raise errors if file_types is empty or None.  Means user has not
        # loaded or selected any file types.
        if self.file_types is None:
            self.badMessage("No file types selected!")
            return None
        elif len(self.file_types.keys()) == 0:
            self.badMessage("No file types selected!")
            return None

        # Collect inputs from tab2 and add file_types to the resulting
        # dictionary
        try:
            config = self.tab2.collectInputs()
        except MyError as err:
            self.badMessage(err.message)
            return None
        else:
            config["file_types"] = self.file_types

        # Get a file name using a save dialog and save the dictionary to a
        # YAML-formatted file with a .config extension
        saveit = QFileDialog.getSaveFileName(self, "Save YAML file", ".")
        if len(saveit[0]) > 0:
            saveit = os.path.abspath(saveit[0])
            if not saveit.endswith(".config"):
                ".".join([saveit, "config"])
            with open(saveit, 'w') as output:
                yaml.dump(config, output, default_flow_style=False)
                output.close()
            print("Saved {0}".format(saveit))
        else:
            return None

        return saveit

    def genClicked(self):
        """ Try to generate a YAML .config file and catch any errors thrown.
        """

        inputs = self.collectAndSaveTabInputs()
        if inputs is None:
            return
        else:
            self.goodMessage("Saved {0}".format(inputs))

    def genAndRunClicked(self):
        """ Try to generate a YAML .config file, then pass that along to
        hlsp_to_xml.
        """

        inputs = self.collectAndSaveTabInputs()
        if inputs is None:
            return
        else:
            self.goodMessage("Saved {0}".format(inputs))
            self.goodMessage("Launching hlsp_to_xml...")
            self.goodMessage("...see terminal for output...")
            hlsp_to_xml(inputs)

    def quitClicked(self):
        self.close()

    def helpClicked(self):
        helppop = HelpPopup()
        helppop.exec_()

    def selectClicked(self):
        """ When the "Select these types" button is clicked in tab1, we want
        to set the file_types variable and update the displayed list of
        selected types for confirmation.
        """

        self.file_types = self.tab1.selected_files
        self.types_list = sorted(self.file_types.keys())
        self.filetypes_display.clear()
        if len(self.types_list) == 0:
            self.filetypes_display.setTextColor(Qt.red)
            self.filetypes_display.append("No file types selected")
        else:
            self.filetypes_display.setTextColor(Qt.black)
            for t in self.types_list:
                self.filetypes_display.append("*_"+t)

#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = HLSPIngest()
    sys.exit(app.exec_())
