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

# --------------------


def make_standard_parameters(hlsp_obj):
    """
    This function constructs a dictionary with standard keyword/value pairs
    for CAOM XML template files.  Different dictionaries correspond to
    different HLSP standards.

    :param hlsp_obj:  An HLSPFile object is needed for analysis to determine
                      which sets of parameters to add.
    :type hlsp_obj:  HLSPFile
    """

    # Initialize a dictionary for new XML entries under metadataList.
    standard_entries = {"metadataList": {}}

    # Normal additions for all HLSP files.
    normal = {"collection": "HLSP",
              "intent": "SCIENCE",
              "observationID": "FILEROOTSUFFIX",
              }

    # Additions for timeseries collections.
    timeseries = {"algorithm": "timeseries"}

    # Additions for Kepler collections.
    kepler = {"aperture_radius": "4",
              "instrument_name": "Kepler",
              "targetPosition_coordsys": "ICRS",
              }

    # Find the standards being used in hlsp_obj.
    fits_standards = hlsp_obj.member_fits_standards()

    if fits_standards:

        # Analyze any standards found and add corresponding parameters.
        for fit in fits_standards:
            std, inst = fit.split("_")
            if std.lower() == "timeseries":
                normal.update(timeseries)
            if inst.lower() == "kepler" or inst.lower() == "k2":
                normal.update(kepler)

    standard_entries["metadataList"].update(normal)
    return standard_entries

# --------------------


class ValueParametersGUI(QWidget):
    """
    This class constructs a GUI for adding and modifying keyword/value pairs
    to be added to CAOM XML template files for HLSP ingestion.

    ..module::  _add_value
    ..synopsis::  Add a new keyword/value row to the GUI.

    ..module::  _del_last_value
    ..synopsis::  Remove the last keyword/value row from the GUI.

    ..module::  _fill_default_xml
    ..synopsis::  When a user selects a new CAOM keyword in the GUI,
                  automatically select the corresponding XML parent.

    ..module::  _read_row_to_hlsp
    ..synopsis::  Read the current information from a keyword/value row in the
                  GUI and add it to the parent's HLSPFile.

    ..module::  _read_parameters_from_hlsp
    ..synopsis::  Add information from a populated HLSPFile to the GUI.

    ..module::  clear_values
    ..synopsis::  Clear all keyword/value rows from the GUI.

    ..module::  display_parameters
    ..synopsis::  Display the current keyword/value pairs the GUI is aware of.

    ..module::  generate_xml_clicked
    ..synopsis::  Trigger writing the contents of the parent's HLSPFile to a
                  CAOM XML template file.

    ..module::  refresh_parameters
    ..synopsis::  Get standard parameters and any existing contents from the
                  parent's HLSPFile and display these.

    ..module::  update_hlsp_file
    ..synopsis::  Read the current contents of the GUI and add these to the
                  parent's HLSPFile.
    """

    def __init__(self, parent):

        super().__init__(parent)

        # Initialize attributes.  values_dict will keep track of keyword/value
        # pairs in a dictionary.
        self.master = parent
        self.values_dict = {}

        # Create a bold QFont for GUI column headers.
        bold = QFont()
        bold.setBold(True)

        # GUI elements for column header labels.
        caom_label = QLabel("CAOM Keyword:")
        caom_label.setFont(bold)
        xml_label = QLabel("XML Parent:")
        xml_label.setFont(bold)
        value_label = QLabel("Value:")
        value_label.setFont(bold)

        # Define GUI column variables.
        self._caom_col = 0
        self._xml_col = 1
        self._value_col = 2

        # Define GUI row variables.
        head_row = 0
        self._first_value = self._next_value = (head_row + 1)

        # Construct a grid layout to display keyword/value pairs.
        self.values_grid = QGridLayout()
        self.values_grid.addWidget(caom_label, head_row, self._caom_col)
        self.values_grid.addWidget(xml_label, head_row, self._xml_col)
        self.values_grid.addWidget(value_label, head_row, self._value_col)

        # GUI elements for action buttons and button connections.
        refresh_button = gb.GreyButton("Refresh from .hlsp file", 40)
        refresh_button.clicked.connect(self.refresh_parameters)
        add_button = gb.GreyButton("+ add a new parameter", 40)
        add_button.clicked.connect(self._add_value)
        template_button = gb.GreenButton("Generate an XML Template file", 40)
        template_button.clicked.connect(self.generate_xml_clicked)

        # Construct the overall GUI layout.
        self.meta_grid = QGridLayout()
        self.meta_grid.addWidget(refresh_button, 0, 0)
        self.meta_grid.addWidget(add_button, 0, 1)
        self.meta_grid.addLayout(self.values_grid, 1, 0, 1, -1)
        self.meta_grid.addWidget(template_button, 2, 0, 1, -1)

        # Display the GUI.
        self.setLayout(self.meta_grid)
        self.show()

    def _add_value(self, obj=None):
        """
        Add a new keyword/value row to the GUI.

        :param obj:  An optional keyword/value pair to populate the new row.
        :type obj:  CAOMXML.CAOMvalue
        """

        # GUI elements for the new row.
        new_caom = CAOMKeywordBox()
        new_xml = QLineEdit()
        new_value = QLineEdit()

        # Watch for any changes of new_caom.
        new_caom.currentIndexChanged.connect(self._fill_default_xml)

        # Add new row elements to the GUI.
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

        # If a CAOMvalue object was provided, update the GUI elements.
        if obj:
            new_caom.setTo(obj.label)
            new_xml.setText(obj.parent)
            new_value.setText(obj.value)

        # Increment the _next_value pointer and update GUI stretch values.
        self.values_grid.setRowStretch(self._next_value, 0)
        self._next_value += 1
        self.values_grid.setRowStretch(self._next_value, 1)

    def _del_last_value(self):
        """
        Remove the last keyword/value row from the GUI.
        """

        # The _next_value pointer stays ahead of the last row in the GUI, so
        # update this first to access the last row.
        self._next_value -= 1

        # Set all widgets in this row to None parents.
        n_elements = self.values_grid.columnCount()
        for n in range(n_elements):
            x = self.values_grid.itemAtPosition(self._next_value, n).widget()
            x.setParent(None)

    def _fill_default_xml(self):
        """
        When a user selects a new CAOM keyword in the GUI, automatically
        select the corresponding XML parent.
        """

        # Identify the row sending the signal.
        sender = self.sender()
        ind = self.values_grid.indexOf(sender)
        pos = self.values_grid.getItemPosition(ind)
        row = pos[0]

        # Grab the CAOM and XML parent widgets from this row.
        caom_box = self.values_grid.itemAtPosition(row, self._caom_col)
        caom_box = caom_box.widget()
        xml_edit = self.values_grid.itemAtPosition(row, self._xml_col)
        xml_edit = xml_edit.widget()

        # Use the built-in CAOMKeywordBox function to get the corresponding
        # XML parent and update the XML parent widget.
        xml = caom_box.getXMLParent()
        xml_edit.setText(xml)

    def _read_parameters_from_hlsp(self):
        """
        Add information from a populated HLSPFile to the GUI.
        """

        # Copy the parent's HLSPFile unique_parameters dict and return it.
        current_parameters = dict(self.master.hlsp.unique_parameters)
        return current_parameters

    def _read_row_to_hlsp(self, row_num):
        """
        Read the current information from a keyword/value row in the GUI and
        add it to the parent's HLSPFile.

        :param row_num:  The row to read information from.
        :type row_num:  int
        """

        # Identify the widgets in the current row.
        this_caom = self.values_grid.itemAtPosition(row_num, self._caom_col)
        this_xml = self.values_grid.itemAtPosition(row_num, self._xml_col)
        this_val = self.values_grid.itemAtPosition(row_num, self._value_col)

        # Get the current text/settings of these widgets.
        this_caom = this_caom.widget().currentText()
        this_xml = this_xml.widget().text()
        this_val = this_val.widget().text()

        # Add these to the parent's HLSPFile.
        self.master.hlsp.add_unique_parameter(this_caom, this_xml, this_val)

    def clear_values(self):
        """
        Clear all keyword/value rows from the GUI.
        """

        # Remove the last keyword/value row from the GUI until the
        # _next_value pointer points to _first_value.
        while self._next_value > self._first_value:
            self._del_last_value()

    def display_parameters(self):
        """
        Display the current keyword/value pairs the GUI is aware of.
        """

        # Clear any current contents from the GUI.
        self.clear_values()

        # Iterate through values_dict and create a new GUI row from each
        # parameter.
        for parent, params in self.values_dict.items():
            for caom, val in params.items():
                as_obj = cx.CAOMvalue(caom)
                as_obj.parent = parent
                as_obj.value = val
                self._add_value(obj=as_obj)

    def generate_xml_clicked(self):
        """
        Trigger writing the contents of the parent's HLSPFile to a CAOM XML
        template file.
        """

        # Use the parent GUI function to update the HLSPFile.
        self.master.save_hlsp()

        # Use the HLSPFile function to write the contents to XML.
        self.master.hlsp.write_xml_template()

    def refresh_parameters(self):
        """
        Get standard parameters and any existing contents from the parent's
        HLSPFile and display these.
        """

        # Set values_dict to standard parameters, then add any from the
        # HLSPFile.
        # self.values_dict = make_standard_parameters(self.master.hlsp)
        current_parameters = self._read_parameters_from_hlsp()
        self.values_dict.update(current_parameters)

        # Display the new contents.
        self.display_parameters()

        # Update the parent's HLSPFile ingest step tracking.
        self.master.hlsp.toggle_ingest(4, state=True)
        self.master.flag_bar.turn_on(4)

    def update_hlsp_file(self):
        """
        Read the current contents of the GUI and add these to the parent's
        HLSPFile.
        """

        # Iterate through all present GUI rows and add the contents to the
        # HLSPFile.
        for row in range(self._first_value, self._next_value):
            self._read_row_to_hlsp(row)
