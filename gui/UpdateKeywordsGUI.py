import gui.GUIbuttons as gb
import os
import sys

from bin.read_yaml import read_yaml
from CHECK_METADATA_FORMAT.check_metadata_format import check_metadata_format
from CHECK_METADATA_FORMAT.precheck_data_format import precheck_data_format
from lib.FileType import FileType
from lib.FitsKeyword import FitsKeyword

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

TEMPLATES_DIR = "CHECK_METADATA_FORMAT/TEMPLATES"


class UpdateKeywordsGUI(QWidget):

    def __init__(self, parent):

        super().__init__(parent)
        self.master = parent

        cwd = os.getcwd()
        self.templates_dir = "/".join([cwd, TEMPLATES_DIR])
        self.standard_template = None

        update_button = gb.GreenButton("Update from current .hlsp file", 70)
        update_button.clicked.connect(self.load_current_fits)

        self.display_grid = QGridLayout()

        bold = QFont()
        bold.setBold(True)
        standard_fits_label = QLabel("Standard FITS Keyword")
        standard_fits_label.setFont(bold)
        caom_keyword_label = QLabel("CAOM Keyword")
        caom_keyword_label.setFont(bold)
        alternate_fits_label = QLabel("Alternate FITS Keyword")
        alternate_fits_label.setFont(bold)
        header_num_label = QLabel("Header #")
        header_num_label.setFont(bold)
        default_val_label = QLabel("Default")
        default_val_label.setFont(bold)

        self._keywords = []
        self._standard_fits_col = 0
        self._caom_keyword_col = 1
        self._alternate_fits_col = 2
        self._header_num_col = 3
        self._default_val_col = 4

        label_row = 1
        self._first_filetype = self._next_filetype = (label_row+1)

        self.display_grid.addWidget(standard_fits_label,
                                    label_row,
                                    self._standard_fits_col
                                    )
        self.display_grid.addWidget(caom_keyword_label,
                                    label_row,
                                    self._caom_keyword_col
                                    )
        self.display_grid.addWidget(alternate_fits_label,
                                    label_row,
                                    self._alternate_fits_col
                                    )
        self.display_grid.addWidget(header_num_label,
                                    label_row,
                                    self._header_num_col
                                    )
        self.display_grid.addWidget(default_val_label,
                                    label_row,
                                    self._default_val_col
                                    )

        self.new_keyword_button = gb.GreyButton("+ add a new keyword", 30)
        self.new_keyword_button.clicked.connect(self._add_new_keyword_row)

        self.meta_grid = QGridLayout()
        self.meta_grid.addWidget(update_button, 0, 0)
        self.meta_grid.addLayout(self.display_grid, 1, 0)
        self.meta_grid.addWidget(self.new_keyword_button, 2, 0)

        self.setLayout(self.meta_grid)
        self.show()

    def _add_keyword_row(self, fits_key=None, info=None):

        fits_kw = QLabel()
        caom_kw = QLabel()
        alt_fits_kw = QLineEdit()
        hdr_num = QLineEdit()
        def_val = QLineEdit()

        if fits_key and info:
            new_keyword_obj = FitsKeyword(fits_key, parameters=info)
            self._keywords.append(new_keyword_obj)
            fits_kw.setText(fits_key)
            caom_kw.setText(info["caom_keyword"])
            hdr_num.setText(str(info["header"]))
            try:
                def_val.setText(str(info["default"]))
            except KeyError:
                pass

        self.display_grid.addWidget(fits_kw,
                                    self._next_filetype,
                                    self._standard_fits_col
                                    )
        self.display_grid.addWidget(caom_kw,
                                    self._next_filetype,
                                    self._caom_keyword_col
                                    )
        self.display_grid.addWidget(alt_fits_kw,
                                    self._next_filetype,
                                    self._alternate_fits_col
                                    )
        self.display_grid.addWidget(hdr_num,
                                    self._next_filetype,
                                    self._header_num_col
                                    )
        self.display_grid.addWidget(def_val,
                                    self._next_filetype,
                                    self._default_val_col
                                    )

        self.display_grid.setRowStretch(self._next_filetype, 0)
        self._next_filetype += 1
        self.display_grid.setRowStretch(self._next_filetype, 1)

    def _add_new_keyword_row(self):

        empty_standard = QLabel()
        # caom_kw =

    def _get_current_standard(self):

        standards = self.master.hlsp.member_fits_standards()
        if standards is None:
            std_label = QLabel("No FITS standard found!")
        elif len(standards) > 1:
            std_label = QLabel("More than 1 FITS standard found!")
        else:
            std_label = QLabel("Loaded {0} keywords".format(standards[0]))
        self.display_grid.addWidget(std_label, 0, 0)

        std = ".".join([standards[0], "yml"])
        self.standard_template = "/".join([self.templates_dir, std])

    def _load_standard_template(self):

        if not self.standard_template:
            return

        template = read_yaml(self.standard_template)
        keywords = template["KEYWORDS"]

        for key, info in keywords.items():
            self._add_keyword_row(key, info)

    def _read_keyword_row(self, row_num):

        std_fits = self.display_grid.itemAtPosition(row_num,
                                                    self._standard_fits_col
                                                    )
        caom_kw = self.display_grid.itemAtPosition(row_num,
                                                   self._caom_keyword_col
                                                   )
        new_fits = self.display_grid.itemAtPosition(row_num,
                                                    self._alternate_fits_col
                                                    )
        hdr_num = self.display_grid.itemAtPosition(row_num,
                                                   self._header_num_col
                                                   )
        default = self.display_grid.itemAtPosition(row_num,
                                                   self._default_val_col
                                                   )

        row_info_dict = {}
        alternates = new_fits.widget().text()
        alternates = [a.strip() for a in alternates.split(",")]
        if len(alternates) == 1 and alternates[0] == "":
            alternates = None
        row_info_dict["alternates"] = alternates
        row_info_dict["header"] = hdr_num.widget().text()
        row_info_dict["default"] = default.widget().text()
        if row_info_dict["default"] == "":
            row_info_dict["default"] = None

        for kw_obj in self._keywords:
            if kw_obj.fits_keyword == std_fits.widget().text():
                update_flag = kw_obj.update(row_info_dict)
                if update_flag:
                    print("UpdateKeywordsGUI found update")
                    self.master.hlsp.add_keyword_update(kw_obj)

    def load_current_fits(self):

        self._get_current_standard()
        self._load_standard_template()

    def update_hlsp_file(self):

        for row in range(self._first_filetype, self._next_filetype):
            self._read_keyword_row(row)
