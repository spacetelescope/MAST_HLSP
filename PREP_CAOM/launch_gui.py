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

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

#--------------------

def get_file_to_load(parent, prompt):

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
    """ Define the help popup window that appears when the user clicks the
    'Help' button.
    """

    def __init__(self):
        super().__init__()
        self.caomUI()

    def caomUI(self):
        # Get the help text from a .txt file.
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
        self.loadtypes = gb.GreyButton("Load .param File", height, big_width)
        self.loadyaml = gb.GreyButton("Load .config File", height, big_width)
        self.reset = gb.RedButton("Reset Forms", height, big_width)
        self.help = gb.GreyButton("Help", height, small_width)
        self.caom = gb.GreyButton("CAOM", height, small_width)
        self.quit = gb.RedButton("Quit", height, small_width)
        self.space = QLabel("")
        self.space.setMinimumWidth(200)
        self.buttonsgrid = QGridLayout()
        self.buttonsgrid.addWidget(self.loadtypes, 0, 0)
        self.buttonsgrid.addWidget(self.loadyaml, 0, 1)
        self.buttonsgrid.addWidget(self.reset, 0, 2)
        self.buttonsgrid.addWidget(self.help, 0, 4)
        #self.buttonsgrid.addWidget(self.caom, 0, 5)
        self.buttonsgrid.addWidget(self.quit, 0, 5)
        self.buttonsgrid.addWidget(self.space, 0, 3)

        # Make a Layout for the file_types display along the right side.
        filetypes_label = QLabel("File types selected: ")
        filetypes_label.setMaximumWidth(125)
        self.filetypes_display = QTextEdit()
        self.filetypes_display.setMaximumWidth(200)
        self.filetypes_display.setReadOnly(True)
        self.filetypes_display.setLineWrapMode(QTextEdit.NoWrap)
        self.filetypes_display.setStyleSheet("background: \
                                             rgba(235,235,235,0%);")
        types_font = QFont()
        types_font.setPointSize(16)
        self.filetypes_display.setFont(types_font)
        self.filetypes_display.setMinimumWidth(150)
        self.filetypes_display.setTextColor(Qt.red)
        self.filetypes_display.append("No file types selected")
        self.filetypesgrid = QGridLayout()
        self.filetypesgrid.addWidget(filetypes_label, 0, 0)
        self.filetypesgrid.addWidget(self.filetypes_display, 1, 0)

        # Make a read-only text box to display status messages
        res_label = QLabel("Messages:")
        res_label.setAlignment(Qt.AlignHCenter)
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setLineWrapMode(QTextEdit.NoWrap)
        self.status.setStyleSheet("border-style: solid; \
                                  border-width: 1px; \
                                  background: rgba(235,235,235,0%);")
        self.outputgrid = QGridLayout()
        self.outputgrid.addWidget(res_label, 0, 0)
        self.outputgrid.addWidget(self.status, 1, 0)

        # Make a Layout for the two big "Generate" buttons at the bottom-right
        self.gen = gb.GreenButton("Generate YAML File", 40)
        self.run = gb.BlueButton("Generate YAML and Run Script", 40)
        self.gen.setMinimumWidth(250)
        self.run.setMinimumWidth(250)
        self.gengrid = QGridLayout()
        self.gengrid.addWidget(self.space, 0, 0)
        self.gengrid.addWidget(self.gen, 1, 0)
        self.gengrid.addWidget(self.run, 2, 0)
        self.gengrid.setRowStretch(0, 1)
        self.gengrid.setRowStretch(1, 0)
        self.gengrid.setRowStretch(2, 0)

        # Add all sub-layouts and the tabs widget to the overall Layout
        self.box = QGridLayout()
        self.box.addLayout(self.buttonsgrid, 0, 0, 1, -1)
        self.box.addWidget(self.tabs, 2, 0)
        self.box.addLayout(self.filetypesgrid, 2, 1)
        self.box.addLayout(self.outputgrid, 3, 0)
        self.box.addLayout(self.gengrid, 3, 1)
        self.setLayout(self.box)
        self.resize(1100,500)

        # Center the window
        qtRectangle = self.frameGeometry()
        print(qtRectangle)
        screen = QDesktopWidget().availableGeometry()
        x = (screen.width() - qtRectangle.width()) / 2
        y = (screen.height() - qtRectangle.height()) / 2
        self.move(x, y)

        # Name and display the window
        self.setWindowTitle("ConfigGenerator")
        self.show()

        # Connect all the buttons
        self.quit.clicked.connect(self.quitClicked)
        self.help.clicked.connect(self.helpClicked)
        self.caom.clicked.connect(self.caomClicked)
        self.loadtypes.clicked.connect(self.loadTypesClicked)
        self.loadyaml.clicked.connect(self.loadYAMLClicked)
        self.reset.clicked.connect(self.resetClicked)
        self.gen.clicked.connect(self.genClicked)
        self.run.clicked.connect(self.genAndRunClicked)
        self.tab1.select_signal.connect(self.selectClicked)

    def bad_message(self, msg):
        self.status.setTextColor(Qt.red)
        self.status.append(msg)

    def good_message(self, msg):
        self.status.setTextColor(Qt.darkGreen)
        self.status.append(msg)

    def neutral_message(self, msg):
        self.status.setTextColor(Qt.black)
        self.status.append(msg)

    #def handleErrors(self, msg):


    def loadTypesClicked(self):
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
            self.good_message("Loaded {0}".format(filename))

        # Catch any MyError instances and write them to the status box.
        except MyError as err:
            self.bad_message(err.message)

    def loadYAMLClicked(self):
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
            self.good_message("Loaded {0}".format(filename))

        # Catch any MyError instances and write them to the status box.
        except MyError as err:
            self.bad_message(err.message)

    def resetClicked(self):
        """ Open a confirmation popup before clearing both tabs.
        """

        # Open a confirmation popup window
        self.cc = ClearConfirm("Reset all entries on both forms?")
        self.cc.exec_()

        # Execute reset modules for both tabs if confirmed
        if self.cc.confirm:
            self.tab1.clearClicked(source="wrapper")
            self.tab2.resetClicked()
            self.neutral_message("Forms reset")

    def collectAndSaveTabInputs(self):
        """ Collect all the inputs from tab2 and add the file_types list to
        the dictionary.  Then save it to a .config YAML file.
        """

        # Raise errors if file_types is empty or None.  Means user has not
        # loaded or selected any file types.
        if self.file_types is None:
            self.bad_message("No file types selected!")
            return None
        elif len(self.file_types.keys()) == 0:
            self.bad_message("No file types selected!")
            return None

        # Collect inputs from tab2 and add file_types to the resulting
        # dictionary
        try:
            config = self.tab2.collectInputs()
            config["file_types"] = self.file_types
        except MyError as err:
            self.bad_message(err.message)
            return None

        # Get a file name using a save dialog and save the dictionary to a
        # YAML-formatted file with a .config extension
        saveit = QFileDialog.getSaveFileName(self, "Save YAML file", ".")
        if len(saveit[0]) > 0:
            saveit = os.path.abspath(saveit[0])
            if not saveit.endswith(".config"):
                saveit += ".config"
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
            self.good_message("Saved {0}".format(inputs))

    def genAndRunClicked(self):
        """ Try to generate a YAML .config file, then pass that along to
        hlsp_to_xml.
        """

        inputs = self.collectAndSaveTabInputs()
        if inputs is None:
            return
        else:
            self.good_message("Saved {0}".format(inputs))
            self.good_message("Launching hlsp_to_xml...")
            self.good_message("...see terminal for output...")
            hlsp_to_xml(inputs)

    def quitClicked(self):
        self.close()

    def helpClicked(self):
        self.helppop = HelpPopup()
        self.helppop.exec_()

    def caomClicked(self):
        self.caompop = CAOMPopup()
        self.caompop.exec_()

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
                self.filetypes_display.append("*"+t)

#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = HLSPIngest()
    sys.exit(app.exec_())
