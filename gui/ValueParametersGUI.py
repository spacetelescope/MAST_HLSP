import gui.GUIbuttons as gb
import os
import sys

from bin.read_yaml import read_yaml
from CHECK_METADATA_FORMAT.check_metadata_format import check_metadata_format
from CHECK_METADATA_FORMAT.precheck_data_format import precheck_data_format
from lib.CAOMKeywordBox import CAOMKeywordBox
import lib.CAOMXML as cx
from lib.FileType import FileType
from lib.FitsKeyword import FitsKeyword

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *


def make_standard_parameters(hlsp_obj):

    standard_entries = {"metadataList": {}}
    normal = {"collection": "HLSP",
              "intent": "SCIENCE",
              "observationID": "FILEROOTSUFFIX",
              }
    timeseries = {"algorithm": "timeseries"}
    kepler = {"aperture_radius": "4",
              "instrument_name": "Kepler",
              "targetPosition_coordsys": "ICRS",
              }

    fits_standards = hlsp_obj.member_fits_standards()
    if not fits_standards:
        return value_objs

    for fit in fits_standards:
        std, inst = fit.split("_")
        if std.lower() == "timeseries":
            normal.update(timeseries)
        if inst.lower() == "kepler" or inst.lower() == "k2":
            normal.update(kepler)

    standard_entries["metadataList"].update(normal)

    return standard_entries


class ValueParametersGUI(QWidget):

    def __init__(self, parent):

        super().__init__(parent)
        self.master = parent
        self.values_dict = {}

        bold = QFont()
        bold.setBold(True)

        caom_label = QLabel("CAOM Keyword:")
        caom_label.setFont(bold)
        xml_label = QLabel("XML Parent:")
        xml_label.setFont(bold)
        value_label = QLabel("Value:")
        value_label.setFont(bold)

        self._caom_col = 0
        self._xml_col = 1
        self._value_col = 2

        head_row = 0
        self._first_value = self._next_value = (head_row + 1)

        self.values_grid = QGridLayout()
        self.values_grid.addWidget(caom_label, head_row, self._caom_col)
        self.values_grid.addWidget(xml_label, head_row, self._xml_col)
        self.values_grid.addWidget(value_label, head_row, self._value_col)

        refresh_button = gb.GreyButton("Refresh from .hlsp file", 40)
        refresh_button.clicked.connect(self.refresh_parameters)
        add_button = gb.GreyButton("+ add a new parameter", 40)
        add_button.clicked.connect(self._add_value)
        template_button = gb.GreenButton("Generate an XML Template file", 40)
        template_button.clicked.connect(self.generate_xml_clicked)

        self.meta_grid = QGridLayout()
        self.meta_grid.addWidget(refresh_button, 0, 0)
        self.meta_grid.addWidget(add_button, 0, 1)
        self.meta_grid.addLayout(self.values_grid, 1, 0, 1, -1)
        self.meta_grid.addWidget(template_button, 2, 0, 1, -1)

        self.setLayout(self.meta_grid)
        self.show()

    def _add_value(self, obj=None):

        new_caom = CAOMKeywordBox()
        new_caom.currentIndexChanged.connect(self._fill_default_xml)
        new_xml = QLineEdit()
        new_value = QLineEdit()

        self.values_grid.addWidget(new_caom,
                                   self._next_value,
                                   self._caom_col
                                   )
        self.values_grid.addWidget(new_xml,
                                   self._next_value,
                                   self._xml_col
                                   )
        self.values_grid.addWidget(new_value,
                                   self._next_value,
                                   self._value_col
                                   )

        if obj:
            new_caom.setTo(obj.label)
            new_xml.setText(obj.parent)
            new_value.setText(obj.value)

        self.values_grid.setRowStretch(self._next_value, 0)
        self._next_value += 1
        self.values_grid.setRowStretch(self._next_value, 1)

    def _del_last_value(self):

        self._next_value -= 1
        n_elements = self.values_grid.columnCount()
        for n in range(n_elements):
            x = self.values_grid.itemAtPosition(self._next_value, n).widget()
            x.setParent(None)

    def _fill_default_xml(self):

        sender = self.sender()
        ind = self.values_grid.indexOf(sender)
        pos = self.values_grid.getItemPosition(ind)
        row = pos[0]

        caom_box = self.values_grid.itemAtPosition(row, self._caom_col)
        caom_box = caom_box.widget()
        xml_edit = self.values_grid.itemAtPosition(row, self._xml_col)
        xml_edit = xml_edit.widget()

        xml = caom_box.getXMLParent()
        xml_edit.setText(xml)

    def _read_row_to_hlsp(self, row_num):

        this_caom = self.values_grid.itemAtPosition(row_num, self._caom_col)
        this_xml = self.values_grid.itemAtPosition(row_num, self._xml_col)
        this_val = self.values_grid.itemAtPosition(row_num, self._value_col)

        this_caom = this_caom.widget().currentText()
        this_xml = this_xml.widget().text()
        this_val = this_val.widget().text()

        self.master.hlsp.add_unique_parameter(this_caom, this_xml, this_val)

    def _read_parameters_from_hlsp(self):

        current_parameters = {}

        for parent, params in self.master.hlsp.unique_parameters.items():
            current_parameters[parent] = {}
            for caom, val in params.items():
                current_parameters[parent].update({caom: val})

        return current_parameters

    def clear_values(self):

        while self._next_value > self._first_value:
            self._del_last_value()

    def display_parameters(self):

        self.clear_values()
        for parent, params in self.values_dict.items():
            for caom, val in params.items():
                as_obj = cx.CAOMvalue(caom)
                as_obj.parent = parent
                as_obj.value = val
                self._add_value(obj=as_obj)

    def generate_xml_clicked(self):

        self.master.save_hlsp()
        self.master.hlsp.write_xml_template()

    def refresh_parameters(self):

        self.values_dict = make_standard_parameters(self.master.hlsp)
        current_parameters = self._read_parameters_from_hlsp()
        self.values_dict.update(current_parameters)

        self.display_parameters()

    def update_hlsp_file(self):

        for row in range(self._first_value, self._next_value):
            self._read_row_to_hlsp(row)
