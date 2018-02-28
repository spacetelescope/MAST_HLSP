"""
..class::  DataTypeBox
    :synopsis:  A subclass of QComboBox to define a desired data type.  Allows
    setting the QComboBox index via string.

..class::  ProductTypeBox
    :synopsis:  A subclass of QComboBox to define a desired product data type.
    Allows setting the QComboBox index via string.

..class::  ClearConfirm
    :synopsis:  Creates a PyQt popup window with a yes/no confirmation dialog.
    Used before clearing changes made to the form.

..class::  ExtGenerator
    :synopsis:  Creates a PyQt widget that allows a user to define data file
    types with various PyQt tools.  These data definitions tell
    ../hlsp_to_xml.py what HLSP data files to look for while browsing a given
    directory.  This information is saved into a .csv table and passed along
    to ../hlsp_to_xml.py via a .yaml config file.  The user can add additional
    rows, load an existing .csv file into the form, save the contents of the
    form to a new .csv file, or clear all changes made to the form.
"""

import csv
import gui.GUIbuttons as gb
import os
import sys
from util.read_yaml import read_yaml
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

#--------------------

class ProductTypeBox(QComboBox):
    """
    Create a subclass of QComboBox to contain Product Type options.
    """
    def __init__(self):
        super().__init__()
        self.entries = ["SCIENCE", "CALIBRATION", "PREVIEW", "AUXILIARY",
                        "THUMBNAIL", "BIAS", "DARK", "FLAT", "WAVECAL",
                        "NOISE", "WEIGHT", "INFO", "CATALOG"]
        for item in self.entries:
            self.addItem(item)

    def setCurrentType(self, ctype):
        if ctype in self.entries:
            index = self.entries.index(ctype)
        return QComboBox.setCurrentIndex(self, index)

#--------------------

class ClearConfirm(QDialog):
    """
    Pop up a confirmation dialog window before clearing all changes to the
    form.
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
        self.setWindowTitle("Confirm Clear")
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

class SelectFiles(QWidget):
    """
    Create a GUI to create a CSV table describing files to search for within
    an HLSP directory and some CAOM parameters to apply to them.  This table
    is necessary to run hlsp_to_xml.py.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        #Add buttons to create a new file entry row, clear all entries in the
        #table, load an existing .csv file, or write the current contents to a
        #new .csv file.
        select_all = gb.GreyButton("Select All", 20, 175)
        de_all = gb.GreyButton("Deselect All", 20, 175)
        add_file = gb.GreyButton("+ add another file type", 20, 175)
        self.clear = gb.GreyButton("- clear table", 20, 175)
        load = gb.GreyButton("Load File", 40)
        self.save = gb.GreenButton("Select these types", 40)
        empty = QSpacerItem(200, 1)
        self.buttonsgrid = QGridLayout()
        self.buttonsgrid.addWidget(select_all, 0, 0)
        self.buttonsgrid.addWidget(de_all, 1, 0)
        self.buttonsgrid.addWidget(add_file, 0, 1)
        self.buttonsgrid.addWidget(self.clear, 1, 1)
        self.buttonsgrid.addItem(empty, 0, 2)
        #self.buttonsgrid.addWidget(load, 0, 3, 2, 1)
        self.buttonsgrid.addWidget(self.save, 0, 4, 2, 2)

        ext_label = QLabel("File ends with:")
        ext_label.setToolTip("Provide a distinctive filename ending to search for within this HLSP ('_img.fits')")
        dt_label = QLabel("Data Type:")
        pt_label = QLabel("Product Type:")
        sel_label = QLabel("Select:")
        self.ext_edit = QLineEdit()
        self.pt_box = ProductTypeBox()
        self.sel_box = QCheckBox()
        self.sel_box.setChecked(True)
        self.firstrow = 1
        self.nextrow = 2
        self.filetypegrid = QGridLayout()
        self.filetypegrid.addWidget(sel_label, 0, 0)
        self.filetypegrid.addWidget(ext_label, 0, 1)
        self.filetypegrid.addWidget(pt_label, 0, 2)
        self.filetypegrid.addWidget(self.sel_box, 1, 0)
        self.filetypegrid.addWidget(self.ext_edit, 1, 1)
        self.filetypegrid.addWidget(self.pt_box, 1, 2)
        self.filetypegrid.setRowStretch(self.nextrow, 0)
        self.filetypegrid.setRowStretch(self.nextrow+1, 1)

        res_label = QLabel("Output:")
        res_label.setAlignment(Qt.AlignHCenter)
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setLineWrapMode(QTextEdit.NoWrap)
        self.status.setStyleSheet("border-style: solid; \
                                  border-width: 1px; \
                                  background: rgba(235,235,235,0%);")
        self.outputgrid = QGridLayout()
        self.outputgrid.addWidget(res_label, 0, 0)
        self.outputgrid.addWidget(self.status, 1, 0)

        self.grid = QGridLayout()
        self.grid.addLayout(self.buttonsgrid, 0, 0, 1, -1)
        self.grid.addLayout(self.filetypegrid, 1, 0)
        #self.grid.addLayout(self.outputgrid, 1, 1)

        self.selected_files = []

        self.setLayout(self.grid)
        self.show()

        self.sel_box.stateChanged.connect(self.selectClicked)
        select_all.clicked.connect(self.sallClicked)
        de_all.clicked.connect(self.dallClicked)
        add_file.clicked.connect(self.newFileClicked)
        self.clear.clicked.connect(self.clearClicked)
        #load.clicked.connect(self.loadFromYAMLClicked)
        self.save.clicked.connect(self.saveClicked)


    def sallClicked(self):
        for n in range(self.firstrow, self.nextrow):
            selected = self.filetypegrid.itemAtPosition(n, 0).widget()
            selected.setChecked(True)


    def dallClicked(self):
        for n in range(self.firstrow, self.nextrow):
            selected = self.filetypegrid.itemAtPosition(n, 0).widget()
            selected.setChecked(False)


    def selectClicked(self, state):
        sender = self.sender()
        ind = self.filetypegrid.indexOf(sender)
        pos = self.filetypegrid.getItemPosition(ind)
        row = pos[0]
        f = self.filetypegrid.itemAtPosition(row, 1).widget()
        pt = self.filetypegrid.itemAtPosition(row, 2).widget()
        if state == Qt.Checked:
            f.setStyleSheet("")
            pt.setVisible(True)
        else:
            f.setStyleSheet("color: DarkGrey; background-color: WhiteSmoke")
            pt.setVisible(False)


    def newFileClicked(self):
        """
        When 'add_file' is clicked, create a new row with the same file entry
        options as the first row.
        """

        new_ext = QLineEdit()
        new_pt = ProductTypeBox()
        new_sel = QCheckBox()
        new_sel.setChecked(True)
        new_sel.stateChanged.connect(self.selectClicked)
        self.filetypegrid.addWidget(new_sel, self.nextrow, 0)
        self.filetypegrid.addWidget(new_ext, self.nextrow, 1)
        self.filetypegrid.addWidget(new_pt, self.nextrow, 2)
        self.filetypegrid.setRowStretch(self.nextrow, 0)
        self.filetypegrid.setRowStretch(self.nextrow+1, 1)
        self.nextrow += 1


    def clearClicked(self, source="clicked"):
        """
        Clear any changes made to the form and reset to original state.
        """

        """
        #Pop up a confirmation dialog if this is not being called from the load
        #function.
        if not source == "load":
            self.cc = ClearConfirm()
            self.cc.exec_()
            if not self.cc.confirm:
                return None
        """

        #Empty the items in the first row but don't delete them.
        sel_one = self.filetypegrid.itemAtPosition(self.firstrow,0).widget()
        sel_one.setChecked(False)
        p_one = self.filetypegrid.itemAtPosition(self.firstrow,1).widget()
        p_one.clear()
        pt_one = self.filetypegrid.itemAtPosition(self.firstrow,2).widget()
        pt_one.setCurrentIndex(0)

        #Remove all elements beyond the first row.
        delete_these = list(reversed(range(self.firstrow+1,
                                           self.filetypegrid.rowCount()-1)))
        if len(delete_these) > 1:
            for n in delete_these:
                test = self.filetypegrid.itemAtPosition(n,0)
                if test == None:
                    continue
                self.filetypegrid.itemAtPosition(n,0).widget().setParent(None)
                self.filetypegrid.itemAtPosition(n,1).widget().setParent(None)
                self.filetypegrid.itemAtPosition(n,2).widget().setParent(None)
        self.nextrow = self.firstrow + 1

        """
        if not source == "load":
            self.status.setTextColor(Qt.black)
            self.status.append("Table cleared.")
        """


    def loadExtensionsYAML(self, filename):
        """
        Open an existing YAML file and load the contents into the form.
        """

        #Read the YAML contents into a list.
        files = {}
        file_config = read_yaml(filename)
        for ext in sorted(file_config.keys()):
            if isinstance(file_config[ext], list):
                for product in file_config[ext]:
                    ending = product['FileEnding']
                    prod_type = product['FileParams']['ProductType']
                    if prod_type == "null":
                        files[ending] = ""
                    else:
                        files[ending] = prod_type

        #Check that there are any data types to insert.
        if len(files.keys()) == 0:
            self.status.setTextColor(Qt.red)
            self.status.append("No data rows in {0}".format(filename))
            return None

        #Clear any changes already made to the form.
        self.clearClicked(source="load")

        #Begin at the first data row and insert values into the form elements.
        #(skip the CSV header row)
        row_num = self.firstrow
        for entry in sorted(files.keys()):
            ext_box = self.filetypegrid.itemAtPosition(row_num, 1)
            if ext_box is None:
                self.newFileClicked()
            sel_box = self.filetypegrid.itemAtPosition(row_num, 0).widget()
            ext_box = self.filetypegrid.itemAtPosition(row_num, 1).widget()
            pt_box = self.filetypegrid.itemAtPosition(row_num, 2).widget()
            sel_box.setChecked(True)
            ext_box.setText(entry)
            if files[entry] is not None:
                pt_box.setCurrentType(files[entry])
            row_num += 1
        self.status.setTextColor(Qt.darkGreen)
        self.status.append("Loaded {0}".format(filename))

    def loadConfigYAML(self, filename):
        """
        Open an existing YAML file and load the contents into the form.
        """

        #Read the YAML contents into a list.
        files = {}
        file_config = read_yaml(filename)
        files = file_config["file_types"]

        #Check that there are any data types to insert.
        if len(files.keys()) == 0:
            self.status.setTextColor(Qt.red)
            self.status.append("No data rows in {0}".format(filename))
            return None

        #Clear any changes already made to the form.
        self.clearClicked(source="load")

        #Begin at the first data row and insert values into the form elements.
        #(skip the CSV header row)
        row_num = self.firstrow
        for entry in sorted(files.keys()):
            ext_box = self.filetypegrid.itemAtPosition(row_num, 1)
            if ext_box is None:
                self.newFileClicked()
            sel_box = self.filetypegrid.itemAtPosition(row_num, 0).widget()
            ext_box = self.filetypegrid.itemAtPosition(row_num, 1).widget()
            pt_box = self.filetypegrid.itemAtPosition(row_num, 2).widget()
            sel_box.setChecked(True)
            ext_box.setText(entry)
            if files[entry] is not None:
                pt_box.setCurrentType(files[entry])
            row_num += 1
        self.status.setTextColor(Qt.darkGreen)
        self.status.append("Loaded {0}".format(filename))


    def saveClicked(self):
        """
        When 'save' is clicked, collect all the user entries and write the
        CSV file.
        """

        self.selected_files = {}

        #Loop over all rows the user might have created in the form.
        for row in range(self.firstrow, self.filetypegrid.rowCount()):
            add_sel = self.filetypegrid.itemAtPosition(row, 0)
            add_ext = self.filetypegrid.itemAtPosition(row, 1)
            add_pt = self.filetypegrid.itemAtPosition(row, 2)
            read_ext = None
            read_pt = None
            read_sel = None

            #Skip any empty rows (might not be possible/necessary)
            if add_ext is None:
                continue

            #Read the entries from the current row.  Skip if there is no text
            #in the file extension entry.
            sel_widget = add_sel.widget()
            read_sel = sel_widget.checkState()
            if read_sel == 0:
                continue
            ext_widget = add_ext.widget()
            read_ext = str(ext_widget.text())
            if read_ext == "":
                continue
            pt_widget = add_pt.widget()
            read_pt = pt_widget.currentText().upper()

            as_tuple = (read_ext, read_pt)
            self.selected_files[read_ext] = read_pt

        #If all file entry rows have empty name entries, button takes no action
        if len(self.selected_files) == 0:
            self.status.setTextColor(Qt.red)
            self.status.append("No file types to save!")
            return None

        return self.selected_files

#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = SelectFiles()
    sys.exit(app.exec_())
