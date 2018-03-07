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

import copy
import csv
import os
import sys
import yaml
from hlsp_to_xml import hlsp_to_xml

import lib.GUIbuttons as gb
import lib.HeaderKeyword as hk
from lib.MyError import MyError

import util.check_paths as cp
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
    """
    Recursively look for a given parent within a potential dictionary of
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

    current_keys = tuple(dictionary.keys())
    current_values = tuple(dictionary.values())

    if parent in current_keys:
        if dictionary[parent] == "":
            dictionary[parent] = parameter
        else:
            dictionary[parent].update(parameter)
        inserted = True
    else:
        for v in current_values:
            ind = current_values.index(v)
            if isinstance(v, dict):
                results = crawl_dictionary(v, parent, parameter, inserted)
                sub_dictionary = results[0]
                inserted = results[1]
                dictionary[current_keys[ind]] = sub_dictionary

    return (dictionary, inserted)

#--------------------

class HeaderTypeBox(QComboBox):

    def __init__(self, parent):
        super().__init__(parent)
        self.header_types = ["Standard", "Kepler"]
        for _type in self.header_types:
            self.addItem(_type)

#--------------------

class DataTypeBox(QComboBox):

    def __init__(self, parent):
        super().__init__(parent)
        self.data_types = ["", "IMAGE", "SPECTRUM", "TIMESERIES", "VISIBILITY",
                          "EVENTLIST", "CUBE", "CATALOG", "MEASUREMENTS"]
        for _type in self.data_types:
            self.addItem(_type)

#--------------------

class CAOMKeywordBox(QComboBox):

    def __init__(self):
        super().__init__()
        self.setEditable(True)
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
        self.allvalues = self.inuse.copy()
        self.allvalues.update(self.unused)

        font = QFont()
        font.setBold(True)

        self.addItem("")
        self.addItem("Unused Keywords")
        unused_parent = self.model().item(1)
        unused_parent.setSelectable(False)
        unused_parent.setFont(font)

        for c in sorted(self.unused.keys()):
            self.addItem(c)

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
        if target in self.allvalues:
            n = self.findText(target)
            self.setCurrentIndex(n)
        else:
            self.setCurrentIndex(0)

    def getXMLParent(self, keyword):
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

        #Create some formatting items for use throughout.
        firstcol = 100
        space = QSpacerItem(50, 1)
        self.keywords = hk.read_header_keywords_table(HEADER_KEYWORDS)

        #Create a section for input of filepath variables.  Includes lineedit
        #objects and buttons to launch file dialogs if the desired paths are
        #local.
        fp = QLabel("Filepaths:", self)
        data = QLabel("HLSP Data: ", fp)
        data.setAlignment(Qt.AlignRight)
        data.setToolTip("Enter the location of the HLSP data files to scan.")
        self.data_edit = QLineEdit(data)
        out = QLabel("Output XML File: ", fp)
        out.setAlignment(Qt.AlignRight)
        out.setToolTip("Provide a file path and name for the XML result file.")
        self.out_edit = QLineEdit(out)
        browse_hlsp = QPushButton()
        hst = browse_hlsp.style()
        icon = hst.standardIcon(QStyle.SP_DirIcon)
        browse_hlsp.setIcon(icon)
        browse_hlsp.setIconSize(QSize(14,14))
        browse_hlsp.setMaximumWidth(26)
        browse_hlsp.setMaximumHeight(22)
        browse_ext = QPushButton()
        browse_out = QPushButton()
        browse_out.setIcon(icon)
        browse_out.setIconSize(QSize(14,14))
        browse_out.setMaximumWidth(26)
        browse_out.setMaximumHeight(22)
        self.pathsgrid = QGridLayout()
        self.pathsgrid.addWidget(data, 0, 0)
        self.pathsgrid.addWidget(self.data_edit, 0, 1)
        self.pathsgrid.addWidget(browse_hlsp, 0, 2)
        self.pathsgrid.addWidget(out, 1, 0)
        self.pathsgrid.addWidget(self.out_edit, 1, 1)
        self.pathsgrid.addWidget(browse_out, 1, 2)

        #Set the boolean overwrite parameter with on/off radio button objects.
        ow = QLabel("Overwrite: ", self)
        ow.setMinimumWidth(firstcol)
        ow.setToolTip("Allow hlsp_to_xml.py to overwrite an existing XML file.")
        self.ow_on = QRadioButton("On", ow)
        self.ow_on.setChecked(True)
        self.ow_off = QRadioButton("Off", ow)
        self.overwritegrid = QGridLayout()
        self.overwritegrid.addItem(space, 0, 0)
        self.overwritegrid.addWidget(ow, 0, 1)
        self.overwritegrid.addWidget(self.ow_on, 0, 2)
        self.overwritegrid.addWidget(self.ow_off, 0, 3)

        # Set the type of .fits headers with a modified QComboBox object.
        ht = QLabel("Header Type: ", self)
        ht.setMinimumWidth(firstcol)
        ht.setToolTip("Select the FITS header type this HLSP uses.")
        self.header = HeaderTypeBox(ht)
        self.header.setMinimumWidth(175)
        self.headertypesgrid = QGridLayout()
        self.headertypesgrid.addItem(space, 0, 0)
        self.headertypesgrid.addWidget(ht, 0, 1)
        self.headertypesgrid.addWidget(self.header, 0, 2)

        # Select the most appropriate data type to apply to the observation
        # using a modified QComboBox.
        dt = QLabel("Data Type: ", self)
        dt.setMinimumWidth(firstcol)
        dt.setToolTip("Add special CAOM parameters for various data types.")
        self.dt_box = DataTypeBox(dt)
        self.dt_box.setMinimumWidth(175)
        self.datatypesgrid = QGridLayout()
        self.datatypesgrid.addItem(space, 0, 0, -1, 1)
        self.datatypesgrid.addWidget(dt, 0, 1)
        self.datatypesgrid.addWidget(self.dt_box, 0, 2)

        #Create custom unique parameters to write into the yaml file.  This
        #list is expandable.  Custom parents can be defined in addition to
        #metadataList and provenance.
        up = QLabel("HLSP-Unique Parameters: ", self)
        up.setToolTip("Define additional CAOM parameters to insert that are \
        not defined in the FITS headers.")
        add_param = gb.GreyButton("+ add a new parameter", 20)
        add_param.setMinimumWidth(125)
        #add_param.setMaximumWidth(175)
        parent_param = QLabel("XML Parent:", up)
        parent_param.setAlignment(Qt.AlignHCenter)
        caom_param = QLabel("CAOM Keyword:", up)
        caom_param.setAlignment(Qt.AlignHCenter)
        value_param = QLabel("Value:", up)
        value_param.setAlignment(Qt.AlignHCenter)
        parent_edit = QComboBox(parent_param, editable=True)
        self.xml_parents = ["", "metadataList", "provenance"]
        for p in self.xml_parents:
            parent_edit.addItem(p)

        #caom_edit = QLineEdit(caom_param)
        caom_edit = CAOMKeywordBox()

        value_edit = QLineEdit(value_param)
        self.uniquesgrid = QGridLayout()
        self.uniquesgrid.addWidget(up, 0, 0)
        self.uniquesgrid.addWidget(add_param, 0, 2)
        self.uniquesgrid.addWidget(caom_param, 1, 0)
        self.uniquesgrid.addWidget(parent_param, 1, 1)
        self.uniquesgrid.addWidget(value_param, 1, 2)
        self.uniquesgrid.addWidget(caom_edit, 2, 0)
        self.uniquesgrid.addWidget(parent_edit, 2, 1)
        self.uniquesgrid.addWidget(value_edit, 2, 2)
        self.firstrow_uniques = 2
        self.nextrow_uniques = 3
        self.uniquesgrid.setRowStretch(self.nextrow_uniques, 1)
        self.uniquesgrid.setColumnStretch(0, 0)
        self.uniquesgrid.setColumnStretch(1, 1)
        self.uniquesgrid.setColumnStretch(2, 1)

        # Adjust .fits header keyword default values or add new header keywords
        # along with the necessary parameters to add to the template file.
        # This is an expandable list with fields that will automatically
        # populate based on a user's keyword selection.
        hd = QLabel("Update Header Defaults: ", self)
        hd.setToolTip("Entries here will update default values for .fits \
        headers if they exist or create new ones if they don't.")
        add_header = gb.GreyButton("+ add a new keyword", 20)
        add_header.setMinimumWidth(125)
        #add_header.setMaximumWidth(175)
        keyword_label = QLabel("FITS Keyword:", hd)
        keyword_label.setAlignment(Qt.AlignHCenter)
        headcaom_label = QLabel("CAOM Keyword:", hd)
        headcaom_label.setAlignment(Qt.AlignHCenter)
        xmlparent_label = QLabel("XML Parent:", hd)
        xmlparent_label.setAlignment(Qt.AlignHCenter)
        extension_label = QLabel("Extension:", hd)
        extension_label.setAlignment(Qt.AlignHCenter)
        default_label = QLabel("Default Value:", hd)
        default_label.setAlignment(Qt.AlignHCenter)
        self.keyword_edit = QComboBox(keyword_label, editable=True)
        self.keyword_edit.addItem("")
        initial_header_type = self.header.header_types[0].lower()
        self.header_keywords = self.keywords[initial_header_type]
        for k in self.header_keywords:
            self.keyword_edit.addItem(k.keyword)
        headcaom_edit = CAOMKeywordBox()
        xmlparent_edit = QComboBox(xmlparent_label, editable=True)
        for p in self.xml_parents:
            xmlparent_edit.addItem(p)
        extension_edit = QLineEdit(extension_label)
        default_edit = QLineEdit(default_label)
        self.headerentrygrid = QGridLayout()
        self.headerentrygrid.addWidget(hd, 0, 0)
        self.headerentrygrid.addWidget(add_header, 0, 3, 1, 2)
        self.headerentrygrid.addWidget(keyword_label, 1, 0)
        self.headerentrygrid.addWidget(headcaom_label, 1, 1)
        self.headerentrygrid.addWidget(xmlparent_label, 1, 2)
        self.headerentrygrid.addWidget(extension_label, 1, 3)
        self.headerentrygrid.addWidget(default_label, 1, 4)
        self.headerentrygrid.addWidget(self.keyword_edit, 2, 0)
        self.headerentrygrid.addWidget(headcaom_edit, 2, 1)
        self.headerentrygrid.addWidget(xmlparent_edit, 2, 2)
        self.headerentrygrid.addWidget(extension_edit, 2, 3)
        self.headerentrygrid.addWidget(default_edit, 2, 4)
        self.firstrow_headers = 2
        self.nextrow_headers = 3
        self.headerentrygrid.setRowStretch(self.nextrow_headers, 1)
        self.headerentrygrid.setColumnStretch(0, 0)
        self.headerentrygrid.setColumnStretch(1, 0)
        self.headerentrygrid.setColumnStretch(2, 0)
        self.headerentrygrid.setColumnStretch(3, 1)
        self.headerentrygrid.setColumnStretch(4, 1)

        # Create a grid layout and add all the layouts and remaining widgets.
        self.grid2 = QGridLayout()
        self.grid2.setColumnStretch(1, 1)
        self.grid2.setColumnStretch(2, 1)
        self.grid2.setColumnStretch(3, 0)
        self.grid2.setColumnStretch(4, 0)
        self.grid2.setColumnStretch(5, 0)
        self.grid2.setRowStretch(9, 0)
        self.grid2.setRowStretch(10, 1)
        self.grid2.addWidget(fp, 0, 0)
        self.grid2.addLayout(self.overwritegrid, 0, 4, 1, 2)
        self.grid2.addLayout(self.pathsgrid, 1, 0, 2, 4)
        self.grid2.addLayout(self.headertypesgrid, 1, 4)
        self.grid2.addLayout(self.datatypesgrid, 2, 4, 1, 1)
        self.grid2.addLayout(self.uniquesgrid, 3, 0, 4, -1)
        self.grid2.addLayout(self.headerentrygrid, 7, 0, 4, -1)

        # Set the window layout and show it.
        self.setLayout(self.grid2)
        self.show()

        # Add button actions.
        browse_hlsp.clicked.connect(self.hlspClicked)
        browse_out.clicked.connect(self.outputClicked)
        add_param.clicked.connect(self.addParameterClicked)
        add_header.clicked.connect(self.addKeywordClicked)
        caom_edit.currentIndexChanged.connect(self.caomKeywordSelected)
        self.header.currentIndexChanged.connect(self.headerTypeChanged)
        self.keyword_edit.currentIndexChanged.connect(self.fitsKeywordSelected)

    def hlspClicked(self):
        """ Launch a file dialog to select a directory containing HLSP data.
        """

        navigate = QFileDialog.getExistingDirectory(self,
                                                    "Select HLSP Directory",
                                                    ".")
        self.data_edit.clear()
        self.data_edit.insert(navigate)


    def outputClicked(self):
        """ Launch a file dialog to define the XML output file name & path.
        """

        navigate = QFileDialog.getSaveFileName(self,
                                               "Save Output XML File",
                                               ".")
        path = navigate[0]
        self.out_edit.clear()
        self.out_edit.insert(path)

    def headerTypeChanged(self):
        """ When the header_type is changed, set the header_keywords to the
        new list.  Re-populate any existing empty keyword menus.  Skip any
        rows that have already been populated.
        """

        # Get the new header type and reset the header_keywords list
        # accordingly.
        new_type = self.header.currentText().lower()
        self.header_keywords = self.keywords[new_type]

        # Iterate through all rows in the headerentrygrid.  Only update the
        # list choices for any rows that are totally empty.
        for row in range(self.firstrow_headers, self.nextrow_headers):
            key_widg = self.headerentrygrid.itemAtPosition(row, 0).widget()
            caom_widg = self.headerentrygrid.itemAtPosition(row, 1).widget()
            xml_widg = self.headerentrygrid.itemAtPosition(row, 2).widget()
            ext_widg = self.headerentrygrid.itemAtPosition(row, 3).widget()
            def_widg = self.headerentrygrid.itemAtPosition(row, 4).widget()
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

        # Get the position of the signal sender.
        sender = self.sender()
        ind = self.uniquesgrid.indexOf(sender)
        pos = self.uniquesgrid.getItemPosition(ind)
        row = pos[0]

        # Get the widgets at this position and the new keyword chosen.
        caom_key_box = self.uniquesgrid.itemAtPosition(row, 0).widget()
        xml_parent_box = self.uniquesgrid.itemAtPosition(row, 1).widget()
        new_caom_selected = caom_key_box.currentText()

        # Get the XML Parent value associated with the new CAOM keyword.
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

        # Add the new widgets to the uniquesgrid layout.
        self.uniquesgrid.addWidget(new_caom, self.nextrow_uniques, 0)
        self.uniquesgrid.addWidget(new_parent, self.nextrow_uniques, 1)
        self.uniquesgrid.addWidget(new_value, self.nextrow_uniques, 2)
        self.uniquesgrid.setRowStretch(self.nextrow_uniques, 0)
        self.uniquesgrid.setRowStretch(self.nextrow_uniques+1, 1)

        # Update self.nextrow_uniques.
        self.nextrow_uniques += 1

        # Connect the new CAOMKeywordBox object to the module that will
        # update the XML Parent depending on the value selected.
        new_caom.currentIndexChanged.connect(self.caomKeywordSelected)

    def fitsKeywordSelected(self):
        """ When a user chooses a header keyword in a headerentrygrid row,
        populate the CAOM Property, XML Parent, Extension, and Default Value
        (if applicaple) fields based on the chosen keyword.
        """

        # Get the position of the signal sender.
        sender = self.sender()
        ind = self.headerentrygrid.indexOf(sender)
        pos = self.headerentrygrid.getItemPosition(ind)
        row = pos[0]

        # Get the sender widget and the new keyword chosen.
        this_keyword = self.headerentrygrid.itemAtPosition(row, 0).widget()
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
        # data from the HeaderKeyword object.
        this_caom = self.headerentrygrid.itemAtPosition(row, 1).widget()
        this_caom.setTo(new_obj.caom)
        this_parent = self.headerentrygrid.itemAtPosition(row, 2).widget()
        n = self.xml_parents.index(new_obj.section)
        this_parent.setCurrentIndex(n)
        this_ext = self.headerentrygrid.itemAtPosition(row, 3).widget()
        this_ext.setText(new_obj.headerName)

    def addKeywordClicked(self):
        """ Create a new row in the headerentrygrid table for modifying .fits
        header keyword properties.
        """

        # Make a new keyword combo box and populate it with the current
        # header_keywords list.
        new_keyword = QComboBox(editable=True)
        new_keyword.addItem("")
        for header_key in self.header_keywords:
            new_keyword.addItem(header_key.keyword)

        # Connect the new keyword combo box to the fitsKeywordSelected action.
        new_keyword.currentIndexChanged.connect(self.fitsKeywordSelected)

        # Make a new 'Parent:' combo box and populate it with self.xml_parents.
        new_xmlparent = QComboBox(editable=True)
        for p in self.xml_parents:
            new_xmlparent.addItem(p)

        # Make new line edits for 'CAOM Property:', 'Extension:', and "Default
        # value".
        new_headcaom = CAOMKeywordBox()
        new_extension = QLineEdit()
        new_default = QLineEdit()

        # Add the new widgets to the headerentrygrid layout.
        self.headerentrygrid.addWidget(new_keyword, self.nextrow_headers, 0)
        self.headerentrygrid.addWidget(new_headcaom, self.nextrow_headers, 1)
        self.headerentrygrid.addWidget(new_xmlparent, self.nextrow_headers, 2)
        self.headerentrygrid.addWidget(new_extension, self.nextrow_headers, 3)
        self.headerentrygrid.addWidget(new_default, self.nextrow_headers, 4)
        self.headerentrygrid.setRowStretch(self.nextrow_headers, 0)
        self.headerentrygrid.setRowStretch(self.nextrow_headers+1, 1)

        # Update self.nextrow_headers.
        self.nextrow_headers += 1

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
            copy_dictionary = copy.deepcopy(sub_dictionary)

            # Look at the first row to see if you're loading into FIRST_ENTRY
            # or NEXT_ENTRY.
            first_parent = self.uniquesgrid.itemAtPosition(
                                                    self.firstrow_uniques,0)
            first_widget = first_parent.widget()
            for param in sub_dictionary.keys():
                value = sub_dictionary[param]

                # If the first widget text is empty, start loading there.
                # Otherwise, load to the self.nextrow_uniques position and
                # create a new set of widgets using addParameterClicked().
                if first_widget.currentText() == "":
                    row = self.firstrow_uniques
                else:
                    row = self.nextrow_uniques
                    self.addParameterClicked()

                # Get the Parent combo box for the current row.
                caom_box = self.uniquesgrid.itemAtPosition(row,0).widget()
                parent_box = self.uniquesgrid.itemAtPosition(row,1).widget()
                value_box = self.uniquesgrid.itemAtPosition(row,2).widget()

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
                caom_box.setTo(param)

                # If the next level is still a dictionary, repeat this process.
                # Otherwise, fill in the Value line edit box.
                if isinstance(sub_dictionary[param], dict):
                    self.loadDictionaries(copy_dictionary)
                else:
                    value_box.insert(sub_dictionary[param])
                    del copy_dictionary[param]

    def loadFromYAML(self, filename):
        """ Load configuration parameters to our ConfigGenerator form using a
        YAML-formatted file.

        :param filename:  The location of the YAML-formatted config file.
        :type filename:  str
        """

        # Read the YAML entries into a dictionary.
        yamlfile = read_yaml(filename)

        # Clear any existing form values before loading the new data.
        self.resetClicked(source="load")

        # Get the 'filepaths' data out of the dictionary and write it into
        # the appropriate lineedits
        try:
            filepaths = yamlfile["filepaths"]
            self.data_edit.insert(filepaths["hlsppath"])
            self.out_edit.insert(filepaths["output"])
        except KeyError:
            msg = "'filepaths' either missing or not formatted in config file"
            raise MyError(msg)

        # Get the 'overwrite' information out of the dictionary and set the
        # radio button
        try:
            if filepaths["overwrite"]:
                self.ow_on.setChecked(True)
            else:
                self.ow_off.setChecked(True)
        except KeyError:
            msg = "'overwrite' not provided in config file"
            raise MyError(msg)

        # Get the 'header_type' data out of the dictionary and set the
        # QComboBox.
        try:
            header_type = yamlfile["header_type"].capitalize()
            header_index = self.header.header_types.index(header_type)
            self.header.setCurrentIndex(header_index)
        except KeyError:
            msg = "'header_type' not provided in config file"
            raise MyError(msg)

        # Get the 'data_type' data out of the dictionary and set the
        # QComboBox.
        try:
            data_type = yamlfile["data_type"].upper()
            dataType_index = self.dt_box.data_types.index(data_type)
            self.dt_box.setCurrentIndex(dataType_index)
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
            load_key = self.headerentrygrid.itemAtPosition(row, 0).widget()
            load_caom = self.headerentrygrid.itemAtPosition(row, 1).widget()
            load_xml = self.headerentrygrid.itemAtPosition(row, 2).widget()
            load_ext = self.headerentrygrid.itemAtPosition(row, 3).widget()
            load_def = self.headerentrygrid.itemAtPosition(row, 4).widget()

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

    def resetClicked(self, source="clicked"):
        """ Clear any changes to the form.
        """

        #Empty the immediately-available elements.
        self.data_edit.clear()
        self.out_edit.clear()
        self.ow_on.setChecked(True)
        self.header.setCurrentIndex(0)
        self.dt_box.setCurrentIndex(0)
        p_one = self.uniquesgrid.itemAtPosition(self.firstrow_uniques,0)
        p_one.widget().setCurrentIndex(0)
        c_one = self.uniquesgrid.itemAtPosition(self.firstrow_uniques,1)
        c_one.widget().setCurrentIndex(0)
        v_one = self.uniquesgrid.itemAtPosition(self.firstrow_uniques,2)
        v_one.widget().clear()
        k_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,0)
        k_one.widget().setCurrentIndex(0)
        h_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,1)
        h_one.widget().setCurrentIndex(0)
        x_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,2)
        x_one.widget().setCurrentIndex(0)
        e_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,3)
        e_one.widget().clear()
        d_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,3)
        d_one.widget().clear()

        # Delete any unique parameter entries beyond the first table row.
        delete_these = list(reversed(range(self.firstrow_uniques+1,
                                           self.uniquesgrid.rowCount())))
        if len(delete_these) > 0:
            for n in delete_these:
                test = self.uniquesgrid.itemAtPosition(n,0)
                if test == None:
                    continue
                self.uniquesgrid.itemAtPosition(n,0).widget().setParent(None)
                self.uniquesgrid.itemAtPosition(n,1).widget().setParent(None)
                self.uniquesgrid.itemAtPosition(n,2).widget().setParent(None)
        self.nextrow_uniques = self.firstrow_uniques + 1

        # Delete any header keyword entries beyond the first row.
        delete_these = list(reversed(range(self.firstrow_headers+1,
                                           self.headerentrygrid.rowCount())))
        if len(delete_these) > 0:
            for n in delete_these:
                test = self.headerentrygrid.itemAtPosition(n,0)
                if test == None:
                    continue
                widg1 = self.headerentrygrid.itemAtPosition(n,0).widget()
                widg1.setParent(None)
                widg2 = self.headerentrygrid.itemAtPosition(n,1).widget()
                widg2.setParent(None)
                widg3 = self.headerentrygrid.itemAtPosition(n,2).widget()
                widg3.setParent(None)
                widg4 = self.headerentrygrid.itemAtPosition(n,3).widget()
                widg4.setParent(None)
                widg5 = self.headerentrygrid.itemAtPosition(n,4).widget()
                widg5.setParent(None)
        self.nextrow_headers = self.firstrow_headers + 1

    def collectInputs(self):
        """ Assemble everything the user has input to the form into a
        dictionary.
        """

        # Initialize dictionaries to populate.
        config = {}
        filepaths = {}

        # Get the HLSP data filepath.  Throw an error if it does not exist.
        hlsppath = self.data_edit.text()
        if hlsppath == "":
            raise MyError("HLSP Data file path is missing!")
        else:
            filepaths["hlsppath"] = hlsppath

        # Get the output filepath from the line edit.  Throw an error if it is
        # empty.  Append with a '.xml' if not already there.  Get the overwrite
        # flag from the checkbox.
        out = self.out_edit.text()
        if out == "":
            raise MyError("Output file path is missing!")
        if not out.endswith(".xml"):
            out += ".xml"
        filepaths["output"] = out
        filepaths["overwrite"] = self.ow_on.isChecked()
        config["filepaths"] = filepaths

        # Grab the selected fits header type.
        config["header_type"] = self.header.currentText().lower()

        # Get the data type.  Throw an error if none selected.
        dt = self.dt_box.currentText().lower()
        if dt == "":
            raise MyError("No data type selected!")
        else:
            config["data_type"] = dt

        # Collect all the unique parameters the user has entered.  Start at row
        # self.firstrow_uniques and search through all rows the user may have
        # added.
        uniques = {}
        for row in range(self.firstrow_uniques, self.uniquesgrid.rowCount()):
            add_caom = self.uniquesgrid.itemAtPosition(row, 0)
            add_parent = self.uniquesgrid.itemAtPosition(row, 1)
            add_value = self.uniquesgrid.itemAtPosition(row, 2)
            unique_parent = None
            unique_caom = None
            unique_value = None

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
            new_uniques = insert[0]
            inserted = insert[1]

            # If crawl_dictionary did not insert the new parameter, the defined
            # parent is not currently present in the dictionary, so create a
            # new entry.
            if not inserted:
                uniques[unique_parent] = parameter
            else:
                uniques = new_uniques
        config["unique_parameters"] = uniques

        # Collect all header keyword entries the user may have provided.
        keywords = {}
        for row in range(self.firstrow_headers, self.nextrow_headers):
            add_key = self.headerentrygrid.itemAtPosition(row, 0)
            add_caom = self.headerentrygrid.itemAtPosition(row, 1)
            add_xml = self.headerentrygrid.itemAtPosition(row, 2)
            add_ext = self.headerentrygrid.itemAtPosition(row, 3)
            add_def = self.headerentrygrid.itemAtPosition(row, 4)
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
                unique_caom = str(add_caom.widget().text())
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
