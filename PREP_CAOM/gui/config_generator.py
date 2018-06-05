"""
..module:: crawl_dictionary
    :synopsis:  This module is designed to add a given parameter to a provided
    dictionary under a designated parent.  It searches for the parent
    recursively in order to examine all possible levels of nested dictionaries.
    If the parent is found, the parameter is added to the dictionary.  The
    entire dictionary is returned, along with a boolean flag to indicate
    whether or not the insertion was successful.

..class:: ConfigGenerator
    :synopsis:  This class defines a PyQt widget that uses multiple methods to
    collect user input in order to generate a .yaml config file needed by
    ../hlsp_to_xml.py.  This will help to ensure that these config files are
    properly formatted and include the necessary information.  This form
    includes functionality to add extra rows for unique parameter definitions,
    load an existing .yaml file into the form, reset all changes made to the
    form, save all inputs to a .yaml config file, or save a .yaml file and
    immediately launch ../hlsp_to_xml.py with said file.
"""

import csv
import os
import sys
import yaml
from hlsp_to_xml import hlsp_to_xml

import lib.GUIbuttons as gb
import lib.HeaderKeyword as hk
from lib.MyError import MyError

from util.read_yaml import read_yaml

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

HEADER_KEYWORDS = "resources/hlsp_keywords.csv"

#--------------------

def crawl_dictionary(dictionary, parent, parameter, inserted=False):
    """ Recursively look for a given parent within a potential dictionary of
    dictionaries.  If the parent is found, insert the new parameter and update
    the 'inserted' flag.  Return both the updated dictionary and inserted flag.

    :param dictionary:  A dict object containing CAOM parameters.  Nested
    dictionaries are possible in this object.
    :type dictionary:  dict

    :param parent:  The parent to search dictionary keys for.  May not be
    currently present.
    :type parent:  str

    :param parameter:  parameter is a single-key single-value dictionary, to be
    inserted to the existing dictionary under the parent key.
    :type parameter:  dict

    :param inserted:  A flag to keep track of whether or not parent has been
    found and the parameter inserted.
    :type inserted:  bool
    """

    # Assign current dictionary items to tuples
    current_keys = tuple(dictionary.keys())
    current_values = tuple(dictionary.values())

    # If the requested parent already exists, either assign it the parameter
    # value if it is empty or update the current value.  Set the inserted flag.
    if parent in current_keys:
        if dictionary[parent] == "":
            dictionary[parent] = parameter
        else:
            dictionary[parent].update(parameter)
        inserted = True

    # If the requested parent cannot be found, recursively call
    # crawl_dictionary on any subdictionaries found within the current one.
    else:
        for v in current_values:
            ind = current_values.index(v)
            if isinstance(v, dict):
                results = crawl_dictionary(v, parent, parameter, inserted)
                sub_dictionary = results[0]
                inserted = results[1]
                dictionary[current_keys[ind]] = sub_dictionary

    # Return both the dictionary and the inserted flag.
    return (dictionary, inserted)

#--------------------

class HeaderTypeBox(QComboBox):
    """ Create a QComboBox populated with valid header type choices.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.header_types = ["STANDARD", "HST", "KEPLER"]
        for type_ in self.header_types:
            self.addItem(type_)

    def setTo(self, target):
        if target.upper() in self.header_types:
            n = self.findText(target.upper())
            self.setCurrentIndex(n)
        else:
            self.setCurrentIndex(0)

#--------------------

class DataTypeBox(QComboBox):
    """ Create a QComboBox populated with valid CAOM dataProductType choices.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.data_types = ["", "IMAGE", "SPECTRUM", "TIMESERIES", "VISIBILITY",
                           "EVENTLIST", "CUBE", "CATALOG", "MEASUREMENTS"
                          ]
        for type_ in self.data_types:
            self.addItem(type_)

    def setTo(self, target):
        if target.upper() in self.data_types:
            n = self.findText(target.upper())
            self.setCurrentIndex(n)
        else:
            self.setCurrentIndex(0)

#--------------------

class CAOMKeywordBox(QComboBox):
    """ Create a QComboBox populated with valid CAOM parameter choices.
    Distinguish between keywords already modified by code and those not
    currently in use.  Assign each to a default XML parent.
    """

    def __init__(self):
        super().__init__()
        self.setEditable(True)

        # Set up the dictionaries
        self.inuse = {"algorithm": "metadataList",
                      "aperture_radius": "metadataList",
                      "collection": "metadataList",
                      "instrument_keywords": "metadataList",
                      "instrument_name": "metadataList",
                      "intent": "metadataList",
                      "name": "provenance",
                      "observationID": "metadataList",
                      "project": "provenance",
                      "targetPosition_coordinates_cval1": "metadataList",
                      "targetPosition_coordinates_cval2": "metadataList",
                      "targetPosition_coordsys": "metadataList",
                      "targetPosition_equinox": "metadataList",
                      "target_name": "metadataList",
                      "telescope_name": "metadataList",
                      "type": "metadataList",
                      "version": "provenance"
                     }
        self.unused = {"dataRelease": "provenance",
                       "lastExecuted": "provenance",
                       "metaRelease": "metadataList",
                       "producer": "provenance",
                       "proposal_id": "provenance",
                       "proposal_pi": "provenance",
                       "proposal_title": "provenance",
                       "reference": "provenance",
                       "runID": "metadataList",
                       "sequenceNumber": "metadataList",
                       "target_keywords": "metadataList",
                       "target_moving": "metadataList",
                       "target_type": "metadataList"
                      }

        # Create a merged dictionary
        self.allvalues = dict(self.inuse)
        self.allvalues.update(self.unused)

        # Use a QFont object to distinguish category seperators
        font = QFont()
        font.setBold(True)

        # Put unused parameters at the top of the list
        self.addItem("")
        self.addItem("Unused Keywords")
        unused_parent = self.model().item(1)
        unused_parent.setSelectable(False)
        unused_parent.setFont(font)
        for c in sorted(self.unused.keys()):
            self.addItem(c)

        # Add a separator, followed by parameters already in use
        self.addItem("---------------")
        self.addItem("Keywords In Use")
        divider = self.model().item(self.count() - 2)
        divider.setSelectable(False)
        inuse_parent = self.model().item(self.count() - 1)
        inuse_parent.setSelectable(False)
        inuse_parent.setFont(font)
        for d in sorted(self.inuse.keys()):
            self.addItem(d)

    def setTo(self, target):
        """ Set the combo box to a certain index given a CAOM keyword.
        """

        if target in self.allvalues:
            n = self.findText(target)
            self.setCurrentIndex(n)
        else:
            self.setCurrentIndex(0)

    def getXMLParent(self, keyword):
        """ Retrieve the XML parent value for a given CAOM keyword from the
        dictionary.
        """

        if keyword in self.allvalues.keys():
            return self.allvalues[keyword]
        else:
            return None

#--------------------

class ConfigGenerator(QWidget):
    """ This class builds a pyqt GUI for generating a properly-formatted YAML
    config file to feed into the template XML generator.
    """

    def __init__(self):
        super().__init__()
        self.file_types = None
        self.initUI()

    def initUI(self):
        """ Create a GUI with input fields for multiple parameters, which will
        be aggregated into a .yaml config file.
        """

        # Create some formatting items for use throughout.
        firstcol = 100
        space = QSpacerItem(50, 1)
        self.keywords = hk.read_header_keywords_table(HEADER_KEYWORDS)

        # Create a section for input of filepath variables.  Includes lineedit
        # objects and buttons to launch file dialogs if the desired paths are
        # local.
        filepath_label = QLabel("Filepaths:", self)
        data_dir_label = QLabel("HLSP Data: ", filepath_label)
        data_dir_label.setAlignment(Qt.AlignRight)
        data_dir_label.setToolTip(("Enter the location of the HLSP data files "
                                   "to scan."))
        self.data_dir_edit = QLineEdit(data_dir_label)
        output_dir_label = QLabel("Output XML File: ", filepath_label)
        output_dir_label.setAlignment(Qt.AlignRight)
        output_dir_label.setToolTip(("Provide a file path and name for the XML"
                                     " result file."))
        self.output_dir_edit = QLineEdit(output_dir_label)
        browse_data_dir = QPushButton()
        browse_style = browse_data_dir.style()
        icon = browse_style.standardIcon(QStyle.SP_DirIcon)
        browse_data_dir.setIcon(icon)
        browse_data_dir.setIconSize(QSize(14,14))
        browse_data_dir.setMaximumWidth(26)
        browse_data_dir.setMaximumHeight(22)
        browse_output_dir = QPushButton()
        browse_output_dir.setIcon(icon)
        browse_output_dir.setIconSize(QSize(14,14))
        browse_output_dir.setMaximumWidth(26)
        browse_output_dir.setMaximumHeight(22)
        self.filepaths_grid = QGridLayout()
        self.filepaths_grid.addWidget(data_dir_label, 0, 0)
        self.filepaths_grid.addWidget(self.data_dir_edit, 0, 1)
        self.filepaths_grid.addWidget(browse_data_dir, 0, 2)
        self.filepaths_grid.addWidget(output_dir_label, 1, 0)
        self.filepaths_grid.addWidget(self.output_dir_edit, 1, 1)
        self.filepaths_grid.addWidget(browse_output_dir, 1, 2)

        # Set the boolean overwrite parameter with on/off radio button objects.
        overwrite_label = QLabel("Overwrite: ", self)
        overwrite_label.setMinimumWidth(firstcol)
        overwrite_label.setToolTip(("Allow hlsp_to_xml.py to overwrite an "
                                    "existing XML file."))
        self.overwrite_on = QRadioButton("On", overwrite_label)
        self.overwrite_on.setChecked(True)
        self.overwrite_off = QRadioButton("Off", overwrite_label)
        self.overwrite_grid = QGridLayout()
        self.overwrite_grid.addItem(space, 0, 0)
        self.overwrite_grid.addWidget(overwrite_label, 0, 1)
        self.overwrite_grid.addWidget(self.overwrite_on, 0, 2)
        self.overwrite_grid.addWidget(self.overwrite_off, 0, 3)

        # Set the type of .fits headers with a modified QComboBox object.
        headertype_label = QLabel("Header Type: ", self)
        headertype_label.setMinimumWidth(firstcol)
        headertype_label.setToolTip(("Select the FITS header type this HLSP "
                                     "uses."))
        self.headertype_box = HeaderTypeBox(headertype_label)
        self.headertype_box.setMinimumWidth(175)
        self.headertype_grid = QGridLayout()
        self.headertype_grid.addItem(space, 0, 0)
        self.headertype_grid.addWidget(headertype_label, 0, 1)
        self.headertype_grid.addWidget(self.headertype_box, 0, 2)

        # Select the most appropriate data type to apply to the observation
        # using a modified QComboBox.
        datatype_label = QLabel("Data Type: ", self)
        datatype_label.setMinimumWidth(firstcol)
        datatype_label.setToolTip(("Add special CAOM parameters for various "
                                   "data types."))
        self.datatype_box = DataTypeBox(datatype_label)
        self.datatype_box.setMinimumWidth(175)
        self.datatype_grid = QGridLayout()
        self.datatype_grid.addItem(space, 0, 0, -1, 1)
        self.datatype_grid.addWidget(datatype_label, 0, 1)
        self.datatype_grid.addWidget(self.datatype_box, 0, 2)

        # Create a layout for the HLSP-Unique Parameters title and new entry
        # button.
        uniques_label = QLabel("HLSP-Unique Parameters: ", self)
        uniques_label.setToolTip(("Define additional CAOM parameters to "
                                  "insert that are not defined in the FITS "
                                  "headers."))
        uniques_space = QSpacerItem(100, 1)
        add_parameter = gb.GreyButton("+ add a new parameter", 20)
        add_parameter.setMinimumWidth(125)
        add_parameter.setMaximumWidth(200)
        self.uniques_title_grid = QGridLayout()
        self.uniques_title_grid.addWidget(uniques_label, 0, 0)
        self.uniques_title_grid.addItem(uniques_space, 0, 1)
        self.uniques_title_grid.addWidget(add_parameter, 0, 2)

        # Create custom unique parameters to write into the yaml file.  This
        # list is expandable.  Custom parents can be defined in addition to
        # metadataList and provenance.
        parent_label = QLabel("XML Parent:", uniques_label)
        parent_label.setAlignment(Qt.AlignHCenter)
        caom_label = QLabel("CAOM Keyword:", uniques_label)
        caom_label.setAlignment(Qt.AlignHCenter)
        value_label = QLabel("Value:", uniques_label)
        value_label.setAlignment(Qt.AlignHCenter)
        parent_box = QComboBox(parent_label, editable=True)
        self.xml_parents = ["", "metadataList", "provenance"]
        for p in self.xml_parents:
            parent_box.addItem(p)
        caom_box = CAOMKeywordBox()
        value_edit = QLineEdit(value_label)
        self.uniques_grid = QGridLayout()
        self.uniques_grid.addWidget(caom_label, 0, 0)
        self.uniques_grid.addWidget(parent_label, 0, 1)
        self.uniques_grid.addWidget(value_label, 0, 2)
        self.uniques_grid.addWidget(caom_box, 1, 0)
        self.uniques_grid.addWidget(parent_box, 1, 1)
        self.uniques_grid.addWidget(value_edit, 1, 2)
        self.firstrow_uniques = 1
        self.nextrow_uniques = 2
        self.uniques_grid.setRowStretch(self.nextrow_uniques, 1)
        self.uniques_grid.setColumnStretch(0, 0)
        self.uniques_grid.setColumnStretch(1, 1)
        self.uniques_grid.setColumnStretch(2, 1)

        # Create a layout for the Update Header Defaults title and new entry
        # button.
        headerdefault_label = QLabel("Update Header Defaults: ", self)
        headerdefault_label.setToolTip(("Entries here will update default "
                                        "values for .fits headers if they "
                                        "exist or create new ones if they "
                                        "don't."))
        headerdefault_space = QSpacerItem(300, 1)
        add_headerdefault = gb.GreyButton("+ add a new keyword", 20)
        add_headerdefault.setMaximumWidth(200)
        self.headerdefault_title_grid = QGridLayout()
        self.headerdefault_title_grid.addWidget(headerdefault_label, 0, 0)
        self.headerdefault_title_grid.addItem(headerdefault_space, 0, 1)
        self.headerdefault_title_grid.addWidget(add_headerdefault, 0, 2)


        # Adjust .fits header keyword default values or add new header keywords
        # along with the necessary parameters to add to the template file.
        # This is an expandable list with fields that will automatically
        # populate based on a user's keyword selection.
        keyword_label = QLabel("FITS Keyword:", headerdefault_label)
        keyword_label.setAlignment(Qt.AlignHCenter)
        headcaom_label = QLabel("CAOM Keyword:", headerdefault_label)
        headcaom_label.setAlignment(Qt.AlignHCenter)
        xmlparent_label = QLabel("XML Parent:", headerdefault_label)
        xmlparent_label.setAlignment(Qt.AlignHCenter)
        extension_label = QLabel("Extension:", headerdefault_label)
        extension_label.setAlignment(Qt.AlignHCenter)
        default_label = QLabel("Default Value:", headerdefault_label)
        default_label.setAlignment(Qt.AlignHCenter)
        self.keyword_box = QComboBox(keyword_label, editable=True)
        self.keyword_box.addItem("")
        initial_header_type = self.headertype_box.header_types[0].lower()
        self.header_keywords = self.keywords[initial_header_type]
        for k in self.header_keywords:
            self.keyword_box.addItem(k.keyword)
        headercaom_box = CAOMKeywordBox()
        xmlparent_box = QComboBox(xmlparent_label, editable=True)
        for p in self.xml_parents:
            xmlparent_box.addItem(p)
        extension_edit = QLineEdit(extension_label)
        default_edit = QLineEdit(default_label)
        self.headerdefault_grid = QGridLayout()
        self.headerdefault_grid.addWidget(keyword_label, 0, 0)
        self.headerdefault_grid.addWidget(headcaom_label, 0, 1)
        self.headerdefault_grid.addWidget(xmlparent_label, 0, 2)
        self.headerdefault_grid.addWidget(extension_label, 0, 3)
        self.headerdefault_grid.addWidget(default_label, 0, 4)
        self.headerdefault_grid.addWidget(self.keyword_box, 1, 0)
        self.headerdefault_grid.addWidget(headercaom_box, 1, 1)
        self.headerdefault_grid.addWidget(xmlparent_box, 1, 2)
        self.headerdefault_grid.addWidget(extension_edit, 1, 3)
        self.headerdefault_grid.addWidget(default_edit, 1, 4)
        self.firstrow_headers = 1
        self.nextrow_headers = 2
        self.headerdefault_grid.setRowStretch(self.nextrow_headers, 1)
        self.headerdefault_grid.setColumnStretch(0, 0)
        self.headerdefault_grid.setColumnStretch(1, 0)
        self.headerdefault_grid.setColumnStretch(2, 0)
        self.headerdefault_grid.setColumnStretch(3, 1)
        self.headerdefault_grid.setColumnStretch(4, 1)

        # Create a grid layout and add all the layouts and remaining widgets.
        self.meta_grid = QGridLayout()
        self.meta_grid.setColumnStretch(1, 1)
        self.meta_grid.setColumnStretch(2, 1)
        self.meta_grid.setColumnStretch(3, 0)
        self.meta_grid.setColumnStretch(4, 0)
        self.meta_grid.setColumnStretch(5, 0)
        self.meta_grid.setRowStretch(9, 0)
        self.meta_grid.setRowStretch(10, 1)
        self.meta_grid.addWidget(filepath_label, 0, 0)
        self.meta_grid.addLayout(self.overwrite_grid, 0, 4, 1, 2)
        self.meta_grid.addLayout(self.filepaths_grid, 1, 0, 2, 4)
        self.meta_grid.addLayout(self.headertype_grid, 1, 4)
        self.meta_grid.addLayout(self.datatype_grid, 2, 4, 1, 1)
        self.meta_grid.addLayout(self.uniques_title_grid, 3, 0, 1, -1)
        self.meta_grid.addLayout(self.uniques_grid, 4, 0, 4, -1)
        self.meta_grid.addLayout(self.headerdefault_title_grid, 8, 0, 1, -1)
        self.meta_grid.addLayout(self.headerdefault_grid, 9, 0, 4, -1)

        # Set the window layout and show it.
        self.setLayout(self.meta_grid)
        self.show()

        # Add button actions.
        browse_data_dir.clicked.connect(self.hlspClicked)
        browse_output_dir.clicked.connect(self.outputClicked)
        add_parameter.clicked.connect(self.addParameterClicked)
        add_headerdefault.clicked.connect(self.addKeywordClicked)
        caom_box.currentIndexChanged.connect(self.caomKeywordSelected)
        headercaom_box.currentIndexChanged.connect(self.caomKeywordSelected)
        self.headertype_box.currentIndexChanged.connect(self.headerTypeChanged)
        self.keyword_box.currentIndexChanged.connect(self.fitsKeywordSelected)

    def hlspClicked(self):
        """ Launch a file dialog to select a directory containing HLSP data.
        """

        navigate = QFileDialog.getExistingDirectory(self,
                                                    "Select HLSP Directory",
                                                    ".")
        self.data_dir_edit.clear()
        self.data_dir_edit.insert(navigate)


    def outputClicked(self):
        """ Launch a file dialog to define the XML output file name & path.
        """

        navigate = QFileDialog.getSaveFileName(self,
                                               "Save Output XML File",
                                               ".")
        path = navigate[0]
        self.output_dir_edit.clear()
        self.output_dir_edit.insert(path)

    def headerTypeChanged(self):
        """ When the header_type is changed, set the header_keywords to the
        new list.  Re-populate any existing empty keyword menus.  Skip any
        rows that have already been populated.
        """

        # Get the new header type and reset the header_keywords list
        # accordingly.
        new_type = self.headertype_box.currentText().lower()
        self.header_keywords = self.keywords[new_type]

        # Iterate through all rows in the headerdefault_grid.  Only update the
        # list choices for any rows that are totally empty.
        for row in range(self.firstrow_headers, self.nextrow_headers):
            key_widg = self.headerdefault_grid.itemAtPosition(row, 0).widget()
            caom_widg = self.headerdefault_grid.itemAtPosition(row, 1).widget()
            xml_widg = self.headerdefault_grid.itemAtPosition(row, 2).widget()
            ext_widg = self.headerdefault_grid.itemAtPosition(row, 3).widget()
            def_widg = self.headerdefault_grid.itemAtPosition(row, 4).widget()
            caom_text = str(caom_widg.currentText())
            xml_text = str(xml_widg.currentText())
            ext_text = str(ext_widg.text())
            def_text = str(def_widg.text())
            if (caom_text == ""
                and xml_text == ""
                and ext_text == ""
                and def_text == ""):
                key_widg.clear()
                key_widg.addItem("")
                for key in self.header_keywords:
                    key_widg.addItem(key.keyword)

    def caomKeywordSelected(self):
        """ In the HLSP-Unique Parameters section, we want to update the XML
        Parent value when a CAOM Keyword is selected from the CAOMKeywordBox.
        """

        # Determine which section is sending the signal and get the position
        # of the signal sender.
        sender = self.sender()
        uniques_index = self.uniques_grid.indexOf(sender)
        headers_index = self.headerdefault_grid.indexOf(sender)
        if uniques_index >= 0:
            section = self.uniques_grid
            pos = section.getItemPosition(uniques_index)
        elif headers_index >= 0:
            section = self.headerdefault_grid
            pos = section.getItemPosition(headers_index)
        else:
            return

        row = pos[0]
        col = pos[1]

        # Get the widgets at this position.
        caom_key_box = section.itemAtPosition(row, col).widget()
        xml_parent_box = section.itemAtPosition(row, col+1).widget()

        # Get the new CAOM keyword and the associated XML Parent value.
        new_caom_selected = caom_key_box.currentText()
        new_xml_parent = caom_key_box.getXMLParent(new_caom_selected)

        # If getXMLParent finds a match, look for this value in the
        # contents of xml_parent_box.
        if new_xml_parent:
            n = xml_parent_box.findText(new_xml_parent)

            # If the chosen XML parent already exists, set the QComboBox to
            # that index.  Otherwise, insert it as new text.
            if n >= 0:
                xml_parent_box.setCurrentIndex(n)
            else:
                xml_parent_box.setCurrentText(new_xml_parent)

        # If no corresponding XML parent is found, set it to "".
        else:
            xml_parent_box.setCurrentIndex(0)

    def addParameterClicked(self):
        """ Add a new unique parameter entry row into the self.nextrow_uniques
        position, then update self.nextrow_uniques.
        """

        # Make a new 'Parent:' combo box and populate it with self.xml_parents.
        new_parent = QComboBox(editable=True)
        for p in self.xml_parents:
            new_parent.addItem(p)

        # Make new line edits for 'CAOM Keyword:' and 'Value:'.
        new_caom = CAOMKeywordBox()
        new_value = QLineEdit()

        # Add the new widgets to the uniques_grid layout.
        self.uniques_grid.addWidget(new_caom, self.nextrow_uniques, 0)
        self.uniques_grid.addWidget(new_parent, self.nextrow_uniques, 1)
        self.uniques_grid.addWidget(new_value, self.nextrow_uniques, 2)
        self.uniques_grid.setRowStretch(self.nextrow_uniques, 0)
        self.uniques_grid.setRowStretch(self.nextrow_uniques+1, 1)

        # Update self.nextrow_uniques.
        self.nextrow_uniques += 1

        # Connect the new CAOMKeywordBox object to the module that will
        # update the XML Parent depending on the value selected.
        new_caom.currentIndexChanged.connect(self.caomKeywordSelected)

    def fitsKeywordSelected(self):
        """ When a user chooses a header keyword in a headerdefault_grid row,
        populate the CAOM Property, XML Parent, Extension, and Default Value
        (if applicaple) fields based on the chosen keyword.
        """

        # Get the position of the signal sender.
        sender = self.sender()
        ind = self.headerdefault_grid.indexOf(sender)
        pos = self.headerdefault_grid.getItemPosition(ind)
        row = pos[0]

        # Get the sender widget and the new keyword chosen.
        this_keyword = self.headerdefault_grid.itemAtPosition(row, 0).widget()
        new_keyword = this_keyword.currentText()

        # The user may have entered a new header keyword, in which case we
        # simply return without populating anything.
        try:
            new_obj = self.header_keywords.find(new_keyword)
        except KeyError:
            return

        # Ignore any empty string entries.
        if new_obj is None:
            return

        # If the header already exists, populate the remaining row fields with
        # data from the HeaderKeyword object.  The CAOMKeywordBox change will
        # update the XML parent selection automatically, so skip it here.
        this_caom = self.headerdefault_grid.itemAtPosition(row, 1).widget()
        this_caom.setTo(new_obj.caom)
        this_ext = self.headerdefault_grid.itemAtPosition(row, 3).widget()
        this_ext.setText(new_obj.headerName)

    def addKeywordClicked(self):
        """ Create a new row in the headerdefault_grid table for modifying
        .fits header keyword properties.
        """

        # Make a new keyword combo box and populate it with the current
        # header_keywords list.
        new_keyword_box = QComboBox(editable=True)
        new_keyword_box.addItem("")
        for header_key in self.header_keywords:
            new_keyword_box.addItem(header_key.keyword)

        # Connect the new keyword combo box to the fitsKeywordSelected action.
        new_keyword_box.currentIndexChanged.connect(self.fitsKeywordSelected)

        # Make a new 'Parent:' combo box and populate it with self.xml_parents.
        new_xmlparent = QComboBox(editable=True)
        for p in self.xml_parents:
            new_xmlparent.addItem(p)

        # Make new line edits for 'CAOM Property:', 'Extension:', and "Default
        # value".
        new_headcaom = CAOMKeywordBox()
        new_headcaom.currentIndexChanged.connect(self.caomKeywordSelected)

        new_extension = QLineEdit()
        new_default = QLineEdit()

        # Add the new widgets to the headerdefault_grid layout.
        self.headerdefault_grid.addWidget(new_keyword_box,
                                          self.nextrow_headers, 0)
        self.headerdefault_grid.addWidget(new_headcaom,
                                          self.nextrow_headers, 1)
        self.headerdefault_grid.addWidget(new_xmlparent,
                                          self.nextrow_headers, 2)
        self.headerdefault_grid.addWidget(new_extension,
                                          self.nextrow_headers, 3)
        self.headerdefault_grid.addWidget(new_default,
                                          self.nextrow_headers, 4)
        self.headerdefault_grid.setRowStretch(self.nextrow_headers, 0)
        self.headerdefault_grid.setRowStretch(self.nextrow_headers+1, 1)

        # Update self.nextrow_headers.
        self.nextrow_headers += 1

    def clearConfigPaths(self):
        self.data_dir_edit.clear()
        self.output_dir_edit.clear()

    def loadConfigPaths(self, paths_dict):
        self.clearConfigPaths()
        self.data_dir_edit.insert(paths_dict["InputDir"])
        self.output_dir_edit.insert(paths_dict["Output"])

    def setProductType(self, data_product_type):
        self.datatype_box.setTo(data_product_type)

    def setHeaderStandard(self, header_type):
        self.headertype_box.setTo(header_type)

    def loadDictionaries(self, uniques):
        """ Recursively handles loading multi-level dictionaries to the unique
        parameters table.

        :param uniques:  A dictionary containing CAOM parameters.  May contain
        nested dictionaries.
        :type uniques:  dict
        """

        if uniques is None:
            return

        parents = uniques.keys()
        for p in parents:
            sub_dictionary = uniques[p]
            copy_dictionary = dict(sub_dictionary)

            # Look at the first row to see if you're loading into FIRST_ENTRY
            # or NEXT_ENTRY.
            first_parent = self.uniques_grid.itemAtPosition(
                                                    self.firstrow_uniques,0)
            first_widget = first_parent.widget()
            for parameter in sub_dictionary.keys():
                value = sub_dictionary[parameter]

                # If the first widget text is empty, start loading there.
                # Otherwise, load to the self.nextrow_uniques position and
                # create a new set of widgets using addParameterClicked().
                if first_widget.currentText() == "":
                    row = self.firstrow_uniques
                else:
                    row = self.nextrow_uniques
                    self.addParameterClicked()

                # Get the Parent combo box for the current row.
                caom_box = self.uniques_grid.itemAtPosition(row,0).widget()
                parent_box = self.uniques_grid.itemAtPosition(row,1).widget()
                value_box = self.uniques_grid.itemAtPosition(row,2).widget()

                # If the desired parent is already an option, set to that.
                # Otherwise add it as a new option in the combo box.
                if p in self.xml_parents:
                    parent_index = self.xml_parents.index(p)
                    parent_box.setCurrentIndex(parent_index)
                else:
                    parent_box.addItem(p)
                    parent_box.setCurrentIndex(parent_box.findText(p))
                    self.xml_parents.append(p)

                # Fill in the CAOM line edit box.
                caom_box.setTo(parameter)

                # If the next level is still a dictionary, repeat this process.
                # Otherwise, fill in the Value line edit box.
                if isinstance(sub_dictionary[parameter], dict):
                    self.loadDictionaries(copy_dictionary)
                else:
                    value_box.insert(sub_dictionary[parameter])
                    del copy_dictionary[parameter]

    def loadFromYAML(self, filename):
        """ Load configuration parameters to our ConfigGenerator form using a
        YAML-formatted file.

        :param filename:  The location of the YAML-formatted config file.
        :type filename:  str
        """

        # Read the YAML entries into a dictionary.  select_files will also be
        # opening the config file, so kill the redundant output.
        yamlfile = read_yaml(filename, output=False)

        # Clear any existing form values before loading the new data.
        self.resetClicked()

        # Get the 'filepaths' data out of the dictionary and write it into
        # the appropriate lineedits
        try:
            filepaths = yamlfile["filepaths"]
            self.data_dir_edit.insert(filepaths["hlsppath"])
            self.output_dir_edit.insert(filepaths["output"])
        except KeyError:
            msg = "'filepaths' either missing or not formatted in config file"
            raise MyError(msg)

        # Get the 'overwrite' information out of the dictionary and set the
        # radio button
        try:
            if filepaths["overwrite"]:
                self.overwrite_on.setChecked(True)
            else:
                self.overwrite_off.setChecked(True)
        except KeyError:
            msg = "'overwrite' not provided in config file"
            raise MyError(msg)

        # Get the 'header_type' data out of the dictionary and set the
        # QComboBox.
        try:
            header_type = yamlfile["header_type"].capitalize()
            header_index = self.headertype_box.header_types.index(header_type)
            self.headertype_box.setCurrentIndex(header_index)
        except KeyError:
            msg = "'header_type' not provided in config file"
            raise MyError(msg)

        # Get the 'data_type' data out of the dictionary and set the
        # QComboBox.
        try:
            data_type = yamlfile["data_type"].upper()
            dataType_index = self.datatype_box.data_types.index(data_type)
            self.datatype_box.setCurrentIndex(dataType_index)
        except KeyError:
            msg = "'data_type' not provided in config file"
            raise MyError(msg)

        # Get the 'unique_parameters' data out of the dictionary using the
        # loadDictionaries module and create new rows as needed.  Error
        # handling just does a pass since not all configs will have extra
        # parameters.
        try:
            uniques = yamlfile["unique_parameters"]
            self.loadDictionaries(uniques)
        except KeyError:
            pass

        # Get the 'keyword_updates' data out of the dictionary. Error handling
        # just returns since this is the last function and not all configs
        # will set keyword values.
        try:
            keyword_updates = yamlfile["keyword_updates"]
        except KeyError:
            return

        # Load the 'keyword_updates' data into the form and create new rows
        # if necessary.
        for key in sorted(keyword_updates.keys()):
            values = keyword_updates[key]

            # If nextrow_headers has not been moved, load into
            # firstrow_headers.  Otherwise, trigger an addKeywordClicked event
            # and load into nextrow_headers.
            if self.nextrow_headers == self.firstrow_headers + 1:
                row = self.firstrow_headers
            else:
                row = self.nextrow_headers
                self.addKeywordClicked()
            load_key = self.headerdefault_grid.itemAtPosition(row, 0).widget()
            load_caom = self.headerdefault_grid.itemAtPosition(row, 1).widget()
            load_xml = self.headerdefault_grid.itemAtPosition(row, 2).widget()
            load_ext = self.headerdefault_grid.itemAtPosition(row, 3).widget()
            load_def = self.headerdefault_grid.itemAtPosition(row, 4).widget()

            # Get the lists of available keyword and XML parent values that
            # currently populate the two QComboBox items.
            available_keys = [load_key.itemText(x)
                                            for x in range(load_key.count())]
            available_xml = [load_xml.itemText(y)
                                            for y in range(load_xml.count())]

            # If the keyword and XML parent values are already available,
            # select them in the appropriate box.  Otherwise, enter them as
            # new values.
            if key in available_keys:
                load_key.setCurrentIndex(available_keys.index(key))
            else:
                load_key.setCurrentText(key)
            load_caom.setTo(values["caom"])
            if values["section"] in available_xml:
                load_xml.setCurrentIndex(
                                        available_xml.index(values["section"]))
            else:
                load_xml.setCurrentText(values["section"])

            # Add the headerName and headerDefaultValue text to the lineedit
            # objects.
            load_ext.setText(values["headerName"])
            load_def.setText(values["headerDefaultValue"])

    def loadParamFile(self, filename):
        """ Load the available information from a .param file created by the
        previous metadata-checking steps of HLSP ingestion.  This will not
        completely fill out the .config file form.

        :param filename:  The filename for the YAML-formatted file to read
                          information from.
        :type filename:  str
        """

        # Read the YAML entries into a dictionary.  select_files will also be
        # opening the config file, so kill the redundant output.
        yamlfile = read_yaml(filename, output=False)

        # Clear any existing form values before loading the new data.
        self.resetClicked()

        # Get the 'filepaths' data out of the dictionary and write it into
        # the appropriate lineedits
        try:
            datadir = yamlfile["InputDir"]
        except KeyError:
            msg = "'InputDir' either missing or not formatted in .param file"
            raise MyError(msg)
        else:
            self.data_dir_edit.insert(datadir)

        # Identify the single .fits entry defined in the .param file, if
        # present.
        try:
            fits = yamlfile["fits"]
        except KeyError:
            msg = "No fits parameters found in .param file"
            raise MyError(msg)
        else:
            if len(fits) > 1:
                msg = "More than one .fits product found in .param file"
                raise MyError(msg)
            else:
                fits = fits[0]

        # If the single .fits entry is present, get the standard that was
        # used for metadata checking.
        try:
            new_head_type = fits["FileParams"]["Standard"].title()
        except KeyError:
            msg = "Could not find a .fits standard in .param file"
            raise MyError(msg)
        else:
            if new_head_type in self.headertype_box.header_types:
                n = self.headertype_box.header_types.index(new_head_type)
                self.headertype_box.setCurrentIndex(n)

        # If the single .fits entry is present, get the ProductType information
        # defined in the .param file.
        try:
            new_data_type = fits["FileParams"]["ProductType"].upper()
        except KeyError:
            msg = "Could not find 'ProductType' parameter in .param file"
            raise MyError(msg)
        else:
            if new_data_type in self.datatype_box.data_types:
                n = self.datatype_box.data_types.index(new_data_type)
                self.datatype_box.setCurrentIndex(n)
            else:
                self.datatype_box.setCurrentIndex(0)

    def resetClicked(self):
        """ Clear any changes to the form.
        """

        #Empty the immediately-available elements.
        self.clearConfigPaths()
        self.overwrite_on.setChecked(True)
        self.headertype_box.setCurrentIndex(0)
        self.datatype_box.setCurrentIndex(0)
        p_one = self.uniques_grid.itemAtPosition(self.firstrow_uniques,0)
        p_one.widget().setCurrentIndex(0)
        c_one = self.uniques_grid.itemAtPosition(self.firstrow_uniques,1)
        c_one.widget().setCurrentIndex(0)
        v_one = self.uniques_grid.itemAtPosition(self.firstrow_uniques,2)
        v_one.widget().clear()
        k_one = self.headerdefault_grid.itemAtPosition(self.firstrow_headers,0)
        k_one.widget().setCurrentIndex(0)
        h_one = self.headerdefault_grid.itemAtPosition(self.firstrow_headers,1)
        h_one.widget().setCurrentIndex(0)
        x_one = self.headerdefault_grid.itemAtPosition(self.firstrow_headers,2)
        x_one.widget().setCurrentIndex(0)
        e_one = self.headerdefault_grid.itemAtPosition(self.firstrow_headers,3)
        e_one.widget().clear()
        d_one = self.headerdefault_grid.itemAtPosition(self.firstrow_headers,4)
        d_one.widget().clear()

        # Delete any unique parameter entries beyond the first table row.
        delete_these = range(self.nextrow_uniques - 1,
                             self.firstrow_uniques,
                             -1)
        for a in delete_these:
            test = self.uniques_grid.itemAtPosition(a, 0)
            if test is None:
                continue
            widgets_per_row = 3
            for b in range(widgets_per_row):
                c = self.uniques_grid.itemAtPosition(a, b).widget()
                c.setParent(None)

        # Reset the nextrow_uniques variable.
        self.nextrow_uniques = self.firstrow_uniques + 1

        # Delete any header keyword entries beyond the first row.
        delete_these = range(self.nextrow_headers - 1,
                             self.firstrow_headers,
                             -1)
        for x in delete_these:
            test = self.headerdefault_grid.itemAtPosition(x,0)
            if test is None:
                continue
            widgets_per_row = 5
            for y in range(widgets_per_row):
                z = self.headerdefault_grid.itemAtPosition(x,y).widget()
                z.setParent(None)

        # Reset the nextrow_headers variable.
        self.nextrow_headers = self.firstrow_headers + 1

    def collectInputs(self):
        """ Assemble everything the user has input to the form into a
        dictionary.
        """

        # Initialize dictionaries to populate.
        config = {}
        filepaths = {}

        # Get the HLSP data filepath.  Throw an error if it does not exist.
        hlsppath = self.data_dir_edit.text()
        if hlsppath == "":
            raise MyError("HLSP Data file path is missing!")
        else:
            filepaths["hlsppath"] = hlsppath

        # Get the output filepath from the line edit.  Throw an error if it is
        # empty.  Append with a '.xml' if not already there.  Get the overwrite
        # flag from the checkbox.
        out = self.output_dir_edit.text()
        if out == "":
            raise MyError("Output file path is missing!")
        if not out.endswith(".xml"):
            out = ".".join([out, "xml"])
        filepaths["output"] = out
        filepaths["overwrite"] = self.overwrite_on.isChecked()
        config["filepaths"] = filepaths

        # Grab the selected fits header type.
        config["header_type"] = self.headertype_box.currentText().lower()

        # Get the data type.  Throw an error if none selected.
        dt = self.datatype_box.currentText().lower()
        if dt == "":
            raise MyError("No data type selected!")
        else:
            config["data_type"] = dt

        # Collect all the unique parameters the user has entered.  Start at row
        # self.firstrow_uniques and search through all rows the user may have
        # added.
        uniques = {}
        for row in range(self.firstrow_uniques, self.nextrow_uniques):
            add_caom = self.uniques_grid.itemAtPosition(row, 0)
            add_parent = self.uniques_grid.itemAtPosition(row, 1)
            add_value = self.uniques_grid.itemAtPosition(row, 2)
            unique_parent = unique_caom = unique_value = None

            # Skip totally empty rows, empty values are okay for defining a new
            # parent.
            if add_parent is None and add_caom is None and add_value is None:
                continue
            if add_parent is not None:
                parent_widget = add_parent.widget()
                unique_parent = str(parent_widget.currentText())
            if add_caom is not None:
                caom_widget = add_caom.widget()
                unique_caom = str(caom_widget.currentText())
            if add_value is not None:
                value_widget = add_value.widget()
                unique_value = str(value_widget.text())
            if (unique_parent == ""
                and unique_caom == ""
                and unique_value == ""):
                continue
            elif unique_parent == "":
                unique_parent = "CompositeObservation"
            parameter = {}
            parameter[unique_caom] = unique_value
            insert = crawl_dictionary(uniques, unique_parent, parameter)

            # crawl_dictionary returns a tuple:
            # (updated dictionary, inserted boolean flag)
            new_uniques, inserted = insert

            # If crawl_dictionary did not insert the new parameter, the defined
            # parent is not currently present in the dictionary, so create a
            # new entry.
            if inserted:
                uniques = new_uniques
            else:
                uniques[unique_parent] = parameter

        config["unique_parameters"] = uniques

        # Collect all header keyword entries the user may have provided.
        keywords = {}
        for row in range(self.firstrow_headers, self.nextrow_headers):
            add_key = self.headerdefault_grid.itemAtPosition(row, 0)
            add_caom = self.headerdefault_grid.itemAtPosition(row, 1)
            add_xml = self.headerdefault_grid.itemAtPosition(row, 2)
            add_ext = self.headerdefault_grid.itemAtPosition(row, 3)
            add_def = self.headerdefault_grid.itemAtPosition(row, 4)
            unique_keyword = None
            unique_caom = None
            unique_xmlparent = None
            unique_extension = None
            unique_default = None

            # Skip rows with any missing properties, otherwise load the info
            # into variables.
            if (add_key is None
                or add_caom is None
                or add_xml is None
                or add_ext is None
                or add_def is None):
                continue
            else:
                unique_keyword = str(add_key.widget().currentText())
                unique_caom = str(add_caom.widget().currentText())
                unique_xmlparent = str(add_xml.widget().currentText())
                unique_extension = str(add_ext.widget().text())
                unique_default = str(add_def.widget().text())

            # Skip the row if any of those variables are empty strings.
            # Otherwise, add the information to a dictionary of properties
            # stored under the given header keyword.
            if (unique_keyword == ""
                or unique_caom == ""
                or unique_xmlparent == ""
                or unique_extension == ""
                or unique_default == ""):
                continue
            else:
                new_entries = {}
                new_entries["caom"] = unique_caom
                new_entries["section"] = unique_xmlparent
                new_entries["headerName"] = unique_extension
                new_entries["headerDefaultValue"] = unique_default
                keywords[unique_keyword] = new_entries

        config["keyword_updates"] = keywords

        # Return the config dictionary
        return config

#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = ConfigGenerator()
    sys.exit(app.exec_())
