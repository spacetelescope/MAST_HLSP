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
import os
import sys
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

class ExtGenerator(QWidget):
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
        add_file = QPushButton("+ add another file type")
        add_file.setStyleSheet("""
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
        add_file.setMaximumWidth(175)
        clear = QPushButton("- clear table")
        clear.setStyleSheet("""
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
        clear.setMaximumWidth(175)
        load = QPushButton("Load File")
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
        save = QPushButton("Save To .csv File", self)
        save.setStyleSheet("""
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
        empty = QSpacerItem(200, 1)
        self.buttonsgrid = QGridLayout()
        self.buttonsgrid.addWidget(add_file, 0, 0)
        self.buttonsgrid.addWidget(clear, 1, 0)
        self.buttonsgrid.addItem(empty, 0, 1)
        self.buttonsgrid.addWidget(load, 0, 2, 2, 1)
        self.buttonsgrid.addWidget(save, 0, 3, 2, 2)

        ext_label = QLabel("File ends with:")
        ext_label.setToolTip("Provide a distinctive filename ending to search for within this HLSP ('_img.fits')")
        dt_label = QLabel("Data Type:")
        pt_label = QLabel("Product Type:")
        req_label = QLabel("Required:")
        self.ext_edit = QLineEdit()
        self.pt_box = ProductTypeBox()
        self.req_box = QCheckBox()
        self.firstrow = 1
        self.nextrow = 2
        self.filetypegrid = QGridLayout()
        self.filetypegrid.addWidget(ext_label, 0, 0)
        self.filetypegrid.addWidget(pt_label, 0, 1)
        self.filetypegrid.addWidget(req_label, 0, 2)
        self.filetypegrid.addWidget(self.ext_edit, 1, 0)
        self.filetypegrid.addWidget(self.pt_box, 1, 1)
        self.filetypegrid.addWidget(self.req_box, 1, 2)

        res_label = QLabel("Results:")
        res_label.setAlignment(Qt.AlignHCenter)
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setLineWrapMode(QTextEdit.NoWrap)
        self.status.setStyleSheet("border-style: solid; \
                                  border-width: 1px; \
                                  background: rgba(235,235,235,0%);")

        self.grid = QGridLayout()
        self.grid.addLayout(self.buttonsgrid, 0, 0)
        self.grid.addLayout(self.filetypegrid, 1, 0)
        self.grid.addWidget(res_label, 2, 0)
        self.grid.addWidget(self.status)

        self.setLayout(self.grid)
        self.show()

        add_file.clicked.connect(self.newFileClicked)
        clear.clicked.connect(self.clearClicked)
        load.clicked.connect(self.loadClicked)
        save.clicked.connect(self.saveClicked)


    def newFileClicked(self):
        """
        When 'add_file' is clicked, create a new row with the same file entry
        options as the first row.
        """

        new_ext = QLineEdit()
        new_pt = ProductTypeBox()
        new_req = QCheckBox()
        self.filetypegrid.addWidget(new_ext, self.nextrow, 0)
        self.filetypegrid.addWidget(new_pt, self.nextrow, 1)
        self.filetypegrid.addWidget(new_req, self.nextrow, 2)
        self.filetypegrid.setRowStretch(self.nextrow, 0)
        self.filetypegrid.setRowStretch(self.nextrow+1, 1)
        self.nextrow += 1


    def clearClicked(self, source="clicked"):
        """
        Clear any changes made to the form and reset to original state.
        """

        #Pop up a confirmation dialog if this is not being called from the load
        #function.
        if not source == "load":
            self.cc = ClearConfirm()
            self.cc.exec_()
            if not self.cc.confirm:
                return None

        #Empty the items in the first row but don't delete them.
        p_one = self.filetypegrid.itemAtPosition(self.firstrow,0).widget()
        p_one.clear()
        pt_one = self.filetypegrid.itemAtPosition(self.firstrow,1).widget()
        pt_one.setCurrentIndex(0)
        req_one = self.filetypegrid.itemAtPosition(self.firstrow,2).widget()
        req_one.setChecked(False)

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

        if not source == "load":
            self.status.setTextColor(Qt.black)
            self.status.append("Table cleared.")


    def loadClicked(self):
        """
        Open an existing CSV file and load the contents into the form.
        """

        loadit = QFileDialog.getOpenFileName(self, "Load a CSV file", ".")
        filename = loadit[0]

        #Check the filename, but from a dialog so we expect it to exist.
        if filename == "":
            return None
        elif not filename.endswith(".csv"):
            self.status.setTextColor(Qt.red)
            self.status.append("{0} is not a .csv file!".format(filename))
            return None

        #Read the CSV contents into a list.
        files = []
        with open(filename, 'r') as csvfile:
            read = csv.reader(csvfile)
            for row in read:
                files.append(row)
            csvfile.close()

        #Check that there are any data types to insert.
        if len(files) <= 1:
            self.status.setTextColor(Qt.red)
            self.status.append("No data rows in {0}".format(filename))
            return None

        #Check the CSV header row and make sure it has the right data.
        header = files[0]
        try:
            ext_index = header.index("extension")
            pt_index = header.index("productType")
            req_index = header.index("fileStatus")
        except ValueError:
            self.status.setTextColor(Qt.red)
            self.status.append("Could not read {0}".format(filename))
            return None

        #Clear any changes already made to the form.
        self.clearClicked(source="load")

        #Begin at the first data row and insert values into the form elements.
        #(skip the CSV header row)
        row_num = self.firstrow
        for entry in files[1:]:
            ext_box = self.filetypegrid.itemAtPosition(row_num, 0)
            if ext_box is None:
                self.newFileClicked()
            ext_box = self.filetypegrid.itemAtPosition(row_num, 0).widget()
            pt_box = self.filetypegrid.itemAtPosition(row_num, 1).widget()
            req_box = self.filetypegrid.itemAtPosition(row_num, 2).widget()
            ext_box.setText(entry[ext_index])
            pt_box.setCurrentType(entry[pt_index])
            if entry[req_index] == "REQUIRED":
                req_box.setChecked(True)
            else:
                req_box.setChecked(False)
            row_num += 1
        self.status.setTextColor(Qt.darkGreen)
        self.status.append("Loaded {0}".format(filename))


    def saveClicked(self):
        """
        When 'save' is clicked, collect all the user entries and write the
        CSV file.
        """

        all_files = []

        #Loop over all rows the user might have created in the form.
        for row in range(self.firstrow, self.filetypegrid.rowCount()):
            add_ext = self.filetypegrid.itemAtPosition(row, 0)
            add_pt = self.filetypegrid.itemAtPosition(row, 1)
            add_req = self.filetypegrid.itemAtPosition(row, 2)
            read_ext = None
            read_pt = None
            read_req = None

            #Skip any empty rows (might not be possible/necessary)
            if add_ext is None:
                continue

            #Read the entries from the current row.  Skip if there is no text
            #in the file extension entry.
            ext_widget = add_ext.widget()
            read_ext = str(ext_widget.text())
            if read_ext == "":
                continue
            pt_widget = add_pt.widget()
            read_pt = pt_widget.currentText().upper()
            req_widget = add_req.widget()
            read_req = req_widget.checkState()
            if read_req > 0:
                read_req = "REQUIRED"
            else:
                read_req = "OPTIONAL"
            as_tuple = (read_ext, read_pt, read_req)
            all_files.append(as_tuple)

        #If all file entry rows have empty name entries, button takes no action
        if len(all_files) == 0:
            self.status.setTextColor(Qt.red)
            self.status.append("No file types to save!")
            return None

        #Create a header row, get a name to save the file, and write all
        #content to the CSV file.
        head = ("extension", "productType", "fileStatus")
        saveit = QFileDialog.getSaveFileName(self, "Save CSV file", ".")
        if len(saveit[0]) > 0:
            saveit = os.path.abspath(saveit[0])
            if not saveit.endswith(".csv"):
                saveit += ".csv"
            with open(saveit, 'w') as output:
                writer = csv.writer(output)
                writer.writerow(head)
                writer.writerows(all_files)
            print("Saved {0}".format(saveit))
            self.status.setTextColor(Qt.darkGreen)
            self.status.append("Saved {0}".format(saveit))
            output.close()
            return saveit
