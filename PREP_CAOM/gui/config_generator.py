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
    :synopsis:  This class defines PyQt widget that uses multiple methods to
    collect user input in order to generate a .yaml config file needed by
    ../hlsp_to_xml.py.  This will help to ensure that these config files are
    properly formatted and include the necessary information.  This form
    includes functionality to add extra rows for unique parameter definitions,
    load an existing .yaml file into the form, reset all changes made to the
    form, save all inputs to a .yaml config file, or save a .yaml file and
    immediately launch ../hlsp_to_xml.py with said file.
"""

import copy
import os
import sys
import yaml
from hlsp_to_xml import hlsp_to_xml
from util.read_yaml import read_yaml
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

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
        self.initUI()


    def initUI(self):
        """
        Create a GUI with input fields for multiple parameters, which will be
        aggregated into a .yaml config file.
        """

        #Create some formatting items for use throughout.
        firstcol = 140
        space = QSpacerItem(30, 1)

        #Create a section for input of filepath variables.  Includes lineedit
        #objects and buttons to launch file dialogs if the desired paths are
        #local.
        fp = QLabel("Filepaths:", self)
        data = QLabel("HLSP Data: ", fp)
        data.setAlignment(Qt.AlignRight)
        data.setToolTip("Enter the location of the HLSP data files to scan.")
        self.data_edit = QLineEdit(data)
        ext = QLabel("File Extensions Table: ", fp)
        ext.setAlignment(Qt.AlignRight)
        ext.setToolTip("Enter the location of the CSV file containing HLSP file information.")
        self.ext_edit = QLineEdit(ext)
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
        browse_ext.setIcon(icon)
        browse_ext.setIconSize(QSize(14,14))
        browse_ext.setMaximumWidth(26)
        browse_ext.setMaximumHeight(22)
        browse_out = QPushButton()
        browse_out.setIcon(icon)
        browse_out.setIconSize(QSize(14,14))
        browse_out.setMaximumWidth(26)
        browse_out.setMaximumHeight(22)
        self.pathsgrid = QGridLayout()
        self.pathsgrid.addWidget(data, 0, 0)
        self.pathsgrid.addWidget(self.data_edit, 0, 1)
        self.pathsgrid.addWidget(browse_hlsp, 0, 2)
        self.pathsgrid.addWidget(ext, 1, 0)
        self.pathsgrid.addWidget(self.ext_edit, 1, 1)
        self.pathsgrid.addWidget(browse_ext, 1, 2)
        self.pathsgrid.addWidget(out, 2, 0)
        self.pathsgrid.addWidget(self.out_edit, 2, 1)
        self.pathsgrid.addWidget(browse_out, 2, 2)

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
        self.header_types = ["Standard", "Kepler"]
        for typ in self.header_types:
            self.header.addItem(typ)
        self.headergrid = QGridLayout()
        self.headergrid.addItem(space, 0, 0)
        self.headergrid.addWidget(ht, 0, 1)
        self.headergrid.addWidget(self.header, 0, 2)

        #Select all appropriate data types to apply to the config file.
        dt = QLabel("Included Data Types: ", self)
        dt.setMinimumWidth(firstcol)
        dt.setToolTip("Add special CAOM parameters for various data types.")
        self.lightcurve = QCheckBox("Light Curves", dt)
        self.spectra = QCheckBox("Spectra", dt)
        self.catalog = QCheckBox("Catalogs", dt)
        self.simulation = QCheckBox("Models / Sims", dt)
        self.datatypesgrid = QGridLayout()
        self.datatypesgrid.addItem(space, 0, 0, -1, 1)
        self.datatypesgrid.addWidget(dt, 0, 1)
        self.datatypesgrid.addWidget(self.lightcurve, 0, 2)
        self.datatypesgrid.addWidget(self.spectra, 1, 2)
        self.datatypesgrid.addWidget(self.catalog, 2, 2)
        self.datatypesgrid.addWidget(self.simulation, 3, 2)

        #Create custom unique parameters to write into the yaml file.  This
        #list is expandable.  Custom parents can be defined in addition to
        #metadataList and provenance.
        up = QLabel("HLSP-Unique Parameters: ", self)
        up.setToolTip("Define additional CAOM parameters to insert that are not defined in the FITS headers.")
        add_param = QPushButton("+ add a new parameter")
        add_param.setStyleSheet("""
                                QPushButton {
                                    background-color: #f2f2f2;
                                    border: 2px solid #afafaf;
                                    border-radius: 8px;
                                    height: 20px
                                    }
                                QPushButton:hover {
                                    border: 4px solid #afafaf;
                                    }
                                QPushButton:pressed {
                                    background-color: #afafaf;
                                    }""")
        add_param.setMinimumWidth(165)
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
        self.firstrow = 2
        self.nextrow = 3
        self.uniquesgrid.setRowStretch(self.nextrow, 1)
        self.uniquesgrid.setColumnStretch(0, 0)
        self.uniquesgrid.setColumnStretch(1, 1)
        self.uniquesgrid.setColumnStretch(2, 1)

        #Create an area for program output messages.
        status_label = QLabel("Results:")
        status_label.setAlignment(Qt.AlignHCenter)
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setLineWrapMode(QTextEdit.NoWrap)
        self.status.setStyleSheet("border-style: solid; \
                                  border-width: 1px; \
                                  background: rgba(235,235,235,0%);")

        #Create the four main buttons for the widget.
        load = QPushButton("Load YAML File")
        load.setStyleSheet("""
                                QPushButton {
                                    background-color: #f2f2f2;
                                    border: 2px solid #afafaf;
                                    border-radius: 8px;
                                    height: 40px
                                    }
                                QPushButton:hover {
                                    border: 4px solid #afafaf;
                                    }
                                QPushButton:pressed {
                                    background-color: #afafaf;
                                    }""")
        reset = QPushButton("Reset Form")
        reset.setStyleSheet("""
                                QPushButton {
                                    background-color: #f2f2f2;
                                    border: 2px solid #afafaf;
                                    border-radius: 8px;
                                    height: 40px;
                                    }
                                QPushButton:hover {
                                    border: 4px solid #afafaf;
                                    }
                                QPushButton:pressed {
                                    background-color: #afafaf;
                                    }""")
        reset.setMinimumWidth(125)
        reset.setMaximumWidth(125)
        gen = QPushButton("Generate YAML File", self)
        gen.setStyleSheet("""
                          QPushButton {
                            background-color: #7af442;
                            border: 2px solid #45a018;
                            border-radius: 8px;
                            height: 40px
                            }
                          QPushButton:hover {
                            border: 4px solid #45a018;
                            }
                          QPushButton:pressed {
                            background-color: #45a018;
                            }""")
        run = QPushButton("Generate YAML and Run Script", self)
        run.setStyleSheet("""
                          QPushButton {
                            background-color: #42d4f4;
                            border: 2px solid #005fa3;
                            border-radius: 8px;
                            height: 40px
                            }
                          QPushButton:hover {
                            border: 4px solid #005fa3;
                            }
                          QPushButton:pressed {
                            background-color: #005fa3;
                            }""")
        self.buttonsgrid = QGridLayout()
        empty = QSpacerItem(25, 1)
        self.buttonsgrid.setColumnStretch(0, 0)
        self.buttonsgrid.setColumnStretch(1, 0)
        self.buttonsgrid.addItem(empty, 0, 0, -1, 1)
        self.buttonsgrid.addWidget(load, 0, 1)
        self.buttonsgrid.addWidget(gen, 0, 2)
        self.buttonsgrid.addWidget(reset, 1, 1)
        self.buttonsgrid.addWidget(run, 1, 2)

        #Create a grid layout and add all the layouts and remaining widgets.
        self.grid2 = QGridLayout()
        self.grid2.setColumnStretch(1, 1)
        self.grid2.setColumnStretch(2, 1)
        self.grid2.setColumnStretch(3, 0)
        self.grid2.setColumnStretch(4, 0)
        self.grid2.setColumnMinimumWidth(4, 100)
        self.grid2.setColumnStretch(5, 0)
        self.grid2.setRowStretch(9, 0)
        self.grid2.setRowStretch(10, 1)
        self.grid2.addWidget(fp, 0, 0)
        self.grid2.addLayout(self.buttonsgrid, 0, 4, 4, 2)
        self.grid2.addLayout(self.pathsgrid, 1, 0, 3, 4)
        self.grid2.addLayout(self.overwritegrid, 4, 5, 1, 2)
        self.grid2.addLayout(self.uniquesgrid, 4, 0, 4, 5)
        self.grid2.addLayout(self.headergrid, 5, 5)
        self.grid2.addLayout(self.datatypesgrid, 6, 5, 4, 1)
        self.grid2.addWidget(status_label, 8, 0, 1, 5)
        self.grid2.addWidget(self.status, 9, 0, 2, 5)
        self.grid2.addItem(space, 10, 0, -1, -1)

        #Set the window layout and show it.
        self.setLayout(self.grid2)
        self.show()

        #Add button actions.
        browse_hlsp.clicked.connect(self.hlspClicked)
        browse_ext.clicked.connect(self.extensionsClicked)
        browse_out.clicked.connect(self.outputClicked)
        add_param.clicked.connect(self.addClicked)
        load.clicked.connect(self.loadClicked)
        reset.clicked.connect(self.resetClicked)
        gen.clicked.connect(self.genClicked)
        run.clicked.connect(self.runClicked)


    def hlspClicked(self):
        """
        Launch a file dialog to select a directory containing HLSP data.
        """

        navigate = QFileDialog.getExistingDirectory(self,
                                                    "Select HLSP Directory",
                                                    ".")
        self.data_edit.clear()
        self.data_edit.insert(navigate)


    def extensionsClicked(self):
        """
        Launch a file dialog to select a .csv file containing data definitions.
        """

        navigate = QFileDialog.getOpenFileName(self,
                                               "Select File Descriptions File",
                                               ".")
        path = navigate[0]
        self.ext_edit.clear()
        self.ext_edit.insert(path)


    def outputClicked(self):
        """
        Launch a file dialog to define the XML output file name & path.
        """

        navigate = QFileDialog.getSaveFileName(self,
                                               "Save Output XML File",
                                               ".")
        path = navigate[0]
        self.out_edit.clear()
        self.out_edit.insert(path)


    def addClicked(self):
        """
        Use the global NEXT_ENTRY variable to add a new unique parameter
        entry row.
        """

        new_parent = QComboBox(editable=True)
        for p in self.xml_parents:
            new_parent.addItem(p)
        new_caom = QLineEdit()
        new_value = QLineEdit()
        self.uniquesgrid.addWidget(new_parent, self.nextrow, 0)
        self.uniquesgrid.addWidget(new_caom, self.nextrow, 1)
        self.uniquesgrid.addWidget(new_value, self.nextrow, 2)
        self.uniquesgrid.setRowStretch(self.nextrow, 0)
        self.uniquesgrid.setRowStretch(self.nextrow+1, 1)
        self.nextrow += 1


    def loadDictionaries(self, uniques):
        """
        Recursively handles loading multi-level dictionaries to the unique
        parameters table.

        :param uniques:  A dictionary containing CAOM parameters.  May contain
        nested dictionaries.
        :type uniques:  dict
        """

        if uniques is None:
            return None

        parents = uniques.keys()
        for p in parents:
            sub_dictionary = uniques[p]
            copy_dictionary = copy.deepcopy(sub_dictionary)

            #Look at the first row to see if you're loading into FIRST_ENTRY
            #or NEXT_ENTRY.
            first_parent = self.uniquesgrid.itemAtPosition(self.firstrow,0).widget()
            for param in sub_dictionary.keys():
                value = sub_dictionary[param]
                if first_parent.currentText() == "":
                    row = self.firstrow
                else:
                    row = self.nextrow
                    self.addClicked()

                #Get the Parent combo box for the current row.
                parent_box = self.uniquesgrid.itemAtPosition(row,0).widget()
                caom_box = self.uniquesgrid.itemAtPosition(row,1).widget()
                value_box = self.uniquesgrid.itemAtPosition(row,2).widget()

                #If the desired parent is already an option, set to that.
                #Otherwise add it as a new option in the combo box.
                if p in self.xml_parents:
                    parent_index = self.xml_parents.index(p)
                    parent_box.setCurrentIndex(parent_index)
                else:
                    parent_box.addItem(p)
                    parent_box.setCurrentIndex(parent_box.findText(p))
                    self.xml_parents.append(p)

                #Fill in the CAOM line edit box.
                caom_box.insert(param)

                #If the next level is still a dictionary, repeat this process.
                #Otherwise, fill in the Value line edit box.
                if isinstance(sub_dictionary[param], dict):
                    self.loadDictionaries(copy_dictionary)
                else:
                    value_box.insert(sub_dictionary[param])
                    del copy_dictionary[param]



    def loadClicked(self):
        """
        Open a user-selected YAML file and load the elements into the form.
        """

        #Launch a file dialog for user file selection.
        loadit = QFileDialog.getOpenFileName(self, "Load a YAML file", ".")
        filename = loadit[0]

        #Check that the selected file is a valid choice.  Uses the QFileDialog
        #so not worrying about picking a file that doesn't exist.
        if filename == "":
            return None
        elif not filename.endswith(".yaml"):
            self.status.setTextColor(Qt.red)
            self.status.append("{0} is not a .yaml file!".format(filename))
            return None

        #Read the YAML entries into a dictionary.
        yamlfile = read_yaml(filename)

        #Clear any existing form values before loading the new data.
        self.resetClicked(source="load")

        #Pull out the data and insert into the form.
        filepaths = yamlfile["filepaths"]
        header_type = yamlfile["header_type"]
        data_types = yamlfile["data_types"]
        uniques = yamlfile["unique_parameters"]
        self.data_edit.insert(filepaths["hlsppath"])
        self.ext_edit.insert(filepaths["extensions"])
        self.out_edit.insert(filepaths["output"])
        if filepaths["overwrite"]:
            self.ow_on.setChecked(True)
        else:
            self.ow_off.setChecked(True)

        header_index = self.header_types.index(header_type.capitalize())

        if "lightcurve" in data_types:
            self.lightcurve.setChecked(True)
        else:
            self.lightcurve.setChecked(False)
        self.header.setCurrentIndex(header_index)

        #Load the unique parameters dictionary into the unique parameters table
        self.loadDictionaries(uniques)

        self.status.setTextColor(Qt.darkGreen)
        self.status.append("Loaded {0}.".format(filename))


    def resetClicked(self, source="clicked"):
        """
        Clear any changes to the form.
        """

        #Confirm the user wants to clear the form, except in the case of a
        #load operation.
        if not source == "load":
            self.reset = ResetConfirm()
            self.reset.exec_()
            if not self.reset.confirm:
                return None

        #Empty the immediately-available elements.
        self.data_edit.clear()
        self.ext_edit.clear()
        self.out_edit.clear()
        self.ow_on.setChecked(True)
        self.header.setCurrentIndex(0)
        self.lightcurve.setChecked(False)
        p_one = self.uniquesgrid.itemAtPosition(self.firstrow,0).widget()
        p_one.setCurrentIndex(0)
        c_one = self.uniquesgrid.itemAtPosition(self.firstrow,1).widget()
        c_one.clear()
        v_one = self.uniquesgrid.itemAtPosition(self.firstrow,2).widget()
        v_one.clear()

        #Delete any unique parameter entries beyond the first table row.
        delete_these = list(reversed(range(self.firstrow+1,
                                           self.uniquesgrid.rowCount())))
        if len(delete_these) > 0:
            for n in delete_these:
                test = self.uniquesgrid.itemAtPosition(n,0)
                if test == None:
                    continue
                self.uniquesgrid.itemAtPosition(n,0).widget().setParent(None)
                self.uniquesgrid.itemAtPosition(n,1).widget().setParent(None)
                self.uniquesgrid.itemAtPosition(n,2).widget().setParent(None)
        self.nextrow = self.firstrow + 1

        if not source == "load":
            self.status.setTextColor(Qt.black)
            self.status.append("Form reset.")


    def collectInputs(self):
        """
        Assemble everything the user has input to the form into a dictionary.
        Then write that dictionary into a yaml file.
        """

        config = {}

        #Create the filepaths section of the dictionary from the edit boxes
        #and overwrite flag.
        filepaths = {}

        hlsppath = self.data_edit.text()
        if hlsppath == "":
            self.status.setTextColor(Qt.red)
            self.status.append("HLSP Data file path is missing!")
            return None
        else:
            filepaths["hlsppath"] = hlsppath

        extensions = self.ext_edit.text()
        if extensions == "":
            self.status.setTextColor(Qt.red)
            self.status.append("Extensions file path is missing!")
            return None
        #extensions table must end with .csv
        if not extensions.endswith(".csv"):
            extensions += ".csv"
        filepaths["extensions"] = extensions

        out = self.out_edit.text()
        if out == "":
            self.status.setTextColor(Qt.red)
            self.status.append("Output file path is missing!")
            return None
        #output file must end with .xml
        if not out.endswith(".xml"):
            out += ".xml"
        filepaths["output"] = out
        filepaths["overwrite"] = self.ow_on.isChecked()
        config["filepaths"] = filepaths

        #Grab the selected fits header type.
        config["header_type"] = self.header.currentText().lower()

        #Collect all selected data type flags.
        data_types = []
        lc = self.lightcurve.checkState()
        if lc > 0:
            data_types.append("lightcurve")
        config["data_types"] = data_types

        #Collect all the unique parameters the user has entered.  Start at row
        #self.firstrow and search through all rows the user may have added.
        uniques = {}
        for row in range(self.firstrow, self.uniquesgrid.rowCount()):
            add_parent = self.uniquesgrid.itemAtPosition(row, 0)
            add_caom = self.uniquesgrid.itemAtPosition(row, 1)
            add_value = self.uniquesgrid.itemAtPosition(row, 2)
            unique_parent = None
            unique_caom = None
            unique_value = None

            #Skip totally empty rows, empty values are okay for defining a new
            #parent.
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
            if unique_parent =="" and unique_caom =="" and unique_value =="":
                continue
            elif unique_parent == "":
                unique_parent = "CompositeObservation"
            parameter = {}
            parameter[unique_caom] = unique_value
            insert = crawl_dictionary(uniques, unique_parent, parameter)

            #crawl_dictionary returns a tuple: (updated dictionary, inserted
            #boolean flag)
            new_uniques = insert[0]
            inserted = insert[1]
            
            #If crawl_dictionary did not insert the new parameter, the defined
            #parent is not currently present in the dictionary, so create a
            #new entry.
            if not inserted:
                uniques[unique_parent] = parameter
            else:
                uniques = new_uniques
        config["unique_parameters"] = uniques

        #Write the config dictionary into a yaml file using a dialog.
        saveit = QFileDialog.getSaveFileName(self, "Save YAML file", ".")
        if len(saveit[0]) > 0:
            saveit = os.path.abspath(saveit[0])
            if not saveit.endswith(".yaml"):
                saveit += ".yaml"
            with open(saveit, 'w') as output:
                yaml.dump(config, output, default_flow_style=False)
            print("Saved {0}".format(saveit))
            self.status.setTextColor(Qt.darkGreen)
            self.status.append("Saved {0}".format(saveit))
            output.close()
            return saveit


    def genClicked(self):
        """
        When generate is clicked, collect all the user inputs and write the
        yaml file.
        """
        self.collectInputs()


    def runClicked(self):
        """
        When run is clicked, collect all the user inputs, write the yaml file,
        and send the file to hlsp_to_xml.
        """
        config = self.collectInputs()
        if config is not None:
            self.status.setTextColor(Qt.darkGreen)
            self.status.append("Launching hlsp_to_xml.py!")
            self.status.append("See terminal for script output.")
            hlsp_to_xml(config)

#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = ConfigGenerator()
    sys.exit(app.exec_())
