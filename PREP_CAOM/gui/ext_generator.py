import csv
import os
import sys
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

global EXTSIZE
EXTSIZE = 3

#--------------------

class DataTypeBox(QComboBox):
    """
    Create a subclass of QComboBox to contain Data Type options.
    """
    def __init__(self):
        super().__init__()
        self.addItem("Image")
        self.addItem("Sepctrum")
        self.addItem("TimeSeries")
        self.addItem("Visibility")
        self.addItem("EventList")
        self.addItem("Cube")
        self.addItem("Catalog")
        self.addItem("Measurements")

#--------------------

class ProductTypeBox(QComboBox):
    """
    Create a subclass of QComboBox to contain Product Type options.
    """
    def __init__(self):
        super().__init__()
        self.addItem("Science")
        self.addItem("Calibration")
        self.addItem("Preview")
        self.addItem("Auxiliary")
        self.addItem("Thumbnail")
        self.addItem("Bias")
        self.addItem("Dark")
        self.addItem("Flat")
        self.addItem("WaveCal")
        self.addItem("Noise")
        self.addItem("Weight")
        self.addItem("Info")
        self.addItem("Catalog")

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
        add_file.setMaximumWidth(200)
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

        self.ext_edit = QLineEdit()
        self.dt_box = DataTypeBox()
        self.pt_box = ProductTypeBox()
        self.req_box = QCheckBox()

        self.grid = QGridLayout()
        self.grid.setRowStretch(EXTSIZE, 2)
        self.grid.addWidget(add_file, 0, 0)
        self.grid.addWidget(save, 0, 1, 1, 3)
        self.grid.addWidget(self.ext_label, 1, 0)
        self.grid.addWidget(self.dt_label, 1, 1)
        self.grid.addWidget(self.pt_label, 1, 2)
        self.grid.addWidget(self.req_label, 1, 3)
        self.grid.addWidget(self.ext_edit, 2, 0)
        self.grid.addWidget(self.dt_box, 2, 1)
        self.grid.addWidget(self.pt_box, 2, 2)
        self.grid.addWidget(self.req_box, 2, 3)

        self.setLayout(self.grid)
        self.show()

        add_file.clicked.connect(self.newFileClicked)
        save.clicked.connect(self.saveClicked)

    def newFileClicked(self):
        """
        When 'add_file' is clicked, create a new row with the same file entry
        options as the first row.
        """
        global EXTSIZE
        new_ext = QLineEdit()
        new_dt = DataTypeBox()
        new_pt = ProductTypeBox()
        new_req = QCheckBox()
        self.grid.addWidget(new_ext, EXTSIZE, 0)
        self.grid.addWidget(new_dt, EXTSIZE, 1)
        self.grid.addWidget(new_pt, EXTSIZE, 2)
        self.grid.addWidget(new_req, EXTSIZE, 3)
        self.grid.setRowStretch(EXTSIZE, 0)
        self.grid.setRowStretch(EXTSIZE+1, 1)
        EXTSIZE += 1

    def saveClicked(self):
        """
        When 'save' is clicked, collect all the user entries and write the
        CSV file.
        """
        begin_row = 2
        all_files = []

        #Loop over all rows the user might have created in the form.
        for row in range(begin_row, self.grid.rowCount()):
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
            output.close()
            return saveit
