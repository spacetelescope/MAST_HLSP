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

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.master = parent
        self.approved = False
        self.unapproved_text = ("An Archive Scientist has not yet approved"
                                " these filenames:"
                                )
        self.approved_text = ("An Archive Scientist has approved these "
                              "filenames:"
                              )
        run_label = QLabel("Check filename formatting in the current HLSP "
                           "path:"
                           )
        self.run_button = gb.GreenButton("Run", 60)
        self.run_button.setEnabled(False)

        self.approve_label = QLabel(self.unapproved_text)
        self.approve_button = gb.GreenButton("Approve", 60)
        self.approve_button.setEnabled(False)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.NoWrap)
        self.log_display.setStyleSheet("border-style: solid; "
                                       "border-width: 1px; "
                                       "background: rgba(235,235,235,0%);"
                                       )

        self.master.hlsp_name_edit.textChanged.connect(self.toggle_run)
        self.master.hlsp_path_edit.textChanged.connect(self.toggle_run)
        self.run_button.clicked.connect(self.run)
        self.approve_button.clicked.connect(self.toggle_approve)

        self.grid = QGridLayout()
        self.grid.addWidget(run_label, 0, 0)
        self.grid.addWidget(self.approve_label, 0, 1)
        self.grid.addWidget(self.run_button, 1, 0)
        self.grid.addWidget(self.approve_button, 1, 1)
        self.grid.addWidget(self.log_display, 2, 0, 1, -1)

        self.setLayout(self.grid)
        self.show()

    def current_input(self):
        current_path = self.master.hlsp_path_edit.text()
        current_name = self.master.hlsp_name_edit.text()
        return current_path, current_name

    def run(self):
        current_path, current_name = self.current_input()
        current_path = os.path.abspath(current_path)
        check_log = check_file_names.check_file_names(current_path,
                                                      current_name)
        check_log = os.path.abspath(check_log)
        # self.log_display.clear()
        with open(check_log, 'r') as logfile:
            lines = logfile.readlines()

        for line in lines:
            if "Started at" in line:
                self.log_display.clear()
            self.log_display.append(line[:-1])

        self.approve_button.setEnabled(True)

    def toggle_approve(self):
        if self.approved:
            self.approved = False
            self.approve_label.setText(self.unapproved_text)
            self.approve_button.set_style(gb.GreenButton)
            self.approve_button.setText("Approve")
            self.approve_button.setEnabled(False)
        else:
            self.approved = True
            self.approve_label.setText(self.approved_text)
            self.approve_button.set_style(gb.RedButton)
            self.approve_button.setText("Unapprove")
        self.master.hlsp.ingest["filenames_checked"] = self.approved

    def toggle_run(self):
        current_path, current_name = self.current_input()
        if current_path == "" or current_name == "":
            self.run_button.setEnabled(False)
        else:
            self.run_button.setEnabled(True)

# --------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CheckFilenamesGUI(parent=None)
    sys.exit(app.exec_())
