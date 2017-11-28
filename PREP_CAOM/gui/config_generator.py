import os
import sys
import yaml
from hlsp_to_xml import hlsp_to_xml
from util.read_yaml import read_yaml
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

#Define the first row for the unique parameters table.
global FIRST_ENTRY
FIRST_ENTRY = 9
#Keep track of where to add a new unique parameter entry
global NEXT_ENTRY
NEXT_ENTRY = FIRST_ENTRY+1

#--------------------

def crawl_dictionary(dictionary, parent, parameter, inserted=False):
    """
    Recursively look for a given parent within a potential dictionary of
    dictionaries.  If the parent is found, insert the new parameter and update
    the 'inserted' flag.  Return both the updated dictionary and inserted flag.
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
        self.confirm = True
        self.close()

    def noClicked(self):
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
        #Filepaths sections contains filepath entry boxes.  May want to make
        #these required.
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

        #Overwrite flag is boolean, on by default.
        ow = QLabel("Overwrite: ", self)
        ow.setToolTip("Allow hlsp_to_xml.py to overwrite an existing XML file.")
        self.ow_on = QRadioButton("On", ow)
        self.ow_on.setChecked(True)
        self.ow_off = QRadioButton("Off", ow)

        #Add all accepted fits header types here.
        ht = QLabel("Header Type: ", self)
        ht.setToolTip("Select the FITS header type this HLSP uses.")
        self.header = QComboBox(ht)
        self.header_types = ["Standard", "Kepler"]
        for typ in self.header_types:
            self.header.addItem(typ)

        #Add all unique data types defined in the static values file here.
        dt = QLabel("Included Data Types: ", self)
        dt.setToolTip("Add special CAOM parameters for various data types.")
        self.lightcurve = QCheckBox("Light Curves", dt)

        #Create custom unique parameters to write into the yaml file.  This
        #list is expandable.  Custom parents can be defined in addition to
        #metadataList and provenance.
        up = QLabel("HLSP-Unique Parameters: ", self)
        up.setToolTip("Define additional CAOM parameters to insert that are not defined in the FITS headers.")
        self.parent_param = QLabel("Parent:", up)
        self.parent_param.setAlignment(Qt.AlignHCenter)
        caom_param = QLabel("CAOM Keyword:", up)
        caom_param.setAlignment(Qt.AlignHCenter)
        value_param = QLabel("Value:", up)
        value_param.setAlignment(Qt.AlignHCenter)
        parent_edit = QComboBox(self.parent_param, editable=True)
        self.xml_parents = ["", "metadataList", "provenance"]
        for p in self.xml_parents:
            parent_edit.addItem(p)
        caom_edit = QLineEdit(caom_param)
        value_edit = QLineEdit(value_param)

        status_label = QLabel("Results:")
        status_label.setAlignment(Qt.AlignHCenter)
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setLineWrapMode(QTextEdit.NoWrap)
        self.status.setStyleSheet("border-style: solid; \
                                  border-width: 1px; \
                                  background: rgba(235,235,235,0%);")

        #Three buttons: Add a unique parameter entry, save as yaml file, or
        #save as yaml file and run hlsp_to_xml.
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
        load.setMinimumWidth(125)
        reset = QPushButton("Reset Form")
        reset.setStyleSheet("""
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
        reset.setMinimumWidth(125)
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

        #Create a grid layout and add all the widgets.
        self.grid2 = QGridLayout()
        self.grid2.setSpacing(FIRST_ENTRY)
        self.grid2.setColumnStretch(1, 1)
        self.grid2.setColumnStretch(2, 1)
        self.grid2.setColumnStretch(3, 0)
        self.grid2.setColumnStretch(4, 2)
        self.grid2.setRowStretch(NEXT_ENTRY, 2)
        self.grid2.addWidget(fp, 0, 0)
        self.grid2.addWidget(load, 0, 3, 2, 1)
        self.grid2.addWidget(gen, 0, 4, 2, 1)
        self.grid2.addWidget(data, 1, 0)
        self.grid2.addWidget(self.data_edit, 1, 1, 1, 2)
        self.grid2.addWidget(reset, 2, 3, 2, 1)
        self.grid2.addWidget(run, 2, 4, 2, 1)
        self.grid2.addWidget(ext, 2, 0)
        self.grid2.addWidget(self.ext_edit, 2, 1, 1, 2)
        self.grid2.addWidget(out, 3, 0)
        self.grid2.addWidget(self.out_edit, 3, 1, 1, 2)
        self.grid2.addWidget(ow, 4, 0)
        self.grid2.addWidget(self.ow_on, 4, 1)
        self.grid2.addWidget(self.ow_off, 4, 2)
        self.grid2.addWidget(status_label, 4, 3, 1, 2)
        self.grid2.addWidget(self.status, 5, 3, -1, 2)
        self.grid2.addWidget(ht, 5, 0)
        self.grid2.addWidget(self.header, 5, 1)
        self.grid2.addWidget(dt, 6, 0)
        self.grid2.addWidget(self.lightcurve, 6, 1)
        self.grid2.addWidget(up, 7, 0)
        self.grid2.addWidget(add_param, 7, 1)
        self.grid2.addWidget(self.parent_param, 8, 0)
        self.grid2.addWidget(caom_param, 8, 1)
        self.grid2.addWidget(value_param, 8, 2)
        self.grid2.addWidget(parent_edit, 9, 0)
        self.grid2.addWidget(caom_edit, 9, 1)
        self.grid2.addWidget(value_edit, 9, 2)

        #Set the window layout and show it.
        self.setLayout(self.grid2)
        self.show()

        #Add button actions.
        add_param.clicked.connect(self.addClicked)
        load.clicked.connect(self.loadClicked)
        reset.clicked.connect(self.resetClicked)
        gen.clicked.connect(self.genClicked)
        run.clicked.connect(self.runClicked)


    def addClicked(self):
        """
        Use the global NEXT_ENTRY variable to add a new unique parameter
        entry row.
        """
        global NEXT_ENTRY
        new_parent = QComboBox(editable=True)
        for p in self.xml_parents:
            new_parent.addItem(p)
        new_caom = QLineEdit()
        new_value = QLineEdit()
        self.grid2.addWidget(new_parent, NEXT_ENTRY, 0)
        self.grid2.addWidget(new_caom, NEXT_ENTRY, 1)
        self.grid2.addWidget(new_value, NEXT_ENTRY, 2)
        self.grid2.setRowStretch(NEXT_ENTRY, 0)
        self.grid2.setRowStretch(NEXT_ENTRY+1, 1)
        NEXT_ENTRY += 1


    def loadDictionaries(self, uniques):
        """
        Recursively handles loading multi-level dictionaries to the unique
        parameters table.
        """

        global FIRST_ENTRY
        global NEXT_ENTRY

        parents = uniques.keys()
        for p in parents:
            sub_dictionary = uniques[p]

            #Look at the first row to see if you're loading into FIRST_ENTRY
            #or NEXT_ENTRY.
            first_parent = self.grid2.itemAtPosition(FIRST_ENTRY,0).widget()
            for param in sub_dictionary.keys():
                if first_parent.currentText() == "":
                    row = FIRST_ENTRY
                else:
                    row = NEXT_ENTRY
                    self.addClicked()

                #Get the Parent combo box for the current row.
                parent_box = self.grid2.itemAtPosition(row,0).widget()

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
                caom_box = self.grid2.itemAtPosition(row,1).widget()
                caom_box.insert(param)

                #If the next level is still a dictionary, repeat this process.
                #Otherwise, fill in the Value line edit box.
                if isinstance(sub_dictionary[param], dict):
                    self.loadDictionaries(sub_dictionary)
                else:
                    value_box = self.grid2.itemAtPosition(row,2).widget()
                    value_box.insert(sub_dictionary[param])


    def loadClicked(self):
        """
        Open a user-selected YAML file and load the elements into the form.
        """

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

        global FIRST_ENTRY
        global NEXT_ENTRY

        #Confirm the user wants to clear the form, except in the case of a
        #load operation.
        if not source == "load":
            self.reset = ResetConfirm()
            self.reset.exec_()
            if not self.reset.confirm:
                return None

        self.data_edit.clear()
        self.ext_edit.clear()
        self.out_edit.clear()
        self.ow_on.setChecked(True)
        self.header.setCurrentIndex(0)
        self.lightcurve.setChecked(False)
        self.grid2.itemAtPosition(FIRST_ENTRY,0).widget().setCurrentIndex(0)
        self.grid2.itemAtPosition(FIRST_ENTRY,1).widget().clear()
        self.grid2.itemAtPosition(FIRST_ENTRY,2).widget().clear()

        #Delete any unique parameter entries beyond the first table row.
        delete_these = list(reversed(range(FIRST_ENTRY+1,
                                           self.grid2.rowCount())))
        if len(delete_these) > 0:
            for n in delete_these:
                test = self.grid2.itemAtPosition(n,0)
                if test == None:
                    continue
                self.grid2.itemAtPosition(n,0).widget().setParent(None)
                self.grid2.itemAtPosition(n,1).widget().setParent(None)
                self.grid2.itemAtPosition(n,2).widget().setParent(None)
        NEXT_ENTRY = FIRST_ENTRY+1
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
        #8 and search through all rows the user may have added.
        uniques = {}
        for row in range(FIRST_ENTRY, self.grid2.rowCount()):
            add_parent = self.grid2.itemAtPosition(row, 0)
            add_caom = self.grid2.itemAtPosition(row, 1)
            add_value = self.grid2.itemAtPosition(row, 2)
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
