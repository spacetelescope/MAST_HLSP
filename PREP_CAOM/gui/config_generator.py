"""
..module:: crawl_dictionary
    :synopsis:  This module is designed to add a given parameter to a provided
    dictionary under a designated parent.  It searches for the parent
    recursively in order to examine all possible levels of nested dictionaries.
    If the parent is found, the parameter is added to the dictionary.  The
    entire dictionary is returned, along with a boolean flag to indicate
    whether or not the insertion was successful.

..class:: ResetConfirm
    :synopsis:  This class defines a PyQt window to display a confirmation
    popup dialog window.  The user can either choose 'yes' or 'no', which will
    set the self.confirm boolean and close the popup window.  This is used when
    the user chooses to reset the main ConfigGenerator form.

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
import gui.GUIbuttons as gb
import util.check_paths as cp
from hlsp_to_xml import hlsp_to_xml
from gui.MyError import MyError
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
class HeaderKeyword():
    def __init__(self, keyword):
        self.keyword = keyword
        self.caom = None
        self.headerName = None
        self.section = "metadataList"
        self.default = "None"

class HeaderKeywordList(list):
    def __init__(self, header_type):
        super().__init__()
        self.header_type = header_type
        self.keywords = []

    def add(self, hk):
        if isinstance(hk, HeaderKeyword):
            self.append(hk)
            self.keywords.append(hk.keyword)

    def find(self, target_keyword):
        for member in self:
            if member.keyword == target_keyword:
                return member
        return None

    def sort(self):
        sorted_list = HeaderKeywordList(self.header_type)
        for k in sorted(self.keywords):
            keyword_obj = self.find(k)
            sorted_list.add(keyword_obj)
        return sorted_list

def read_header_keywords_table(filepath):
    tablepath = cp.check_existing_file(filepath)
    keywords = []
    with open(tablepath) as csvfile:
        hlsp_keys = csv.reader(csvfile, delimiter=",")
        for row in hlsp_keys:
            keywords.append(row)
        csvfile.close()

    cols = keywords[0]
    full_table = {}
    for column in cols:
        n = cols.index(column)
        values = []
        for row in keywords[1:]:
            values.append(row[n])
        full_table[column] = values

    all_caom = full_table["caom"]
    all_headerName = full_table["headerName"]
    all_section = full_table["section"]

    cols.remove("caom")
    cols.remove("section")
    cols.remove("headerName")
    header_types = cols

    header_keywords = {}
    for _type in header_types:
        keywords = full_table[_type]
        keyword_objects = HeaderKeywordList(header_type=_type)
        for key in keywords:
            if key == "" or key.lower() == "null":
                continue
            n = keywords.index(key)
            hk = HeaderKeyword(key)
            hk.caom = all_caom[n]
            hk.headerName = all_headerName[n]
            hk.section = all_section[n]
            keyword_objects.add(hk)
        header_keywords[_type] = keyword_objects.sort()

    return header_keywords

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


class ResetConfirm(QDialog):
    """
    Create a reset confirmation dialog window before clearing all changes.
    """

    def __init__(self):
        super().__init__()
        self.confirmUI()

    def confirmUI(self):
        """
        Launch a confirmation dialog with yes/no button options.
        """
        self.confirm = False
        label = QLabel("Reset all current changes to this form?")
        label.setAlignment(Qt.AlignHCenter)
        yes = QPushButton("Yes")
        no = QPushButton("No")

        g = QGridLayout()
        g.addWidget(label, 0, 0, 1, -1)
        g.addWidget(yes, 1, 0)
        g.addWidget(no, 1, 1)
        self.setLayout(g)
        self.setWindowTitle("Confirm Reset")
        self.resize(300, 50)
        self.show()

        yes.clicked.connect(self.yesClicked)
        no.clicked.connect(self.noClicked)

    def yesClicked(self):
        """
        Set the confirm boolean to True if 'Yes' is clicked.
        """
        self.confirm = True
        self.close()

    def noClicked(self):
        """
        Set the confirm boolean to False if 'No' is clicked.
        """
        self.confirm = False
        self.close()

#--------------------

class ConfigGenerator(QWidget):
    """
    This class builds a pyqt GUI for generating a properly-formatted yaml
    config file to feed into the template XML generator.  There is also the
    option to save the yaml file and immediately launch hlsp_to_xml with the
    new file.
    """

    def __init__(self):
        super().__init__()
        self.file_types = None
        self.initUI()


    def initUI(self):
        """
        Create a GUI with input fields for multiple parameters, which will be
        aggregated into a .yaml config file.
        """

        #Create some formatting items for use throughout.
        firstcol = 100
        space = QSpacerItem(50, 1)
        self.keywords = read_header_keywords_table(HEADER_KEYWORDS)

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

        #Set the type of .fits headers with a QComboBox object.
        ht = QLabel("Header Type: ", self)
        ht.setMinimumWidth(firstcol)
        ht.setToolTip("Select the FITS header type this HLSP uses.")
        self.header = QComboBox(ht)
        self.header.setMinimumWidth(175)
        self.header_types = ["Standard", "Kepler"]
        for typ in self.header_types:
            self.header.addItem(typ)
        self.headertypesgrid = QGridLayout()
        self.headertypesgrid.addItem(space, 0, 0)
        self.headertypesgrid.addWidget(ht, 0, 1)
        self.headertypesgrid.addWidget(self.header, 0, 2)

        #Select all appropriate data types to apply to the config file.
        dt = QLabel("Data Type: ", self)
        dt.setMinimumWidth(firstcol)
        dt.setToolTip("Add special CAOM parameters for various data types.")
        self.datatypes = ["", "IMAGE", "SPECTRUM", "TIMESERIES", "VISIBILITY",
                          "EVENTLIST", "CUBE", "CATALOG", "MEASUREMENTS"]
        self.dt_box = QComboBox()
        self.dt_box.setMinimumWidth(175)
        for typ in self.datatypes:
            self.dt_box.addItem(typ)

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
        add_param.setMaximumWidth(175)
        parent_param = QLabel("Parent:", up)
        parent_param.setAlignment(Qt.AlignHCenter)
        caom_param = QLabel("CAOM Keyword:", up)
        caom_param.setAlignment(Qt.AlignHCenter)
        value_param = QLabel("Value:", up)
        value_param.setAlignment(Qt.AlignHCenter)
        parent_edit = QComboBox(parent_param, editable=True)
        self.xml_parents = ["", "metadataList", "provenance"]
        for p in self.xml_parents:
            parent_edit.addItem(p)
        caom_edit = QLineEdit(caom_param)
        value_edit = QLineEdit(value_param)
        self.uniquesgrid = QGridLayout()
        self.uniquesgrid.addWidget(up, 0, 0)
        self.uniquesgrid.addWidget(add_param, 0, 1)
        self.uniquesgrid.addWidget(parent_param, 1, 0)
        self.uniquesgrid.addWidget(caom_param, 1, 1)
        self.uniquesgrid.addWidget(value_param, 1, 2)
        self.uniquesgrid.addWidget(parent_edit, 2, 0)
        self.uniquesgrid.addWidget(caom_edit, 2, 1)
        self.uniquesgrid.addWidget(value_edit, 2, 2)
        self.firstrow_uniques = 2
        self.nextrow_uniques = 3
        self.uniquesgrid.setRowStretch(self.nextrow_uniques, 1)
        self.uniquesgrid.setColumnStretch(0, 0)
        self.uniquesgrid.setColumnStretch(1, 1)
        self.uniquesgrid.setColumnStretch(2, 1)

        ###NEW HEADER UPDATE SECTION
        #Create custom unique parameters to write into the yaml file.  This
        #list is expandable.  Custom parents can be defined in addition to
        #metadataList and provenance.
        hd = QLabel("Update Header Defaults: ", self)
        hd.setToolTip("Entries here will update default values for .fits \
        headers if they exist or create new ones if they don't.")
        add_header = gb.GreyButton("+ add a new keyword", 20)
        add_header.setMinimumWidth(125)
        add_header.setMaximumWidth(175)
        keyword_label = QLabel("Keyword:", hd)
        keyword_label.setAlignment(Qt.AlignHCenter)
        headcaom_label = QLabel("CAOM Property:", hd)
        headcaom_label.setAlignment(Qt.AlignHCenter)
        xmlparent_label = QLabel("XML Parent:", hd)
        xmlparent_label.setAlignment(Qt.AlignHCenter)
        extension_label = QLabel("Extension:", hd)
        extension_label.setAlignment(Qt.AlignHCenter)
        default_label = QLabel("Default Value:", hd)
        default_label.setAlignment(Qt.AlignHCenter)
        self.keyword_edit = QComboBox(keyword_label, editable=True)
        self.keyword_edit.addItem("")
        self.header_keywords = self.keywords[self.header_types[0].lower()]
        for k in self.header_keywords:
            self.keyword_edit.addItem(k.keyword)
        headcaom_edit = QLineEdit(headcaom_label)
        xmlparent_edit = QComboBox(xmlparent_label, editable=True)
        for p in self.xml_parents:
            xmlparent_edit.addItem(p)
        extension_edit = QLineEdit(extension_label)
        default_edit = QLineEdit(default_label)
        self.headerentrygrid = QGridLayout()
        self.headerentrygrid.addWidget(hd, 0, 0)
        self.headerentrygrid.addWidget(add_header, 0, 1, 1, 2)
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
        self.headerentrygrid.setColumnStretch(1, 1)
        self.headerentrygrid.setColumnStretch(2, 1)

        #Create a grid layout and add all the layouts and remaining widgets.
        self.grid2 = QGridLayout()
        self.grid2.setColumnStretch(1, 1)
        self.grid2.setColumnStretch(2, 1)
        self.grid2.setColumnStretch(3, 0)
        self.grid2.setColumnStretch(4, 0)
        #self.grid2.setColumnMinimumWidth(4, 100)
        self.grid2.setColumnStretch(5, 0)
        self.grid2.setRowStretch(9, 0)
        self.grid2.setRowStretch(10, 1)
        self.grid2.addWidget(fp, 0, 0)
        self.grid2.addLayout(self.pathsgrid, 1, 0, 2, 4)
        self.grid2.addLayout(self.overwritegrid, 0, 4, 1, 2)
        self.grid2.addLayout(self.uniquesgrid, 3, 0, 4, -1)
        self.grid2.addLayout(self.headertypesgrid, 1, 4)
        self.grid2.addLayout(self.datatypesgrid, 2, 4, 1, 1)
        self.grid2.addLayout(self.headerentrygrid, 7, 0, 4, -1)

        #Set the window layout and show it.
        self.setLayout(self.grid2)
        self.show()

        #Add button actions.
        browse_hlsp.clicked.connect(self.hlspClicked)
        browse_out.clicked.connect(self.outputClicked)
        add_param.clicked.connect(self.addParameterClicked)
        add_header.clicked.connect(self.addKeywordClicked)
        self.header.currentIndexChanged.connect(self.headerTypeChanged)
        self.keyword_edit.currentIndexChanged.connect(self.keywordSelected)

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
        new_type = self.header.currentText().lower()
        self.header_keywords = self.keywords[new_type]
        for row in range(self.firstrow_headers, self.nextrow_headers):
            key_widg = self.headerentrygrid.itemAtPosition(row, 0).widget()
            caom_widg = self.headerentrygrid.itemAtPosition(row, 1).widget()
            xml_widg = self.headerentrygrid.itemAtPosition(row, 2).widget()
            ext_widg = self.headerentrygrid.itemAtPosition(row, 3).widget()
            def_widg = self.headerentrygrid.itemAtPosition(row, 4).widget()
            caom_text = str(caom_widg.text())
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

    def addParameterClicked(self):
        """ Add a new unique parameter entry row into the self.nextrow_uniques
        position, then update self.nextrow_uniques.
        """

        # Make a new 'Parent:' combo box and populate it with self.xml_parents.
        new_parent = QComboBox(editable=True)
        for p in self.xml_parents:
            new_parent.addItem(p)

        # Make new line edits for 'CAOM Keyword:' and 'Value:'.
        new_caom = QLineEdit()
        new_value = QLineEdit()

        # Add the new widgets to the uniquesgrid layout.
        self.uniquesgrid.addWidget(new_parent, self.nextrow_uniques, 0)
        self.uniquesgrid.addWidget(new_caom, self.nextrow_uniques, 1)
        self.uniquesgrid.addWidget(new_value, self.nextrow_uniques, 2)
        self.uniquesgrid.setRowStretch(self.nextrow_uniques, 0)
        self.uniquesgrid.setRowStretch(self.nextrow_uniques+1, 1)

        # Update self.nextrow_uniques.
        self.nextrow_uniques += 1

    def keywordSelected(self):
        sender = self.sender()
        ind = self.headerentrygrid.indexOf(sender)
        pos = self.headerentrygrid.getItemPosition(ind)
        row = pos[0]
        this_keyword = self.headerentrygrid.itemAtPosition(row, 0).widget()
        new_keyword = this_keyword.currentText()
        try:
            new_obj = self.header_keywords.find(new_keyword)
        except KeyError:
            return

        if new_obj is None:
            return
        this_caom = self.headerentrygrid.itemAtPosition(row, 1).widget()
        this_caom.setText(new_obj.caom)
        this_parent = self.headerentrygrid.itemAtPosition(row, 2).widget()
        n = self.xml_parents.index(new_obj.section)
        this_parent.setCurrentIndex(n)
        this_ext = self.headerentrygrid.itemAtPosition(row, 3).widget()
        this_ext.setText(new_obj.headerName)

    def addKeywordClicked(self):
        """ New Header Keyword action
        """

        # Make a new 'Parent:' combo box and populate it with self.xml_parents.
        new_keyword = QComboBox(editable=True)
        new_keyword.addItem("")
        for hk in self.header_keywords:
            new_keyword.addItem(hk.keyword)
        new_keyword.currentIndexChanged.connect(self.keywordSelected)

        new_xmlparent = QComboBox(editable=True)
        for p in self.xml_parents:
            new_xmlparent.addItem(p)

        # Make new line edits for 'CAOM Keyword:' and 'Value:'.
        new_headcaom = QLineEdit()
        new_extension = QLineEdit()
        new_default = QLineEdit()

        # Add the new widgets to the uniquesgrid layout.
        self.headerentrygrid.addWidget(new_keyword, self.nextrow_headers, 0)
        self.headerentrygrid.addWidget(new_headcaom, self.nextrow_headers, 1)
        self.headerentrygrid.addWidget(new_xmlparent, self.nextrow_headers, 2)
        self.headerentrygrid.addWidget(new_extension, self.nextrow_headers, 3)
        self.headerentrygrid.addWidget(new_default, self.nextrow_headers, 4)
        self.headerentrygrid.setRowStretch(self.nextrow_headers, 0)
        self.headerentrygrid.setRowStretch(self.nextrow_headers+1, 1)

        # Update self.nextrow_uniques.
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
                # Otherwise, load to the self.nextrow_uniques position and create a
                # new set of widgets using addParameterClicked().
                if first_widget.currentText() == "":
                    row = self.firstrow_uniques
                else:
                    row = self.nextrow_uniques
                    self.addParameterClicked()

                # Get the Parent combo box for the current row.
                parent_box = self.uniquesgrid.itemAtPosition(row,0).widget()
                caom_box = self.uniquesgrid.itemAtPosition(row,1).widget()
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
                caom_box.insert(param)

                # If the next level is still a dictionary, repeat this process.
                # Otherwise, fill in the Value line edit box.
                if isinstance(sub_dictionary[param], dict):
                    self.loadDictionaries(copy_dictionary)
                else:
                    value_box.insert(sub_dictionary[param])
                    del copy_dictionary[param]

    def loadFromYAML(self, filename):

        #Read the YAML entries into a dictionary.
        yamlfile = read_yaml(filename)

        #Clear any existing form values before loading the new data.
        self.resetClicked(source="load")

        #Pull out the data and insert into the form.
        filepaths = yamlfile["filepaths"]
        header_type = yamlfile["header_type"]
        keyword_updates = yamlfile["keyword_updates"]
        data_type = yamlfile["data_type"]
        uniques = yamlfile["unique_parameters"]
        self.file_types = yamlfile["file_types"]
        self.data_edit.insert(filepaths["hlsppath"])
        self.out_edit.insert(filepaths["output"])
        if filepaths["overwrite"]:
            self.ow_on.setChecked(True)
        else:
            self.ow_off.setChecked(True)

        header_index = self.header_types.index(header_type.capitalize())
        dataType_index = self.datatypes.index(data_type.upper())

        self.header.setCurrentIndex(header_index)
        self.dt_box.setCurrentIndex(dataType_index)

        #Load the unique parameters dictionary into the unique parameters table
        self.loadDictionaries(uniques)

        for key in sorted(keyword_updates.keys()):
            values = keyword_updates[key]
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

            available_keys = [load_key.itemText(x)
                                            for x in range(load_key.count())]
            available_xml = [load_xml.itemText(y)
                                            for y in range(load_xml.count())]

            if key in available_keys:
                load_key.setCurrentIndex(available_keys.index(key))
            else:
                load_key.setCurrentText(key)
            load_caom.setText(values["caom"])
            if values["section"] in available_xml:
                load_xml.setCurrentIndex(
                                        available_xml.index(values["section"]))
            else:
                load_xml.setCurrentText(values["section"])
            load_ext.setText(values["headerName"])
            load_def.setText(values["headerDefaultValue"])

        return True


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
        c_one.widget().clear()
        v_one = self.uniquesgrid.itemAtPosition(self.firstrow_uniques,2)
        v_one.widget().clear()
        k_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,0)
        k_one.widget().setCurrentIndex(0)
        h_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,1)
        h_one.widget().clear()
        x_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,2)
        x_one.widget().setCurrentIndex(0)
        e_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,3)
        e_one.widget().clear()
        d_one = self.headerentrygrid.itemAtPosition(self.firstrow_headers,3)
        d_one.widget().clear()

        #Delete any unique parameter entries beyond the first table row.
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
        dictionary.  Then write that dictionary into a yaml file.
        """

        config = {}
        filepaths = {}

        # Get the HLSP data filepath.  Throw an error if it does not exist.
        hlsppath = self.data_edit.text()
        if hlsppath == "":
            raise MyError("HLSP Data file path is missing!")
            return
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
        # self.firstrow_uniques and search through all rows the user may have added.
        uniques = {}
        for row in range(self.firstrow_uniques, self.uniquesgrid.rowCount()):
            add_parent = self.uniquesgrid.itemAtPosition(row, 0)
            add_caom = self.uniquesgrid.itemAtPosition(row, 1)
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
                unique_caom = str(caom_widget.text())
            if add_value is not None:
                value_widget = add_value.widget()
                unique_value = str(value_widget.text())
            if unique_parent == "" and unique_caom == "" and unique_value == "":
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

            # Skip totally empty rows, empty values are okay for defining a new
            # parent.
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

        return config

        # Write the config dictionary into a yaml file using a dialog.



    def nogenClicked(self):
        """ When generate is clicked, collect all the user inputs and write the
        yaml file.
        """
        self.collectInputs()


    def norunClicked(self):
        """ When run is clicked, collect all the user inputs, write the yaml
        file, and send the file to hlsp_to_xml.
        """
        config = self.collectInputs()
        if config is not None:
            self.status.setTextColor(Qt.darkGreen)
            self.status.append("Launching hlsp_to_xml.py!")
            self.status.append("See terminal for script output.")
            hlsp_to_xml(config)
        else:
            raise MyError("No .yaml file generated!")

#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = ConfigGenerator()
    sys.exit(app.exec_())
