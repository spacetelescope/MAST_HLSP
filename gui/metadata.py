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


class CheckMetadataGUI(QWidget):

    def __init__(self, parent):

        super().__init__(parent)
        self.master = parent

        self.selected_count = 0

        cwd = os.getcwd()
        templates_dir = "/".join([cwd, TEMPLATES_DIR])
        templates = os.listdir(templates_dir)
        self.standards = [t.split(".")[0] for t in templates]

        precheck_button = gb.GreenButton("Pre-check File Metadata", 70)
        precheck_button.clicked.connect(self.precheck_clicked)
        self.precheck_grid = QGridLayout()
        self.precheck_grid.addWidget(precheck_button, 0, 0)

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
        mrp_head = QLabel("MRP?")
        mrp_head.setFont(bold)

        head_row = 0
        self._first_file = self._next_file = (head_row+1)
        self._file_end_col = 0
        self._standard_col = 1
        self._data_type_col = 2
        self._file_type_col = 3
        self._product_type_col = 4
        self._check_meta_col = 5
        self._mrp_col = 6

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
        self.files_grid.addWidget(mrp_head,
                                  head_row,
                                  self._mrp_col
                                  )

        self.metacheck_button = gb.GreenButton(
            "Check Metadata of Selected File(s)", 70)
        self.metacheck_button.clicked.connect(self.metacheck_clicked)
        self.metacheck_button.setEnabled(False)
        self.check_grid = QGridLayout()
        self.check_grid.addWidget(self.metacheck_button, 0, 0)

        self.type_count_label = QLabel()
        self.meta_grid = QGridLayout()
        self.meta_grid.addLayout(self.precheck_grid, 0, 0)
        self.meta_grid.addWidget(self.type_count_label, 1, 0)
        self.meta_grid.addLayout(self.files_grid, 2, 0)
        self.meta_grid.addLayout(self.check_grid, 3, 0)

        self.meta_grid.setRowStretch(0, 0)
        self.meta_grid.setRowStretch(1, 0)
        self.meta_grid.setRowStretch(2, 1)

        self.setLayout(self.meta_grid)
        self.show()

    def _add_file_row(self, new_file):

        ft = QLabel(new_file.ftype)

        if self._next_file == self._first_file:
            standard = QComboBox()
            standard.addItems(sorted(self.standards))
            standard.currentIndexChanged.connect(self._set_data_types)
        else:
            standard = QLabel()

        data_type = QComboBox()
        data_type.addItems(new_file.valid_pt)
        data_type.setCurrentText(new_file.product_type)

        file_type = QComboBox()
        file_type.addItems(new_file.valid_ft)
        file_type.setCurrentText(new_file.file_type)

        product_type = QComboBox()
        product_type.addItems(new_file.valid_cpt)
        product_type.setCurrentText(new_file.caom_product_type)

        toggle_meta = QCheckBox()
        toggle_meta.setChecked(new_file.run_check)
        if new_file.run_check:
            self.selected_count += 1
        toggle_meta.stateChanged.connect(self._update_selected)

        toggle_mrp = QCheckBox()
        toggle_mrp.setChecked(new_file.mrp_check)

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
        self.files_grid.addWidget(toggle_mrp,
                                  self._next_file,
                                  self._mrp_col
                                  )

        self._next_file += 1

    def _del_file_row(self):

        self._next_file -= 1
        n_elements = self.files_grid.columnCount()
        for n in range(n_elements):
            x = self.files_grid.itemAtPosition(self._next_file, n).widget()
            x.setParent(None)

    def _read_file_row(self, row_num):

        ending = self.files_grid.itemAtPosition(row_num, 0).widget()
        std = self.files_grid.itemAtPosition(self._first_file, 1).widget()
        dt = self.files_grid.itemAtPosition(row_num, 2).widget()
        ft = self.files_grid.itemAtPosition(row_num, 3).widget()
        pt = self.files_grid.itemAtPosition(row_num, 4).widget()
        chk = self.files_grid.itemAtPosition(row_num, 5).widget().checkState()
        mrp = self.files_grid.itemAtPosition(row_num, 6).widget().checkState()

        for ft_obj in self.master.hlsp.file_types:
            if ft_obj.ftype == ending.text():
                ft_obj.standard = std.currentText().split("_")[-1]
                ft_obj.product_type = dt.currentText()
                ft_obj.file_type = ft.currentText()
                ft_obj.caom_product_type = pt.currentText()
                ft_obj.run_check = (True if chk == Qt.Checked else False)
                ft_obj.mrp_check = (True if mrp == Qt.Checked else False)

    def _set_data_types(self):

        std = self.files_grid.itemAtPosition(self._first_file, 1).widget()
        dt = std.currentText().split("_")[0]
        for row in range(self._first_file, self._next_file):
            data_type = self.files_grid.itemAtPosition(row, 2).widget()
            data_type.setCurrentText(dt)

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

    def clear_files(self):

        while self._next_file > self._first_file:
            self._del_file_row()
        self.selected_count = 0

    def display_files(self, types_list):

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
            self._add_file_row(as_obj)

        self._toggle_prechecked()

    def metacheck_clicked(self):

        self.master.hlsp.ingest["02_metadata_checked"] = True
        self.update_hlsp_file()
        check_metadata_format(self.master.hlsp.as_dict(), is_file=False)

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
        self.display_files(types_found)
        self.update_hlsp_file()

    def update_hlsp_file(self):

        for n in range(self._first_file, self._next_file):
            self._read_file_row(n)
        self.master.hlsp.save()


# --------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CheckMetadataGUI(parent=None)
    sys.exit(app.exec_())
