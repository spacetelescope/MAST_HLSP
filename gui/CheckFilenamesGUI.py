from CHECK_FILE_NAMES import (check_in_known_missions,
                              check_dirpath_lower,
                              check_file_compliance,
                              check_file_names,
                              check_in_known_filters,
                              check_is_version_string,
                              get_all_files)
#import CHECK_FILE_NAMES.check_file_names
#from CHECK_FILE_NAMES.check_file_names import check_file_names
import gui.GUIbuttons as gb
import os
import sys

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *


class CheckFilenamesGUI(QWidget):
    """
    This class creates a GUI to execute file name checking on an HLSP data
    directory, and view the results.

    ..module::  _update_button_state
    ..synopsis::  Updates the approve_button status and appearance based on
                  the self.approved value.

    ..module::  current_input
    ..synopsis::  Reads the current HLSP data path and name from the master
                  GUI.

    ..module::  load_hlsp
    ..synopsis::  Update the GUI with data from an .hlsp file.

    ..module::  run
    ..synopsis::  Execute the file name checking software.

    ..module::  toggle_approve
    ..synopsis::  Toggles the self.approved value and updates the GUI and
                  HLSPFile accordingly.

    ..module::  toggle_run
    ..synopsis::  Toggles the GUI button to run the filename check software
                  based on whether or not enough information is present.
    """

    def __init__(self, parent):

        super().__init__(parent=parent)

        # Set up necessary attributes.
        self.master = parent
        self.approved = False
        self.unapproved_text = ("An Archive Scientist has not yet approved"
                                " these filenames:"
                                )
        self.approved_text = ("An Archive Scientist has approved these "
                              "filenames:"
                              )

        # Elements to launch filename checking.
        run_label = QLabel("Check filename formatting in the current HLSP "
                           "path:"
                           )
        self.run_button = gb.GreenButton("Run", 60)
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.run)

        # Elements to approve file name verification after checking.
        self.approve_label = QLabel(self.unapproved_text)
        self.approve_button = gb.GreenButton("Approve", 60)
        self.approve_button.setEnabled(False)
        self.approve_button.clicked.connect(self.toggle_approve)

        # Elements to display the log file results from file name checking.
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.NoWrap)
        self.log_display.setStyleSheet("border-style: solid; "
                                       "border-width: 1px; "
                                       "background: rgba(235,235,235,0%);"
                                       )

        # Connect to text editing signals in the parent GUI.
        self.master.hlsp_name_edit.textChanged.connect(self.toggle_run)
        self.master.hlsp_path_edit.textChanged.connect(self.toggle_run)

        # Set up a grid layout.
        self.grid = QGridLayout()
        self.grid.addWidget(run_label, 0, 0)
        self.grid.addWidget(self.approve_label, 0, 1)
        self.grid.addWidget(self.run_button, 1, 0)
        self.grid.addWidget(self.approve_button, 1, 1)
        self.grid.addWidget(self.log_display, 2, 0, 1, -1)

        # Display the GUI.
        self.setLayout(self.grid)
        self.show()

    def _display_log(self, log):

        self.master.ready.emit()

        with open(log, 'r') as logfile:
            log_lines = logfile.readlines()

        for line in log_lines:
            if "Started at" in line:
                self.log_display.clear()
            self.log_display.append(line[:-1])

    def _update_button_state(self):
        """
        Update the approve_button status and appearance based on the
        self.approved value.
        """

        # If the filenames have been approved, change this to a red "Unapprove"
        # button.
        if self.approved:
            self.master.flag_bar.turn_on(0)
            self.approve_label.setText(self.approved_text)
            self.approve_button.set_style(gb.RedButton)
            self.approve_button.setText("Unapprove")
            self.approve_button.setEnabled(True)

        # If the filenames have not been approved, change this to a green
        # "Approve" button.
        else:
            self.master.flag_bar.turn_off(0)
            self.approve_label.setText(self.unapproved_text)
            self.approve_button.set_style(gb.GreenButton)
            self.approve_button.setText("Approve")
            self.approve_button.setEnabled(False)

    def current_input(self):
        """
        Read the current HLSP parameters from the parent GUI.
        """

        # Get the current HLSP data path and name values.
        current_path = self.master.hlsp_path_edit.text()
        current_name = self.master.hlsp_name_edit.text().lower()

        return current_path, current_name

    def load_hlsp(self, hlsp_file):
        """
        Given a new approved state, update the GUI.

        :param new_approved:  The filenames checked state from a loaded .hlsp
                              file.
        :type new_approved:  bool
        """

        # Update the self.approved value and trigger a button state update.
        logfile = hlsp_file.find_log_file("check_file_names.py", here=True)
        self.approved = hlsp_file.check_ingest_step(0)
        self._update_button_state()

        if self.approved:
            self._display_log(logfile)

    def run(self):
        """
        Launch the filename checking scripts in CHECK_FILE_NAMES.
        """

        # Retrieve and expand the current HLSP data path and name values from
        # the parent GUI.
        current_path, current_name = self.master.current_config()
        current_path = os.path.abspath(current_path)

        # Launch the check_file_names module.
        self.master.progress.setValue(0)
        script = ScriptThread(current_path, current_name)
        script.finished.connect(lambda: self._display_log(script.log))
        self.master.running.emit()
        self.master.files_found = script.count
        script.start()
        self.master.progress.setValue(100)

        # Enable the approve button.
        self.approve_button.setEnabled(True)

    def toggle_approve(self):
        """
        Toggle the self.approved value.
        """

        # Update self.approved and trigger a button state update.
        self.approved = (not self.approved)
        self._update_button_state()

        # Get the file name parameters from the parent GUI.
        x, current_name = self.current_input()
        auto = self.master.auto_save

        # Update the HLSPFile object accordingly.
        self.master.hlsp.toggle_ingest(0, state=self.approved)
        self.master.hlsp.save(filename="".join([current_name, auto]))

    def toggle_run(self):
        """
        Toggle the button to launch check_file_names based on the information
        available.
        """

        # Read the current HLSP data path and name values.
        current_path, current_name = self.master.current_config()

        # Set the XML template filename based on the HLSP name.
        out_file = "_".join([current_name, "template.xml"])

        # Update the HLSPFile object.
        self.master.hlsp.update_filepaths(input=current_path, output=out_file)
        self.master.hlsp.hlsp_name = current_name

        # If either the data path or name are missing, disable the run button.
        # Otherwise, enable it.
        if current_path == "" or current_name == "":
            self.run_button.setEnabled(False)
        else:
            self.run_button.setEnabled(True)

# --------------------


class ScriptThread(QThread):

    def __init__(self, path, name):

        super().__init__()
        self._path = path
        self._name = name
        self.log = None
        self.count = None
        # self._count_files()

    def _count_files(self):

        temp = []
        for _p, _d, files in os.walk(self._path):
            temp.extend(files)

        self.count = len(temp)

    def run(self):

        self.log = check_file_names.check_file_names(self._path, self._name)


# --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CheckFilenamesGUI(parent=None)
    sys.exit(app.exec_())
