"""
..class::  ProductTypeBox
    :synopsis:  A subclass of QComboBox to define a desired product data type.
    Allows setting the QComboBox index via string.

..class::  SelectFiles
    :synopsis:  Creates a PyQt widget that allows a user to define data file
    types with various PyQt tools.  These data definitions tell
    ../hlsp_to_xml.py what HLSP data files to look for while browsing a given
    directory.  This information is saved into a .csv table and passed along
    to ../hlsp_to_xml.py via a .yaml config file.  The user can add additional
    rows, load an existing .csv file into the form, save the contents of the
    form to a new .csv file, or clear all changes made to the form.
"""

import csv
import os
import sys

import lib.GUIbuttons as gb
from lib.ClearConfirm import ClearConfirm
from lib.MyError import MyError

from util.read_yaml import read_yaml

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

#--------------------

class ProductTypeBox(QComboBox):
    """ Create a subclass of QComboBox to contain Product Type options.
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

class SelectFiles(QWidget):
    """ Create a GUI to create a CSV table describing files to search for
    within an HLSP directory and some CAOM parameters to apply to them.  This
    table is necessary to run hlsp_to_xml.py.
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # Set two variables to track the beginning and end of the file entry
        # table, since it has a variable number of rows
        self.firstrow = 1
        self.nextrow = 2

        # Define a list variable to track selected files
        self.selected_files = []

        self.error = None
        self.message = None

        # Add buttons to create a new file entry row, clear all entries in the
        # table, load an existing .csv file, or write the current contents to a
        # new .csv file.
        select_all = gb.GreyButton("Select All", 20, 175)
        de_all = gb.GreyButton("Deselect All", 20, 175)
        add_file = gb.GreyButton("+ add another file type", 20, 175)
        self.clear = gb.GreyButton("- clear table", 20, 175)
        self.save = gb.GreenButton("Select these types", 40)
        empty = QSpacerItem(100, 1)
        self.buttonsgrid = QGridLayout()
        self.buttonsgrid.addWidget(select_all, 0, 0)
        self.buttonsgrid.addWidget(de_all, 1, 0)
        self.buttonsgrid.addWidget(add_file, 0, 1)
        self.buttonsgrid.addWidget(self.clear, 1, 1)
        self.buttonsgrid.addItem(empty, 0, 2)
        self.buttonsgrid.addWidget(self.save, 0, 3, 2, 2)

        # Make the widgets and set the layout for the file extensions entry
        # portion of the window
        ext_label = QLabel("File ends with:")
        ext_label.setToolTip("Provide a distinctive filename ending to search for within this HLSP ('_img.fits')")
        dt_label = QLabel("Data Type:")
        pt_label = QLabel("Product Type:")
        sel_label = QLabel("Select:")
        self.ext_edit = QLineEdit()
        self.pt_box = ProductTypeBox()
        self.sel_box = QCheckBox()
        self.sel_box.setChecked(True)
        self.filetypegrid = QGridLayout()
        self.filetypegrid.addWidget(sel_label, 0, 0)
        self.filetypegrid.addWidget(ext_label, 0, 1)
        self.filetypegrid.addWidget(pt_label, 0, 2)
        self.filetypegrid.addWidget(self.sel_box, 1, 0)
        self.filetypegrid.addWidget(self.ext_edit, 1, 1)
        self.filetypegrid.addWidget(self.pt_box, 1, 2)
        self.filetypegrid.setRowStretch(self.nextrow, 0)
        self.filetypegrid.setRowStretch(self.nextrow+1, 1)

        """
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
        """

        # Add the sub-layouts to the window layout
        self.grid = QGridLayout()
        self.grid.addLayout(self.buttonsgrid, 0, 0, 1, -1)
        self.grid.addLayout(self.filetypegrid, 1, 0)
        #self.grid.addLayout(self.outputgrid, 1, 1)

        self.setLayout(self.grid)
        self.show()

        # Connect all buttons
        self.sel_box.stateChanged.connect(self.selectBoxClicked)
        select_all.clicked.connect(self.selectAllClicked)
        de_all.clicked.connect(self.deselectAllClicked)
        add_file.clicked.connect(self.newFileClicked)
        self.clear.clicked.connect(self.clearClicked)
        self.save.clicked.connect(self.saveClicked)


    def selectAllClicked(self):
        """ Set all file entries from firstrow to nextrow as selected.
        """

        for n in range(self.firstrow, self.nextrow):
            selected = self.filetypegrid.itemAtPosition(n, 0).widget()
            selected.setChecked(True)


    def deselectAllClicked(self):
        """ Set all file entries from firstrow to nextrow as unselected.
        """

        for n in range(self.firstrow, self.nextrow):
            selected = self.filetypegrid.itemAtPosition(n, 0).widget()
            selected.setChecked(False)


    def selectBoxClicked(self, state):
        """ Toggle visibility of file type rows when the select box is clicked.
        """

        # Many select boxes connect to this module, so need to determine which
        # is sending the signal
        sender = self.sender()
        ind = self.filetypegrid.indexOf(sender)
        pos = self.filetypegrid.getItemPosition(ind)
        row = pos[0]
        f = self.filetypegrid.itemAtPosition(row, 1).widget()
        pt = self.filetypegrid.itemAtPosition(row, 2).widget()

        # Toggle visibility based on check box state
        if state == Qt.Checked:
            f.setStyleSheet("")
            pt.setVisible(True)
        else:
            f.setStyleSheet("color: DarkGrey; background-color: WhiteSmoke")
            pt.setVisible(False)


    def newFileClicked(self):
        """ When 'add_file' is clicked, create a new row with the same file
        entry options as the first row.  Create this new row at the nextrow
        position and advance the nextrow tracker.
        """

        # Create new widgets
        new_ext = QLineEdit()
        new_pt = ProductTypeBox()
        new_sel = QCheckBox()

        # Set to selected by default and connect to the select box toggle
        # module
        new_sel.setChecked(True)
        new_sel.stateChanged.connect(self.selectBoxClicked)

        # Add new widgets to the filetypegrid layout
        self.filetypegrid.addWidget(new_sel, self.nextrow, 0)
        self.filetypegrid.addWidget(new_ext, self.nextrow, 1)
        self.filetypegrid.addWidget(new_pt, self.nextrow, 2)

        # Set stretch properties so rows are kept evenly spaced
        self.filetypegrid.setRowStretch(self.nextrow, 0)
        self.filetypegrid.setRowStretch(self.nextrow+1, 1)

        # Advance nextrow
        self.nextrow += 1


    def clearClicked(self, source):
        """ Clear any changes made to the form and reset to original state.
        """

        #Pop up a confirmation dialog if this is not being called from the load
        #function.
        if not source:
            self.cc = ClearConfirm("Clear all file type entries?")
            self.cc.exec_()
            if not self.cc.confirm:
                return None

        #Empty the items in the first row but don't delete them.
        sel_one = self.filetypegrid.itemAtPosition(self.firstrow,0).widget()
        sel_one.setChecked(False)
        p_one = self.filetypegrid.itemAtPosition(self.firstrow,1).widget()
        p_one.clear()
        pt_one = self.filetypegrid.itemAtPosition(self.firstrow,2).widget()
        pt_one.setCurrentIndex(0)

        #Remove all elements beyond the first row.
        delete_these = list(reversed(range(self.firstrow+1,
                                           self.nextrow)))
        if len(delete_these) > 1:
            for n in delete_these:
                test = self.filetypegrid.itemAtPosition(n,0)
                if test == None:
                    continue
                self.filetypegrid.itemAtPosition(n,0).widget().setParent(None)
                self.filetypegrid.itemAtPosition(n,1).widget().setParent(None)
                self.filetypegrid.itemAtPosition(n,2).widget().setParent(None)
        self.nextrow = self.firstrow + 1

    def loadExtensionsYAML(self, filename):
        """ Open an existing YAML file and load the contents into the form.
        """

        #Read the YAML contents into a list.
        files = {}
        file_config = read_yaml(filename)
        if isinstance(file_config, str):
            raise MyError(file_config)
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
            raise MyError("No 'FileEnding' rows in {0}".format(filename))

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
        self.message = "Loaded {0}".format(filename)

    def loadConfigYAML(self, filename):
        """
        Open an existing YAML file and load the contents into the form.
        """

        #Read the YAML contents into a list.
        files = {}
        file_config = read_yaml(filename)
        if isinstance(file_config, str):
            raise MyError(file_config)
        try:
            files = file_config["file_types"]
        except KeyError:
            #self.error = "'file_types' not defined in .config file!"
            raise MyError("'file_types' not defined in .config file!")
            return None

        #Check that there are any data types to insert.
        if len(files.keys()) == 0:
            self.error = "No data rows in {0}".format(filename)
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

        return file_config

    def collectSelectedFiles(self):
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
            self.error = "No file types to save!"
            return None

        return self.selected_files

    def saveClicked(self):
        selection = self.collectSelectedFiles()
        return selection

#--------------------

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = SelectFiles()
    sys.exit(app.exec_())
