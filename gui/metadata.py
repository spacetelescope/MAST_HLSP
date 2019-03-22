import gui.GUIbuttons as gb
import os
import sys

from bin.read_yaml import read_yaml
from CHECK_METADATA_FORMAT.check_metadata_format import check_metadata_format
from CHECK_METADATA_FORMAT.precheck_data_format import precheck_data_format
from lib.FileType import FileType

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

TEMPLATES_DIR = "CHECK_METADATA_FORMAT/TEMPLATES"

# --------------------


class CheckMetadataGUI(QWidget):
    """
    This class constructs a GUI to launch FITS metadata checking software found
    in CHECK_METADATA_FORMAT.

    ..module::  _add_file_row
    ..synopsis::  Add information from a FileType object into a new row in the
                  file types display area.

    ..module::  _del_file_row
    ..synopsis::  Remove the last row in the file types display area.

    ..module::  _read_file_row
    ..synopsis::  Read information from a file type row and use it to update
                  a FileType object in the parent HLSPFile object.

    ..module::  _set_data_types
    ..synopsis::  Update "Data Type" dropboxes when a new standard value is
                  selected.

    ..module::  _toggle_prechecked
    ..synopsis::  Check whether a metadata precheck has been executed, and
                  update the GUI and HLSPFile accordingly.

    ..module::  _update_selected
    ..synopsis::  Keep track of the number of file types included in this
                  observation.

    ..module::  add_found_files
    ..synopsis::  Add all file types found in the metadata precheck to the
                  HLSPFile and load these into the display area.

    ..module::  clear_files
    ..synopsis::  Remove all existing file type rows from the display area.

    ..module::  load_hlsp
    ..synopsis::  Add file types from an HLSPFile object to the GUI.

    ..module::  metacheck_clicked
    ..synopsis::  Launch check_metadata_format and update the HLSPFile.

    ..module::  precheck_clicked
    ..synopsis::  Launch precheck_data_format and display the results.  Update
                  and save the HLSPFile.

    ..module::  update_hlsp_file
    ..synopsis::  Add information from the file type rows to the parent
                  HLSPFile and save it if selected.
    """

    def __init__(self, parent):

        super().__init__(parent)

        # Set necessary attributes.
        self.master = parent
        self.selected_count = 0

        # Get a list of available FITS standards.
        cwd = os.getcwd()
        templates_dir = "/".join([cwd, TEMPLATES_DIR])
        templates = os.listdir(templates_dir)
        self.standards = [t.split(".")[0] for t in templates]

        # GUI elements to launch precheck_data_format.
        precheck_button = gb.GreenButton("Pre-check File Metadata", 70)
        precheck_button.clicked.connect(self.precheck_clicked)
        self.precheck_grid = QGridLayout()
        self.precheck_grid.addWidget(precheck_button, 0, 0)

        # GUI elements to display and update file type information.
        bold = QFont()
        bold.setBold(True)
        file_ending_head = QLabel("File Ending:")
        file_ending_head.setFont(bold)
        standard_head = QLabel("Standard:")
        standard_head.setFont(bold)
        data_type_head = QLabel("Data Type:")
        data_type_head.setFont(bold)
        file_type_head = QLabel("File Type:")
        file_type_head.setFont(bold)
        product_type_head = QLabel("Product Type:")
        product_type_head.setFont(bold)
        check_meta_head = QLabel("Check Metadata?")
        check_meta_head.setFont(bold)
        inc_head = QLabel("Include in Observation?")
        inc_head.setFont(bold)

        # Set column number variables to rearrange later if needed.
        head_row = 0
        self._first_file = self._next_file = (head_row + 1)
        self._file_end_col = 0
        self._standard_col = 1
        self._data_type_col = 2
        self._file_type_col = 3
        self._product_type_col = 4
        self._check_meta_col = 5
        self._inc_col = 6

        # Construct the file types display area.
        self.files_grid = QGridLayout()
        self.files_grid.addWidget(file_ending_head,
                                  head_row,
                                  self._file_end_col
                                  )
        self.files_grid.addWidget(standard_head,
                                  head_row,
                                  self._standard_col
                                  )
        self.files_grid.addWidget(data_type_head,
                                  head_row,
                                  self._data_type_col
                                  )
        self.files_grid.addWidget(file_type_head,
                                  head_row,
                                  self._file_type_col
                                  )
        self.files_grid.addWidget(product_type_head,
                                  head_row,
                                  self._product_type_col
                                  )
        self.files_grid.addWidget(check_meta_head,
                                  head_row,
                                  self._check_meta_col
                                  )
        self.files_grid.addWidget(inc_head,
                                  head_row,
                                  self._inc_col
                                  )

        # GUI elements to launch check_metadata_format.
        meta_msg = "Check Metadata of Selected File(s)"
        self.metacheck_button = gb.GreenButton(meta_msg, 70)
        self.metacheck_button.clicked.connect(self.metacheck_clicked)
        self.metacheck_button.setEnabled(False)
        self.check_grid = QGridLayout()
        self.check_grid.addWidget(self.metacheck_button, 0, 0)

        # Construct the overall layout.
        self.type_count_label = QLabel()
        self.meta_grid = QGridLayout()
        self.meta_grid.addLayout(self.precheck_grid, 0, 0)
        self.meta_grid.addWidget(self.type_count_label, 1, 0)
        self.meta_grid.addLayout(self.files_grid, 2, 0)
        self.meta_grid.addLayout(self.check_grid, 3, 0)

        self.meta_grid.setRowStretch(0, 0)
        self.meta_grid.setRowStretch(1, 0)
        self.meta_grid.setRowStretch(2, 1)

        # Display the GUI.
        self.setLayout(self.meta_grid)
        self.show()

    def _add_file_row(self, new_file):
        """
        Add information from a FileType object into a new row in the file
        types display area.

        :param new_file:  A new file type to add a GUI row for.
        :type new_file:  FileType
        """

        # GUI element to display file ending information.
        if self._next_file == self._first_file:
            ft = QLabel("(UPDATE ALL FILES)")
        else:
            ft = QLabel(new_file.ftype)

        # GUI elements to display and select FITS standard information.
        standard = QComboBox()
        standard.addItems(sorted(self.standards))
        standard.setCurrentText("_".join([new_file.product_type,
                                          str(new_file.standard)
                                          ]))

        # GUI elements to display and select data type information.
        data_type = QComboBox()
        data_type.addItems(new_file.valid_pt)
        data_type.setCurrentText(new_file.product_type)

        # GUI elements to display and select file type information
        file_type = QComboBox()
        file_type.addItems(new_file.valid_ft)
        file_type.setCurrentText(new_file.file_type)

        # GUI elements to display and select CAOM product type information.
        product_type = QComboBox()
        product_type.addItems(new_file.valid_cpt)
        product_type.setCurrentText(new_file.caom_product_type)

        # GUI elements to toggle inclusion in FITS metadata checks.
        toggle_meta = QCheckBox()
        toggle_meta.setChecked(new_file.run_check)

        # Track the number of files included for metadata checking.
        if new_file.run_check and self._next_file > self._first_file:
            self.selected_count += 1

        # GUI elements to toggle inclusion in this CAOM observation.
        toggle_inc = QCheckBox()
        toggle_inc.setChecked(True)

        # Construct the file type display area.
        self.files_grid.addWidget(ft,
                                  self._next_file,
                                  self._file_end_col
                                  )
        self.files_grid.addWidget(standard,
                                  self._next_file,
                                  self._standard_col
                                  )
        self.files_grid.addWidget(data_type,
                                  self._next_file,
                                  self._data_type_col
                                  )
        self.files_grid.addWidget(file_type,
                                  self._next_file,
                                  self._file_type_col
                                  )
        self.files_grid.addWidget(product_type,
                                  self._next_file,
                                  self._product_type_col
                                  )
        self.files_grid.addWidget(toggle_meta,
                                  self._next_file,
                                  self._check_meta_col
                                  )
        self.files_grid.addWidget(toggle_inc,
                                  self._next_file,
                                  self._inc_col
                                  )

        if self._next_file == self._first_file:
            standard.setStyleSheet("background-color:#d6d6d6;")
            data_type.setStyleSheet("background-color:#d6d6d6;")
            file_type.setStyleSheet("background-color:#d6d6d6;")
            product_type.setStyleSheet("background-color:#d6d6d6;")
            toggle_meta.setStyleSheet("background-color:#d6d6d6;")
            toggle_inc.setStyleSheet("background-color:#d6d6d6;")
            standard.currentIndexChanged.connect(self._set_all_in_column)
            data_type.currentIndexChanged.connect(self._set_all_in_column)
            file_type.currentIndexChanged.connect(self._set_all_in_column)
            product_type.currentIndexChanged.connect(self._set_all_in_column)
            toggle_meta.stateChanged.connect(self._set_all_in_column)
            toggle_inc.stateChanged.connect(self._set_all_in_column)
            self._next_file += 1
            self._add_file_row(new_file)
        else:
            toggle_meta.stateChanged.connect(self._update_selected)
            self._next_file += 1

    def _del_file_row(self):
        """
        Remove the last row in the file types display area.
        """

        # The _next_file pointer stays one row ahead of the final row, so move
        # this back to access the last row.
        self._next_file -= 1

        # Get the number of columns and remove each widget.
        n_elements = self.files_grid.columnCount()
        for n in range(n_elements):
            x = self.files_grid.itemAtPosition(self._next_file, n).widget()
            x.setParent(None)

    def _finish_metacheck(self, check_thread):

        self.master.ready.emit()

        # Set the metadata checked flag (may wish to incorporate some sort of
        # approval here as well).
        self.master.hlsp.toggle_ingest(2, state=True)
        self.master.flag_bar.turn_on(2)

        # Save the HLSPFile.
        self.update_hlsp_file(save=True)

    def _finish_precheck(self, precheck_thread):

        self.results = precheck_thread.results
        self.master.ready.emit()

        # Read the resulting log file.
        results_dict = read_yaml(self.results)
        types_found = results_dict["FileTypes"]

        # Display the precheck results and save the HLSPFile.
        self.type_count_label.setText(
            "...found {0} file types".format(len(types_found)))
        self.clear_files()
        self.add_found_files(types_found)
        self.update_hlsp_file(save=True)

    def _read_file_row(self, row_num):
        """
        Read information from a file type row and use it to update a FileType
        object in the parent HLSPFile object.

        :param row_num:  The row number we wish to pull values from.
        :type row_num:  int
        """

        # Access the widgets in the given row.
        ending = self.files_grid.itemAtPosition(row_num,
                                                self._file_end_col
                                                )
        std = self.files_grid.itemAtPosition(row_num,
                                             self._standard_col
                                             )
        dt = self.files_grid.itemAtPosition(row_num,
                                            self._data_type_col
                                            )
        ft = self.files_grid.itemAtPosition(row_num,
                                            self._file_type_col
                                            )
        pt = self.files_grid.itemAtPosition(row_num,
                                            self._product_type_col
                                            )
        chk = self.files_grid.itemAtPosition(row_num,
                                             self._check_meta_col
                                             )
        inc = self.files_grid.itemAtPosition(row_num,
                                             self._inc_col
                                             )

        # Find the corresponding FileType object in the HLSPFile.
        ft_obj = self.master.hlsp.find_file_type(ending.widget().text())

        # If a matching FileType was found, update its attributes.
        if ft_obj:
            ft_obj.standard = std.widget().currentText().split("_")[-1]
            ft_obj.product_type = dt.widget().currentText()
            ft_obj.file_type = ft.widget().currentText()
            ft_obj.caom_product_type = pt.widget().currentText()
            if chk.widget().checkState() == Qt.Checked:
                ft_obj.run_check = True
            else:
                ft_obj.run_check = False
            if inc.widget().checkState() != Qt.Checked:
                self.master.hlsp.remove_filetype(ft_obj)

    def _set_all_in_column(self):
        """
        Using the top row of selection widgets, propegate a choice in any of
        these to all widgets below in the same column.
        """

        # Get the position of the signal sender.
        sender = self.sender()
        ind = self.files_grid.indexOf(sender)
        pos = self.files_grid.getItemPosition(ind)
        col = pos[1]

        # Get the new selected value.
        new = self.files_grid.itemAtPosition(self._first_file, col).widget()
        if type(new) == QComboBox:
            new_val = new.currentText()
        elif type(new) == QCheckBox:
            new_val = new.checkState()

        # Update all widgets below with the new selected value.
        for row in range(self._first_file, self._next_file):
            current = self.files_grid.itemAtPosition(row, col).widget()

            if type(new) == QComboBox:
                current.setCurrentText(new_val)
            elif type(new) == QCheckBox:
                current.setChecked(new_val)

    def _set_data_types(self):
        """
        Upon changing a row's 'Standard' value, update the 'Data Type' value
        as well.  Currently, we can only handle one data type for a given
        observation, so changing any standard value will update all data types.
        """

        # Get the new standard value.
        std = self.files_grid.itemAtPosition(self._first_file,
                                             self._standard_col
                                             )
        dt = std.widget().currentText().split("_")[0]

        # Update all data type boxes with the new standard value.
        for row in range(self._first_file, self._next_file):
            data_type = self.files_grid.itemAtPosition(row,
                                                       self._data_type_col
                                                       )
            data_type.widget().setCurrentText(dt)

    def _toggle_prechecked(self):
        """
        Update button and status states based on whether file types have been
        found.
        """

        # If there are no file type rows or none have been selected, disable
        # the check_metadata_format button and set the HLSPFile flag.
        if self._next_file == self._first_file or self.selected_count == 0:
            self.metacheck_button.setEnabled(False)
            self.master.hlsp.toggle_ingest(1, state=False)
            self.master.flag_bar.turn_off(1)

        # Otherwise, enable the check_metadata_format button.
        else:
            self.metacheck_button.setEnabled(True)
            self.master.hlsp.toggle_ingest(1, state=True)
            self.master.flag_bar.turn_on(1)

    def _update_selected(self, state):
        """
        Track the number of file types the user has selected for metadata
        checking.
        """

        # Update the self.selected_count counter.
        if state == Qt.Checked:
            self.selected_count += 1
        else:
            self.selected_count -= 1

        # Trigger necessary GUI updates.
        self._toggle_prechecked()

    def add_found_files(self, types_list):
        """
        Use a list of file types returned from a precheck to create FileType
        objects and add them to the HLSPFile.

        :param types_list:  A list of file type dictionaries found by the
                            precheck_data_format script.
        :type types_list:  list
        """

        # Expecting a list of single-key dictionaries:
        # e.g. [{type: {key: val, key: val, ...}}, ...]
        for ftype in types_list:
            name = list(ftype.keys())

            # If a single dict lists multiple file types, ignore (this is
            # unexpected).
            if len(name) > 1:
                continue
            else:
                name = name[0]

            # Create a FileType class object.
            as_obj = FileType(name, param_dict=ftype[name])

            # Add the FileType object to the parent HLSPFile.
            self.master.hlsp.add_filetype(as_obj)

        # Load the newly-updated HLSPFile into the GUI.
        self.load_hlsp()

    def clear_files(self):
        """
        Remove all file type rows from the GUI and reset the counter.
        """

        # Remove the last row until _next_file points to _first_file.
        while self._next_file > self._first_file:
            self._del_file_row()

        self.selected_count = 0

    def load_hlsp(self):
        """
        Display the contents of the parent HLSPFile.file_types in the GUI.
        """

        # Clear anything currently displayed.
        self.clear_files()

        # Add a file type row for each FileType object in the HLSPFile.
        for ft in self.master.hlsp.file_types:
            self._add_file_row(ft)

        # Trigger additional GUI updates.
        self._toggle_prechecked()

    def metacheck_clicked(self):
        """
        Launch the check_metadata_format script to examine FITS keywords in
        the selected data files.
        """

        self.update_hlsp_file()

        # Launch check_metadata_format with the current contents of the parent
        # HLSPFile as a dict.
        self.master.running.emit()
        thr = CheckThread(self.master.hlsp.as_dict())
        print("metacheck_clicked made a CheckThread")
        thr.finished.connect(lambda: self._finish_metacheck(thr))
        print("metacheck_clicked connected the CheckThread")
        thr.start()

    def precheck_clicked(self):
        """
        Launch the precheck_data_format script and display any results.
        """

        # Read the current HLSP data path and name.
        hlsp_dir, hlsp_name = self.master.current_config()

        # Launch the precheck_data_format script.
        self.master.running.emit()
        thr = PrecheckThread(hlsp_dir, hlsp_name)
        thr.finished.connect(lambda: self._finish_precheck(thr))
        thr.start()

    def update_hlsp_file(self, save=None):
        """
        Read the current GUI contents to the HLSPFile in memory, with an
        option to save it.
        """

        # Read the current GUI contents.
        for n in range(self._first_file + 1, self._next_file):
            self._read_file_row(n)

        # Save the HLSPFile if selected.
        if save:
            name = self.master.hlsp.hlsp_name
            auto = self.master.auto_save
            self.master.hlsp.save(filename="".join([name, auto]))

# --------------------


class CheckThread(QThread):

    def __init__(self, hlsp_dict):

        super().__init__()
        self._hlsp = hlsp_dict
        print("CheckThread() initiated")

    def run(self):

        print("Beginning check_metadata_format")
        check_metadata_format(self._hlsp, is_file=False)
        print("check_metadata_format is done")

# --------------------


class PrecheckThread(QThread):

    def __init__(self, path, name):

        super().__init__()
        self._path = path
        self._name = name

    def run(self):

        self.results = precheck_data_format(self._path, self._name)


# --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CheckMetadataGUI(parent=None)
    sys.exit(app.exec_())
