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
        else:
            raise MyError("{0} is not a valid productType!".format(ctype))

#--------------------

class SelectFiles(QWidget):
    """ Create a GUI to create a CSV table describing files to search for
    within an HLSP directory and some CAOM parameters to apply to them.  This
    table is necessary to run hlsp_to_xml.py.
    """

    # Make a signal for launch_gui to collect selected file types on any
    # check box toggle.
    select_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # Set two variables to track the beginning and end of the file entry
        # table, since it has a variable number of rows
        self.firstrow = 1
        self.nextrow = self.firstrow + 1

        # Define a list variable to track selected files
        self.selected_files = {}

        self.error = None
        self.message = None

        # Add buttons to create a new file entry row, clear all entries in the
        # table, load an existing .csv file, or write the current contents to a
        # new .csv file.
        b_height = 20
        b_width = 160
        select_all = gb.GreyButton("Select All", b_height, b_width)
        deselect_all = gb.GreyButton("Deselect All", b_height, b_width)
        add_type = gb.GreyButton("+ Add Another File Type", b_height, b_width)
        self.clear = gb.GreyButton("- Clear Table", b_height, b_width)
        self.buttons_grid = QGridLayout()
        self.buttons_grid.addWidget(select_all, 0, 0)
        self.buttons_grid.addWidget(deselect_all, 0, 1)
        self.buttons_grid.addWidget(add_type, 0, 2)
        self.buttons_grid.addWidget(self.clear, 0, 3)

        # Make the widgets and set the layout for the file extensions entry
        # portion of the window
        filetype_label = QLabel("File ends with:")
        filetype_label.setToolTip(("Provide a distinctive filename ending to "
                                   "search for within this HLSP ('_img.fits')")
                                  )
        producttype_label = QLabel("Product Type:")
        select_label = QLabel("Select:")
        filetype_edit = QLineEdit()
        producttype_box = ProductTypeBox()
        select_box = QCheckBox()
        select_box.setChecked(True)
        self.filetypes_grid = QGridLayout()
        self.filetypes_grid.addWidget(select_label, 0, 0)
        self.filetypes_grid.addWidget(filetype_label, 0, 1)
        self.filetypes_grid.addWidget(producttype_label, 0, 2)
        self.filetypes_grid.addWidget(select_box, 1, 0)
        self.filetypes_grid.addWidget(filetype_edit, 1, 1)
        self.filetypes_grid.addWidget(producttype_box, 1, 2)
        self.filetypes_grid.setRowStretch(self.nextrow, 0)
        self.filetypes_grid.setRowStretch(self.nextrow+1, 1)

        # Add the sub-layouts to the window layout
        self.meta_grid = QGridLayout()
        self.meta_grid.addLayout(self.buttons_grid, 0, 0, 1, -1)
        self.meta_grid.addLayout(self.filetypes_grid, 1, 0)

        self.setLayout(self.meta_grid)
        self.show()

        # Connect all buttons
        select_box.stateChanged.connect(self.selectBoxClicked)
        select_all.clicked.connect(self.selectAllClicked)
        deselect_all.clicked.connect(self.deselectAllClicked)
        add_type.clicked.connect(self.newFileClicked)
        self.clear.clicked.connect(self.clearClicked)

    def selectAllClicked(self):
        """ Set all file entries from firstrow to nextrow as selected.
        """

        for n in range(self.firstrow, self.nextrow):
            selected = self.filetypes_grid.itemAtPosition(n, 0).widget()
            selected.setChecked(True)

    def deselectAllClicked(self):
        """ Set all file entries from firstrow to nextrow as unselected.
        """

        for n in range(self.firstrow, self.nextrow):
            selected = self.filetypes_grid.itemAtPosition(n, 0).widget()
            selected.setChecked(False)

    def selectBoxClicked(self, state):
        """ Toggle visibility of file type rows when the select box is clicked.
        """

        # Many select boxes connect to this module, so need to determine which
        # is sending the signal
        sender = self.sender()
        ind = self.filetypes_grid.indexOf(sender)
        pos = self.filetypes_grid.getItemPosition(ind)
        row = pos[0]
        fe = self.filetypes_grid.itemAtPosition(row, 1).widget()
        file_extension = fe.text()
        pt = self.filetypes_grid.itemAtPosition(row, 2).widget()
        product_type = pt.currentText()

        # Toggle visibility based on check box state
        if state == Qt.Checked:
            fe.setStyleSheet("")
            pt.setVisible(True)
            if (file_extension in self.selected_files.keys()
                or file_extension == ""):
                pass
            else:
                self.selected_files[file_extension] = product_type
        else:
            fe.setStyleSheet("color: DarkGrey; background-color: WhiteSmoke")
            pt.setVisible(False)
            if (file_extension in self.selected_files.keys()
                and file_extension != ""):
                del self.selected_files[file_extension]
            else:
                pass

        # Emit a select_signal so launch_gui will update the list of selected
        # files
        self.select_signal.emit()


    def newFileClicked(self):
        """ When 'add_type' is clicked, create a new row with the same file
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

        # Add new widgets to the filetypes_grid layout
        self.filetypes_grid.addWidget(new_sel, self.nextrow, 0)
        self.filetypes_grid.addWidget(new_ext, self.nextrow, 1)
        self.filetypes_grid.addWidget(new_pt, self.nextrow, 2)

        # Set stretch properties so rows are kept evenly spaced
        self.filetypes_grid.setRowStretch(self.nextrow, 0)
        self.filetypes_grid.setRowStretch(self.nextrow+1, 1)

        # Advance nextrow
        self.nextrow += 1

    def clearClicked(self, source):
        """ Clear any changes made to the form and reset to original state.
        """

        # Pop up a confirmation dialog if this is not being called from the
        # load function.
        if not source:
            self.cc = ClearConfirm("Clear all file type entries?")
            self.cc.exec_()
            if not self.cc.confirm:
                return

        # Empty the items in the first row but don't delete them.
        sel_one = self.filetypes_grid.itemAtPosition(self.firstrow,0).widget()
        sel_one.setChecked(False)
        p_one = self.filetypes_grid.itemAtPosition(self.firstrow,1).widget()
        p_one.clear()
        pt_one = self.filetypes_grid.itemAtPosition(self.firstrow,2).widget()
        pt_one.setCurrentIndex(0)

        # Remove all elements beyond the first row.
        delete_these = list(reversed(range(self.firstrow+1,
                                           self.nextrow)))
        if len(delete_these) > 0:
            for x in delete_these:
                test = self.filetypes_grid.itemAtPosition(x,0)
                if test is None:
                    continue
                widgets_per_row = 3
                for y in range(widgets_per_row):
                    z = self.filetypes_grid.itemAtPosition(x,y).widget()
                    z.setParent(None)

        # Reset the nextrow variable.
        self.nextrow = self.firstrow + 1

        # Clear the selected_files dictionary and emit a signal to refresh
        # the launch_gui list
        self.selected_files = {}
        self.select_signal.emit()

    def loadFromYaml(origin_function):
        """ Provide a wrapper function for the two methods of loading file
        type information to this form.  This code is common to both methods
        and covers reading the YAML file to a dictionary, and inserting data
        into widget elements.
        """

        def wrapper(s, **kwargs):

            # Read the YAML contents into a dictionary.
            filename = kwargs['filename']
            file_config = read_yaml(filename)

            # If file_config is a string, this is error text.
            if isinstance(file_config, str):
                raise MyError(file_config)

            # Translate the file_config dictionary to a standardized
            # dictionary ready to be inserted in the form.
            kwargs['file_config'] = file_config
            files = origin_function(s,
                                    filename=filename,
                                    file_config=file_config
                                   )

            #Clear any changes already made to the form.
            s.clearClicked(source="load")

            # Begin at the first data row and insert values into the form
            # elements.
            row_num = s.firstrow
            for entry in sorted(files.keys()):

                # If this row item does not exist, trigger a new row creation.
                ext_box = s.filetypes_grid.itemAtPosition(row_num, 1)
                if ext_box is None:
                    s.newFileClicked()

                # Get all widgets in the row.
                sel_box = s.filetypes_grid.itemAtPosition(row_num, 0).widget()
                ext_box = s.filetypes_grid.itemAtPosition(row_num, 1).widget()
                pt_box = s.filetypes_grid.itemAtPosition(row_num, 2).widget()

                # Insert file type parameters to the widgets.
                sel_box.setChecked(True)
                ext_box.setText(entry)
                if files[entry] is not None:
                    try:
                        pt_box.setCurrentType(files[entry])
                    except MyError as err:
                        raise MyError(err.message)

                # Move to the next row.
                row_num += 1

            return file_config
        return wrapper

    @loadFromYaml
    def loadExtensionsYAML(self, **kwargs):
        """ Open a YAML file sent from HLSP metadata checking and get just the
        parameters we need.
        """

        files = {}
        filename = kwargs['filename']
        file_config = kwargs['file_config']

        # For each extension listed in file_config, create a FileEnding:
        # CAOMProductType pair in the files dictionary.
        for ext in sorted(file_config.keys()):

            # Not every file_config entry will be a list
            if isinstance(file_config[ext], list):
                for product in file_config[ext]:
                    try:
                        ending = product['FileEnding']
                    except KeyError:
                        msg = "'FileEnding' not found in .param file"
                        raise MyError(msg)

                    try:
                        params = product['FileParams']
                    except KeyError:
                        msg = "'FileParams' not found in .param file"
                        raise MyError(msg)

                    try:
                        prod_type = params['CAOMProductType']
                    except KeyError:
                        msg = "'CAOMProductType' not found in .param file"
                        raise MyError(msg)

                    if prod_type == "null":
                        files[ending] = ""
                    else:
                        files[ending] = prod_type.upper()

        # Check that there are any data types to insert.
        if len(files.keys()) == 0:
            raise MyError("No 'FileEnding' rows in {0}".format(filename))

        # The files dictionary can now be read by the loadFromYaml wrapper and
        # inserted into GUI widgets.
        return files

    @loadFromYaml
    def loadConfigYAML(self, **kwargs):
        """ Open an existing full YAML config file and pull out the
        'file_types' dictionary.
        """

        files = {}
        filename = kwargs['filename']
        file_config = kwargs['file_config']

        # Get the 'file_types' dictionary.
        try:
            files = file_config["file_types"]
        except KeyError:
            raise MyError("'file_types' not defined in .config file!")
            return None

        # Check that there are any data types to insert.
        if len(files.keys()) == 0:
            self.error = "No data rows in {0}".format(filename)
            return None

        # The files dictionary can now be read by the loadFromYaml wrapper and
        # inserted into GUI widgets.
        return files

    def collectSelectedFiles(self):
        """ When 'save' is clicked, collect all the user entries and write the
        CSV file.
        """

        # Loop over all rows the user might have created in the form.
        for row in range(self.firstrow, self.nextrow):
            additional_select = self.filetypes_grid.itemAtPosition(row, 0)
            additional_extension = self.filetypes_grid.itemAtPosition(row, 1)
            additional_producttype = self.filetypes_grid.itemAtPosition(row, 2)

            # Skip any empty rows (might not be possible/necessary)
            if additional_extension is None:
                continue

            # Check the select box first, if that is not checked then skip to
            # next row.
            select_widget = additional_select.widget()
            read_select = select_widget.checkState()
            if read_select == 0:
                continue

            # Read in the provided file extension, skip to next row if empty.
            extension_widget = additional_extension.widget()
            read_extension = str(extension_widget.text())
            if read_extension == "":
                continue

            # Read in the product type selection (can't be empty).
            producttype_widget = additional_producttype.widget()
            read_producttype = producttype_widget.currentText().upper()

            as_tuple = (read_extension, read_producttype)
            self.selected_files[read_extension] = read_producttype

        # If all file entry rows have empty name entries, button takes no
        # action
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
