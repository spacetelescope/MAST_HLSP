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

class ExtGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        add_file = QPushButton("+ add another file type")
        add_file.setStyleSheet("""
                                QPushButton {
                                    background-color: #dddddd;
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
        self.dt_label = QLabel("Data Type:")
        self.pt_label = QLabel("Product Type:")
        self.req_label = QLabel("Required:")

        self.ext_edit = QLineEdit()
        self.dt_box = QComboBox()
        self.dt_box.addItem("Image")
        self.dt_box.addItem("Sepctrum")
        self.dt_box.addItem("TimeSeries")
        self.dt_box.addItem("Visibility")
        self.dt_box.addItem("EventList")
        self.dt_box.addItem("Cube")
        self.dt_box.addItem("Catalog")
        self.dt_box.addItem("Measurements")
        self.pt_box = QComboBox()
        self.pt_box.addItem("Science")
        self.pt_box.addItem("Calibration")
        self.pt_box.addItem("Preview")
        self.pt_box.addItem("Auxiliary")
        self.pt_box.addItem("Thumbnail")
        self.pt_box.addItem("Bias")
        self.pt_box.addItem("Dark")
        self.pt_box.addItem("Flat")
        self.pt_box.addItem("WaveCal")
        self.pt_box.addItem("Noise")
        self.pt_box.addItem("Weight")
        self.pt_box.addItem("Info")
        self.pt_box.addItem("Catalog")
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
        global EXTSIZE
        new_ext = QLineEdit()
        new_dt = QComboBox()
        new_dt.addItem("Image")
        new_dt.addItem("Sepctrum")
        new_dt.addItem("TimeSeries")
        new_dt.addItem("Visibility")
        new_dt.addItem("EventList")
        new_dt.addItem("Cube")
        new_dt.addItem("Catalog")
        new_dt.addItem("Measurements")
        new_pt = QComboBox()
        new_pt.addItem("Science")
        new_pt.addItem("Calibration")
        new_pt.addItem("Preview")
        new_pt.addItem("Auxiliary")
        new_pt.addItem("Thumbnail")
        new_pt.addItem("Bias")
        new_pt.addItem("Dark")
        new_pt.addItem("Flat")
        new_pt.addItem("WaveCal")
        new_pt.addItem("Noise")
        new_pt.addItem("Weight")
        new_pt.addItem("Info")
        new_pt.addItem("Catalog")
        new_req = QCheckBox()
        self.grid.addWidget(new_ext, EXTSIZE, 0)
        self.grid.addWidget(new_dt, EXTSIZE, 1)
        self.grid.addWidget(new_pt, EXTSIZE, 2)
        self.grid.addWidget(new_req, EXTSIZE, 3)
        self.grid.setRowStretch(EXTSIZE, 0)
        self.grid.setRowStretch(EXTSIZE+1, 1)
        EXTSIZE += 1

    def saveClicked(self):
        begin_row = 2
        all_files = []
        for row in range(begin_row, self.grid.rowCount()):
            add_ext = self.grid.itemAtPosition(row, 0)
            add_dt = self.grid.itemAtPosition(row, 1)
            add_pt = self.grid.itemAtPosition(row, 2)
            add_req = self.grid.itemAtPosition(row, 3)
            read_ext = None
            read_dt = None
            read_pt = None
            read_req = None
            #Skip totally empty rows, empty values are okay for defining a new
            #parent.
            if add_ext is None:
                continue

            ext_widget = add_ext.widget()
            read_ext = str(ext_widget.text())
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
            line = ",".join(as_tuple)
            all_files.append(as_tuple)

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
