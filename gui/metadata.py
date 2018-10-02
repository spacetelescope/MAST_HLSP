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
    ..synopsis::  Update all "Data Type" dropboxes when any new standard is
                  selected.  Currently, we only handle a single data type at
                  a time.

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
        self._first_file = self._next_file = (head_row+1)
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
        self.metacheck_button = gb.GreenButton(
            "Check Metadata of Selected File(s)", 70)
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
        ft = QLabel(new_file.ftype)

        # GUI elements to display and select FITS standard information.
        standard = QComboBox()
        standard.addItems(sorted(self.standards))
        standard.setCurrentText("_".join([new_file.product_type,
                                          new_file.standard
                                          ]))
        standard.currentIndexChanged.connect(self._set_data_types)

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
        if new_file.run_check:
            self.selected_count += 1
        toggle_meta.stateChanged.connect(self._update_selected)

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

        # Increment self._next_file.
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

    def _set_data_types(self):

        sender = self.sender()
        ind = self.files_grid.indexOf(sender)
        pos = self.files_grid.getItemPosition(ind)
        row = pos[0]

        std = self.files_grid.itemAtPosition(row,
                                             self._standard_col
                                             )
        dt = std.widget().currentText().split("_")[0]

        for row in range(self._first_file, self._next_file):
            data_type = self.files_grid.itemAtPosition(row,
                                                       self._data_type_col
                                                       )
            data_type.widget().setCurrentText(dt)

    def _toggle_prechecked(self):

        if self._next_file == self._first_file or self.selected_count == 0:
            self.metacheck_button.setEnabled(False)
            self.master.hlsp.ingest["01_metadata_prechecked"] = False
        else:
            self.metacheck_button.setEnabled(True)
            self.master.hlsp.ingest["01_metadata_prechecked"] = True

    def _update_selected(self, state):
        """
        sender = self.sender()
        ind = self.files_grid.indexOf(sender)
        pos = self.files_grid.getItemPosition(ind)
        row = pos[0]
        standard_col = 1
        std = self.files_grid.itemAtPosition(row, standard_col).widget()
        """

        if state == Qt.Checked:
            self.selected_count += 1
            # std.setVisible(True)
        else:
            self.selected_count -= 1
            # std.setVisible(False)

        self._toggle_prechecked()

    def add_found_files(self, types_list):

        for ftype in types_list:
            name = list(ftype.keys())
            if len(name) > 1:
                continue
            else:
                name = name[0]
            # print("<<<metadata sending>>>{0}".format(ftype[name]))
            as_obj = FileType(name, param_dict=ftype[name])
            # print("<<<as_obj>>>{0}".format(as_obj.as_dict()))
            self.master.hlsp.add_filetype(as_obj)

        self.load_hlsp()

    def clear_files(self):

        while self._next_file > self._first_file:
            self._del_file_row()
        self.selected_count = 0

    def load_hlsp(self):

        self.clear_files()

        for ft in self.master.hlsp.file_types:
            self._add_file_row(ft)

        self._toggle_prechecked()

    def metacheck_clicked(self):

        check_metadata_format(self.master.hlsp.as_dict(), is_file=False)
        self.master.hlsp.ingest["02_metadata_checked"] = True
        self.update_hlsp_file(save=True)

    def precheck_clicked(self):

        hlsp_dir = self.master.hlsp.file_paths["InputDir"]
        hlsp_name = self.master.hlsp.hlsp_name
        results = precheck_data_format(hlsp_dir, hlsp_name)
        results_dict = read_yaml(results)
        types_found = results_dict["FileTypes"]
        self.type_count_label.setText(
            "...found {0} file types".format(len(types_found)))
        # print("<<<metadata GUI found>>> {0}".format(types_found))
        self.clear_files()
        self.add_found_files(types_found)
        self.update_hlsp_file(save=True)

    def update_hlsp_file(self, save=None):

        for n in range(self._first_file, self._next_file):
            self._read_file_row(n)

        if save:
            self.master.hlsp.save()

# --------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CheckMetadataGUI(parent=None)
    sys.exit(app.exec_())
