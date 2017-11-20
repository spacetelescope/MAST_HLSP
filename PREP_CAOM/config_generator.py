import os
import sys
import yaml
from hlsp_to_xml import hlsp_to_xml
try:
    from PyQt4.QtWidgets import *
except ModuleNotFoundError:
    from PyQt5.QtWidgets import *

global SIZE
SIZE = 9

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
        self.data_edit = QLineEdit(data)
        ext = QLabel("File Extensions Table: ", fp)
        self.ext_edit = QLineEdit(ext)
        out = QLabel("Output File: ", fp)
        self.out_edit = QLineEdit(out)

        #Overwrite flag is boolean, on by default.
        ow = QLabel("Overwrite: ", self)
        self.ow_on = QRadioButton("On", ow)
        self.ow_on.setChecked(True)
        self.ow_off = QRadioButton("Off", ow)

        #Add all accepted fits header types here.
        ht = QLabel("Header Type: ", self)
        self.header = QComboBox(ht)
        self.header.addItem("Standard")
        self.header.addItem("Kepler")

        #Add all unique data types defined in the static values file here.
        dt = QLabel("Included Data Types: ", self)
        self.lightcurve = QCheckBox("Light Curves", dt)

        #Create custom unique parameters to write into the yaml file.  This
        #list is expandable.  Custom parents can be defined in addition to
        #metadataList and provenance.
        up = QLabel("HLSP-Unique Parameters: ", self)
        self.parent_param = QLabel("Parent:", up)
        caom_param = QLabel("CAOM Keyword:", up)
        value_param = QLabel("Value:", up)
        parent_edit = QComboBox(self.parent_param, editable=True)
        parent_edit.addItem("")
        parent_edit.addItem("metadataList")
        parent_edit.addItem("provenance")
        caom_edit = QLineEdit(caom_param)
        value_edit = QLineEdit(value_param)

        #Three buttons: Add a unique parameter entry, save as yaml file, or
        #save as yaml file and run hlsp_to_xml.
        add_param = QPushButton("Additional Parameter", self)
        gen = QPushButton("Generate YAML File", self)
        gen.setStyleSheet("background-color: #7af442; \
                          border-radius: 4px; \
                          height: 25px")
        gen.resize(200,20)
        run = QPushButton("Generate YAML and Run 'hlsp_to_xml.py'", self)
        run.setStyleSheet("background-color: #42d4f4; \
                          border-radius: 4px; \
                          height: 25px")

        #Create a grid layout and add all the widgets.
        self.grid = QGridLayout()
        self.grid.setSpacing(SIZE)
        self.grid.addWidget(fp, 1, 0)
        self.grid.addWidget(data, 1, 1)
        self.grid.addWidget(self.data_edit, 1, 2, 1, 2)
        self.grid.addWidget(ext, 2, 1)
        self.grid.addWidget(self.ext_edit, 2, 2, 1, 2)
        self.grid.addWidget(out, 3, 1)
        self.grid.addWidget(self.out_edit, 3, 2, 1, 2)
        self.grid.addWidget(ow, 4, 0)
        self.grid.addWidget(self.ow_on, 4, 1)
        self.grid.addWidget(self.ow_off, 4, 2)
        self.grid.addWidget(ht, 5, 0)
        self.grid.addWidget(self.header, 5, 1)
        self.grid.addWidget(dt, 6, 0)
        self.grid.addWidget(self.lightcurve, 6, 1)
        self.grid.addWidget(up, 7, 0)
        self.grid.addWidget(self.parent_param, 7, 1)
        self.grid.addWidget(caom_param, 7, 2)
        self.grid.addWidget(value_param, 7, 3)
        self.grid.addWidget(add_param, 8, 0)
        self.grid.addWidget(parent_edit, 8, 1)
        self.grid.addWidget(caom_edit, 8, 2)
        self.grid.addWidget(value_edit, 8, 3)
        self.grid.addWidget(gen, 9, 0)
        self.grid.addWidget(run, 10, 0)

        #Set the window layout and show it.
        self.setLayout(self.grid)
        self.resize(700,300)
        self.setWindowTitle("ConfigGenerator")
        self.show()

        #Add button actions.
        add_param.clicked.connect(self.addClicked)
        gen.clicked.connect(self.genClicked)
        run.clicked.connect(self.runClicked)

    def addClicked(self):
        """
        Use the global SIZE variable to add a new unique parameter entry row.
        """
        global SIZE
        new_parent = QComboBox(editable=True)
        new_parent.addItem("")
        new_parent.addItem("metadataList")
        new_parent.addItem("provenance")
        new_caom = QLineEdit()
        new_value = QLineEdit()
        self.grid.addWidget(new_parent, SIZE, 1)
        self.grid.addWidget(new_caom, SIZE, 2)
        self.grid.addWidget(new_value, SIZE, 3)
        SIZE += 1

    def collectInputs(self):
        """
        Assemble everything the user has input to the form into a dictionary.
        Then write that dictionary into a yaml file.
        """

        config = {}

        #Create the filepaths section of the dictionary from the edit boxes
        #and overwrite flag.
        filepaths = {}
        filepaths["hlsppath"] = self.data_edit.text()
        extensions = self.ext_edit.text()
        #extensions table must end with .csv
        if not extensions.endswith(".csv"):
            extensions += ".csv"
        filepaths["extensions"] = extensions
        out = self.out_edit.text()
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
        begin_row = 8
        uniques = {}
        for row in range(begin_row, self.grid.rowCount()):
            add_parent = self.grid.itemAtPosition(row, 1)
            add_caom = self.grid.itemAtPosition(row, 2)
            add_value = self.grid.itemAtPosition(row, 3)
            unique_parent = None
            unique_caom = None
            unique_value = None
            #Skip totally empty rows, empty values are okay for defining a new
            #parent.
            if add_parent is None and add_caom is None and add_value is None:
                continue
            if add_parent is not None:
                parent_widget = add_parent.widget()
                unique_parent = parent_widget.currentText()
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
            print("Saved {}".format(saveit))
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
        print("Launching hlsp_to_xml.py...")
        hlsp_to_xml(config)

#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = ConfigGenerator()
    sys.exit(app.exec_())
