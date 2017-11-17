import os
import sys
import yaml
from hlsp_to_xml import hlsp_to_xml
from  PyQt5.QtWidgets import *

global SIZE
SIZE = 9

def crawl_dictionary(dictionary, parent, parameter, inserted=False):
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

class ConfigGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        fp = QLabel("Filepaths:", self)
        data = QLabel("HLSP Data: ", fp)
        self.data_edit = QLineEdit(data)
        ext = QLabel("File Extensions Table: ", fp)
        self.ext_edit = QLineEdit(ext)
        out = QLabel("Output File: ", fp)
        self.out_edit = QLineEdit(out)

        ow = QLabel("Overwrite: ", self)
        self.ow_on = QRadioButton("On", ow)
        self.ow_on.setChecked(True)
        self.ow_off = QRadioButton("Off", ow)

        ht = QLabel("Header Type: ", self)
        self.header = QComboBox(ht)
        self.header.addItem("Standard")
        self.header.addItem("Kepler")

        dt = QLabel("Included Data Types: ", self)
        self.lightcurve = QCheckBox("Light Curves", dt)

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

        self.setLayout(self.grid)
        self.resize(700,300)
        self.setWindowTitle("ConfigGenerator")
        self.show()

        add_param.clicked.connect(self.addClicked)
        gen.clicked.connect(self.genClicked)
        run.clicked.connect(self.runClicked)

    def addClicked(self):
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
        config = {}
        filepaths = {}
        filepaths["hlsppath"] = self.data_edit.text()
        filepaths["extensions"] = self.ext_edit.text()
        out = self.out_edit.text()
        if not out.endswith(".xml"):
            out += ".xml"
        filepaths["output"] = out
        filepaths["overwrite"] = self.ow_on.isChecked()
        config["filepaths"] = filepaths

        config["header_type"] = self.header.currentText().lower()

        data_types = []
        lc = self.lightcurve.checkState()
        if lc > 0:
            data_types.append("lightcurve")
        config["data_types"] = data_types

        begin_row = 8
        uniques = {}
        for row in range(begin_row, self.grid.rowCount()):
            add_parent = self.grid.itemAtPosition(row, 1)
            add_caom = self.grid.itemAtPosition(row, 2)
            add_value = self.grid.itemAtPosition(row, 3)
            unique_parent = None
            unique_caom = None
            unique_value = None
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
            new_uniques = insert[0]
            inserted = insert[1]
            if not inserted:
                uniques[unique_parent] = parameter
            else:
                uniques = new_uniques
        config["unique_parameters"] = uniques

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
        self.collectInputs()

    def runClicked(self):
        config = self.collectInputs()
        print("Launching hlsp_to_xml.py...")
        hlsp_to_xml(config)

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = ConfigGenerator()
    sys.exit(app.exec_())
