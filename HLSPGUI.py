import os
import sys
import time
import yaml
base = sys.path[0]
subdirectories = [x for x in os.listdir(base) if (os.path.isdir(x)
                                                  and x[0] is not ".")
                  ]
subpackages = [os.path.join(base, subdir) for subdir in subdirectories]
sys.path = subpackages + sys.path

from bin.read_yaml import read_yaml
from gui.GUIbuttons import BlueButton, GreenButton, GreyButton, RedButton
from gui.CheckFilenamesGUI import CheckFilenamesGUI
from gui.metadata import CheckMetadataGUI
from gui.ClearConfirm import ClearConfirm
from gui.FilenameConfirm import FilenameConfirm
from gui.MyError import MyError
from gui.UpdateKeywordsGUI import UpdateKeywordsGUI
from gui.ValueParametersGUI import ValueParametersGUI
from lib.HLSPFile import HLSPFile

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

# --------------------


class TimerThread(QThread):

    def __init__(self, label):

        super().__init__()
        self._label = label

    def run(self):

        start = time.time()

        while True:
            time.sleep(1)
            now = time.time()
            elapsed = int(now - start)
            m = str(int(elapsed / 60)).zfill(2)
            s = str(elapsed % 60).zfill(2)
            as_string = "{0}:{1}".format(m, s)
            self._label.setText("(elapsed time: {0})".format(as_string))

# --------------------


class HLSPGUI(QTabWidget):
    """
    This class creates a master GUI for HLSP software execution.  It uses a
    tab widget to incorporate different GUI's for different steps of the
    ingest process.  It also includes some over-arching functionality, such
    as specifiying the HLSP data directory, and load/save execution.

    ..module::  closeEvent
    ..synopsis::  Intercepting the closeEvent signal allows us to prompt the
                  user to save the .hlsp file in progress.

    ..module::  load_hlsp
    ..synopsis::  Read data from an existing .hlsp file and update all the tab
                  GUI's.

    ..module::  save_hlsp
    ..synopsis::  Update the current HLSPFile object and then save that to a
                  specified file.

    ..module::  update_hlsp_path
    ..synopsis::  Update the appropriate HLSPFile attribute when the user
                  updates the HLSP data path.
    """

    files_updated = pyqtSignal(object)
    ready = pyqtSignal()
    running = pyqtSignal()

    def __init__(self):

        super().__init__()

        # Begin with an empty HLSPFile object in memory.
        self.hlsp = HLSPFile()

        self._files_found = None
        self.busy = False
        self.ready.connect(self._ready)
        self.running.connect(self._running)

        # Set up autosave variable to pass to child GUIs.
        self.auto_save = "_autosave.hlsp"

        # Elements to launch loading a pre-existing .hlsp file.
        load_button = GreyButton("Load an .hlsp File", 70, min_width=150)
        load_button.clicked.connect(self.load_hlsp)

        # Elements to change the file path to find HLSP data.
        path_label = QLabel("HLSP Data Path: ")
        self.hlsp_path_edit = QLineEdit()
        # self.hlsp_path_edit.insert(os.getcwd())
        self.hlsp_path_edit.insert(
            "/Users/pforshay/Documents/1709_hlsp/hlsp_data")
        self.hlsp_path_edit.textEdited.connect(self.update_hlsp_path)

        # Elements to change HLSP name and file name values.
        name_label = QLabel("HLSP Name: ")
        self.hlsp_name_edit = QLineEdit()
        file_label = QLabel("Save As: ")
        self.file_name_edit = QLineEdit()

        # Elements to launch saving the HLSPFile object to a YAML file.
        save_hlsp_button = GreyButton("Save to .hlsp File", 70, min_width=150)
        save_hlsp_button.clicked.connect(self.save_hlsp)

        self.header_grid = QGridLayout()
        self.header_grid.addWidget(load_button, 0, 0, 2, 1)
        self.header_grid.addWidget(path_label, 0, 1)
        self.header_grid.addWidget(self.hlsp_path_edit, 0, 2, 1, 3)
        self.header_grid.addWidget(save_hlsp_button, 0, 5, 2, 1)
        self.header_grid.addWidget(name_label, 1, 1)
        self.header_grid.addWidget(self.hlsp_name_edit, 1, 2)
        self.header_grid.addWidget(file_label, 1, 3)
        self.header_grid.addWidget(self.file_name_edit, 1, 4)

        # Set up the tabs contained in this widget
        self.tabs = QTabWidget()
        self.step1 = CheckFilenamesGUI(parent=self)
        self.step2 = CheckMetadataGUI(parent=self)
        self.step3 = UpdateKeywordsGUI(parent=self)
        self.step4 = ValueParametersGUI(parent=self)
        self.tabs.addTab(self.step1, "1: Check Filenames")
        self.tabs.addTab(self.step2, "2: Check Metadata")
        self.tabs.addTab(self.step3, "3: Update FITS Keywords")
        self.tabs.addTab(self.step4, "4: Edit Value Parameters")
        self.tbar = self.tabs.tabBar()
        # self.tbar.setTabTextColor(0, Qt.red)

        self.flag_bar = FlagBar()

        self.status = QLabel("> Ready")
        self.status.setMaximumWidth(80)
        self.counter = QLabel("counter")
        self.files_updated.connect(self._update_count)
        window_width = self.frameGeometry().width()
        self.spacer = QSpacerItem(int(window_width * 0.8), 1)
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.timer = TimerThread(self.counter)

        self.progress_grid = QGridLayout()
        self.progress_grid.addWidget(self.status, 0, 0, 1, 1)
        self.progress_grid.addWidget(self.counter, 0, 1, 1, 1)
        self.progress_grid.addItem(self.spacer, 0, 2, 1, -1)
        self.progress_grid.addWidget(self.progress, 1, 0, 1, -1)

        # Create a grid layout and add all the elements.
        self.meta_grid = QVBoxLayout()
        self.meta_grid.addLayout(self.header_grid)
        self.meta_grid.addWidget(self.tabs)
        self.meta_grid.addLayout(self.progress_grid)
        self.meta_grid.addLayout(self.flag_bar)

        # Set the layout and size properties.
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

    def _ready(self):

        self.status.setText("> Ready")
        self.busy = False
        if self.timer.isRunning():
            self.timer.terminate()

    def _running(self):

        self.status.setText("> Running...")
        self.busy = True
        self.timer.start()

    def _update_count(self):

        self.counter.setText("{0} files found".format(self.files_found))

    @property
    def files_found(self):
        return self._files_found

    @files_found.setter
    def files_found(self, value):
        self._files_found = value
        self.files_updated.emit(value)

    def closeEvent(self, event):
        """
        Prompt the user to save the HLSPFile object before closing the GUI.
        """

        event.accept()
        """
        save_prompt = ClearConfirm("Save to .hlsp file?")
        save_prompt.exec_()
        if save_prompt.confirm:
            event.accept()
        else:
            event.ignore()
        """

    def current_config(self):

        return self.hlsp_path_edit.text(), self.hlsp_name_edit.text().lower()

    def load_hlsp(self):
        """
        Load data from an existing .hlsp file into an HLSPFile object, then
        update the GUI's with this new data.
        """

        # Launch the file selection dialog to locate an .hlsp file.
        prompt = "Select an .hlsp file to load:"
        filename = get_file_to_load(self, prompt)

        # Leave the module if the user cancels.
        if not filename:
            return

        # Clear the current entries.
        self.hlsp_name_edit.clear()
        self.hlsp_path_edit.clear()
        self.file_name_edit.clear()

        # Set self.hlsp to a new HLSPFile object using the user-selected file.
        self.hlsp = HLSPFile(path=filename)
        print("<HLSPGUI> load_hlsp() keyword_updates:")
        self.hlsp.keyword_updates.__display__()
        print("<<<>>>")

        # Update the line edit elements in the master GUI using the new
        # HLSPFile parameters.
        self.hlsp_name_edit.insert(self.hlsp.hlsp_name)
        self.hlsp_path_edit.insert(self.hlsp.file_paths["InputDir"])
        self.file_name_edit.insert(filename.split("/")[-1])

        # Launch the load modules for each GUI in the tabs.
        for step in sorted(self.hlsp.ingest.keys()):
            done = self.hlsp.ingest[step]
            num = int(step[1])

            if not done:
                self.flag_bar.turn_off(num)
                break
            elif step.startswith("00"):
                self.step1.load_hlsp(self.hlsp)
            elif step.startswith("01"):
                self.step2.load_hlsp()
            elif step.startswith("03"):
                self.step3.load_current_fits()
            elif step.startswith("04"):
                self.step4.refresh_parameters()

            self.flag_bar.turn_on(num)

    def save_hlsp(self):
        """
        Make sure the HLSPFile object has all the current GUI data, then save
        it to a file.
        """

        # Launch the update modules for each GUI in the tabs.
        self.step2.update_hlsp_file()
        self.step3.update_hlsp_file()
        self.step4.update_hlsp_file()

        # If the "Save As:" line edit has an entry, use this as the file name.
        save_as = self.file_name_edit.text()
        if save_as:
            self.hlsp.save(filename=save_as)

        # If the "Save As:" line edit is empty, launch a FilenameConfirm dialog
        # window.
        else:
            name_dialog = FilenameConfirm(self.hlsp.hlsp_name)
            name_dialog.exec_()

            # If the FilenameConfirm dialog has a valid string, use this to
            # save the HLSPFile, and insert that into the "Save As:" line.
            if name_dialog.file:
                new_file = self.hlsp.save(filename=name_dialog.file)
                self.file_name_edit.insert(new_file)

            # If the FilenameConfirm dialog is empty, the user hit 'Cancel'.
            else:
                return

    def update_hlsp_path(self):
        """
        Update the HLSPFile object filepaths data.  Don't think this is
        actually used...
        """

        current_path = self.hlsp_path_edit.text()
        self.hlsp.update_filepaths(input=current_path)
        self.hlsp.toggle_updated(True)

# --------------------


class FlagBar(QHBoxLayout):

    off_css = ("font-style: italic; "
               "color: #ffaaaa; "
               "text-align: center; "
               "border: 4px inset #ffaaaa; "
               )
    on_css = ("font-style: normal; "
              "font-weight: bold; "
              "color: #45a018; "
              "text-align: center; "
              "border: 4px outset #45a018; "
              )

    def __init__(self):

        super().__init__()

        self.flag_labels = {0: QLabel("Filenames Checked"),
                            1: QLabel("File Metadata Pre-Checked"),
                            2: QLabel("File Metadata Checked"),
                            3: QLabel("FITS Keywords Updated"),
                            4: QLabel("Value Parameters Added")
                            }

        for x in sorted(self.flag_labels.keys()):
            widg = self.flag_labels[x]
            widg.setStyleSheet(self.off_css)
            self.addWidget(widg)

    def turn_on(self, ind):

        widg = self.flag_labels[ind]
        widg.setStyleSheet(self.on_css)

    def turn_off(self, ind):

        widg = self.flag_labels[ind]
        widg.setStyleSheet(self.off_css)

# --------------------


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

# --------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = HLSPGUI()
    sys.exit(app.exec_())
