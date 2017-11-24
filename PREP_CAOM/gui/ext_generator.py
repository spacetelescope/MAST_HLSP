import csv
import os
import sys
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

global FIRST_ENTRY
FIRST_ENTRY = 3
global NEXT_ENTRY
NEXT_ENTRY = FIRST_ENTRY + 1

#--------------------

class DataTypeBox(QComboBox):
    """
    Create a subclass of QComboBox to contain Data Type options.
    """
    def __init__(self):
        super().__init__()
        self.entries = ["IMAGE", "SPECTRUM", "TIMESERIES", "VISIBILITY",
                        "EVENTLIST", "CUBE", "CATALOG", "MEASUREMENTS"]
        for item in self.entries:
            self.addItem(item)

    def setCurrentType(self, ctype):
        if ctype in self.entries:
            index = self.entries.index(ctype)
        return QComboBox.setCurrentIndex(self, index)

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

        #Add buttons to create a new file entry row and to launch the CSV file
        #creation
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

        self.ext_label = QLabel("File ends with:")
        self.ext_label.setToolTip("Provide a distinctive filename ending to search for within this HLSP ('_img.fits')")
        self.dt_label = QLabel("Data Type:")
        self.pt_label = QLabel("Product Type:")
        self.req_label = QLabel("Required:")
        self.res_label = QLabel("Results:")
        self.res_label.setAlignment(Qt.AlignHCenter)

        self.ext_edit = QLineEdit()
        self.dt_box = DataTypeBox()
        self.pt_box = ProductTypeBox()
        self.req_box = QCheckBox()
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setLineWrapMode(QTextEdit.NoWrap)
        self.status.setStyleSheet("border-style: solid; \
                                  border-width: 1px; \
                                  background: rgba(235,235,235,0%);")

        self.grid = QGridLayout()
        self.grid.setRowStretch(NEXT_ENTRY, 2)
        self.grid.addWidget(add_file, 0, 0)
        self.grid.addWidget(clear, 1, 0)
        self.grid.addWidget(load, 0, 2, 2, 1)
        self.grid.addWidget(save, 0, 3, 2, 2)
        self.grid.addWidget(self.ext_label, 2, 0)
        self.grid.addWidget(self.dt_label, 2, 1)
        self.grid.addWidget(self.pt_label, 2, 2)
        self.grid.addWidget(self.req_label, 2, 3)
        self.grid.addWidget(self.res_label, 2, 4)
        self.grid.addWidget(self.ext_edit, 3, 0)
        self.grid.addWidget(self.dt_box, 3, 1)
        self.grid.addWidget(self.pt_box, 3, 2)
        self.grid.addWidget(self.req_box, 3, 3)
        self.grid.addWidget(self.status, 3, 4, -1, 1)

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
        global NEXT_ENTRY
        new_ext = QLineEdit()
        new_dt = DataTypeBox()
        new_pt = ProductTypeBox()
        new_req = QCheckBox()
        self.grid.addWidget(new_ext, NEXT_ENTRY, 0)
        self.grid.addWidget(new_dt, NEXT_ENTRY, 1)
        self.grid.addWidget(new_pt, NEXT_ENTRY, 2)
        self.grid.addWidget(new_req, NEXT_ENTRY, 3)
        self.grid.setRowStretch(NEXT_ENTRY, 0)
        self.grid.setRowStretch(NEXT_ENTRY+1, 1)
        self.setLayout(self.grid)
        self.show()
        NEXT_ENTRY += 1

    def clearClicked(self):
        global FIRST_ENTRY
        global NEXT_ENTRY
        delete_these = list(reversed(range(FIRST_ENTRY+1,
                                           self.grid.rowCount()-1)))
        if len(delete_these) > 1:
            for n in delete_these:
                test = self.grid.itemAtPosition(n,0)
                if test == None:
                    continue
                self.grid.itemAtPosition(n,0).widget().setParent(None)
                self.grid.itemAtPosition(n,1).widget().setParent(None)
                self.grid.itemAtPosition(n,2).widget().setParent(None)
                self.grid.itemAtPosition(n,3).widget().setParent(None)
        NEXT_ENTRY = FIRST_ENTRY+1
        self.status.setTextColor(Qt.black)
        self.status.append("Table cleared.")

    def loadClicked(self):
        global FIRST_ENTRY
        global NEXT_ENTRY
        loadit = QFileDialog.getOpenFileName(self, "Load a CSV file", ".")
        filename = loadit[0]
        if not filename.endswith(".csv"):
            self.status.setTextColor(Qt.red)
            self.status.append("{0} is not a .csv file!".format(filename))
            return None
        files = []
        with open(filename, 'r') as csvfile:
            read = csv.reader(csvfile)
            for row in read:
                files.append(row)
            csvfile.close()
        if len(files) <= 1:
            self.status.setTextColor(Qt.red)
            self.status.append("No data rows in {0}".format(filename))
            return None

        self.clearClicked()

        row_num = FIRST_ENTRY
        for entry in files[1:]:
            ext_box = self.grid.itemAtPosition(row_num, 0)
            if ext_box is None:
                self.newFileClicked()
            ext_box = self.grid.itemAtPosition(row_num, 0)
            dt_box = self.grid.itemAtPosition(row_num, 1)
            pt_box = self.grid.itemAtPosition(row_num, 2)
            req_box = self.grid.itemAtPosition(row_num, 3)
            ext_widget = ext_box.widget()
            dt_widget = dt_box.widget()
            pt_widget = pt_box.widget()
            req_widget = req_box.widget()
            ext_widget.setText(entry[0])
            dt_widget.setCurrentType(entry[1])
            pt_widget.setCurrentType(entry[2])
            if entry[3] == "REQUIRED":
                req_widget.setChecked(True)
            else:
                req_widget.setChecked(False)
            row_num += 1
        self.status.setTextColor(Qt.darkGreen)
        self.status.append("Loaded {0}".format(filename))

    def saveClicked(self):
        """
        When 'save' is clicked, collect all the user entries and write the
        CSV file.
        """
        global FIRST_ENTRY
        all_files = []

        #Loop over all rows the user might have created in the form.
        for row in range(FIRST_ENTRY, self.grid.rowCount()):
            add_ext = self.grid.itemAtPosition(row, 0)
            add_dt = self.grid.itemAtPosition(row, 1)
            add_pt = self.grid.itemAtPosition(row, 2)
            add_req = self.grid.itemAtPosition(row, 3)
            read_ext = None
            read_dt = None
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
            dt_widget = add_dt.widget()
            read_dt = dt_widget.currentText().upper()
            pt_widget = add_pt.widget()
            read_pt = pt_widget.currentText().upper()
            req_widget = add_req.widget()
            read_req = req_widget.checkState()
            if read_req > 0:
                read_req = "REQUIRED"
            else:
                read_req = "OPTIONAL"
            as_tuple = (read_ext, read_dt, read_pt, read_req)
            all_files.append(as_tuple)

        #If all file entry rows have empty name entries, button takes no action
        if len(all_files) == 0:
            self.status.setTextColor(Qt.red)
            self.status.append("No file types to save!")
            return None

        #Create a header row, get a name to save the file, and write all
        #content to the CSV file.
        head = ("extension", "dataProductType", "productType", "fileStatus")
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
