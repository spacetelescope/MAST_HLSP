"""
.. module:: select_data_templates_gui
    :synopsis: Defines the GUI used by select_data_templates.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------

import logging
import os
import sys
import numpy
import yaml

from get_filetypes_keys import get_filetypes_keys

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    import PyQt5.QtWidgets as QtWidgets
except ImportError:
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import QFont
    import PyQt4.QtWidgets as QtWidgets

# Define allowed template types, file types, and product types.
TEMPLATE_TYPES_FILE = "allowed_template_types.dat"
FILE_TYPES_FILE = "allowed_file_types.dat"
PRODUCT_TYPES_FILE = "allowed_product_types.dat"
CAOMPRODUCT_TYPES_FILE = "allowed_caomproduct_types.dat"

#--------------------

def read_allowed_template_types():
    """ Reads in a list of allowed template types from a file on disk. """
    if os.path.isfile(TEMPLATE_TYPES_FILE):
        with open(TEMPLATE_TYPES_FILE, 'r') as at_file:
            return list(set([x.strip() for x in at_file.readlines()]))
    else:
        raise OSError('Allowed Template Types file not found.  Looking for "' +
                      TEMPLATE_TYPES_FILE + '".')

#--------------------

def read_allowed_file_types():
    """ Reads in a list of allowed file types from a file on disk. """
    if os.path.isfile(FILE_TYPES_FILE):
        with open(FILE_TYPES_FILE, 'r') as ft_file:
            return list(set([x.strip() for x in ft_file.readlines()]))
    else:
        raise OSError('Allowed File Types file not found.  Looking for "' +
                      FILE_TYPES_FILE + '".')

#--------------------

def read_allowed_product_types():
    """ Reads in a list of allowed product types from a file on disk. """
    if os.path.isfile(PRODUCT_TYPES_FILE):
        with open(PRODUCT_TYPES_FILE, 'r') as pt_file:
            return list(set([x.strip() for x in pt_file.readlines()]))
    else:
        raise OSError('Allowed Product Types file not found.  Looking for "' +
                      PRODUCT_TYPES_FILE + '".')

#--------------------

def read_allowed_caomproduct_types():
    """ Reads in a list of allowed caomproduct types from a file on disk. """
    if os.path.isfile(CAOMPRODUCT_TYPES_FILE):
        with open(CAOMPRODUCT_TYPES_FILE, 'r') as cpt_file:
            return list(set([x.strip() for x in cpt_file.readlines()]))
    else:
        raise OSError('Allowed CAOM Product Types file not found.  Looking for'
                      ' "' + CAOMPRODUCT_TYPES_FILE + '".')

#--------------------

class SelectDataTemplatesGUI(QtWidgets.QWidget):
    """
    This class builds a pyqt GUI for defining templates and data format types
        of HLSP files to check with check_data_format.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def get_yaml_index(self, ending):
        """
        Gets the index to use in the YAML data object for the given ending.

        :param ending: The file ending, e.g., 'llc.fits' or 'spec.tar.gz'.

        :type ending: str

        :returns: int -- The index to use inside the YAML object.
        """

        # This line extracts the keys from the list of dicts in param_data.
        # Note that this assumes each entry has a single key that is the file
        # ending.  If the structure of the parameter file changes, this will
        # have to be updated as well.
        file_ending_list = numpy.asarray(
            get_filetypes_keys(self.param_data['FileTypes']))
        index = numpy.where(file_ending_list == ending)[0]

        if len(index) == 1:
            return index
        else:
            raise ValueError("Multiple entries with the same FileEnding"
                             " found.")

    def update_yaml_value(self, ending, update_key, update_value):
        """
        Updates a value in the YAML data object.

        :param ending: The file ending, e.g., 'llc.fits' or 'spec.tar.gz'.

        :type ending: str

        :param update_key: The key to update with the update_value in the
            YAML data object.

        :type update_key: str

        :param update_value: The value to update with in the YAML data object.

        :type update_value: str or bool
        """

        index = self.get_yaml_index(ending)
        self.param_data['FileTypes'][index[0]][ending][update_key] = (
            update_value)

    def set_default_standard(self, widget, ending):
        """
        Selects an appropriate default choice for the Template Standard
            drop-down.  Keep previous saved values if present.

        :param widget: The widget containing the drop-down box.

        :type widget: (PyQt).QtWidgets.QComboBox

        :param ending: The file ending, e.g., 'llc.fits' or 'spec.tar.gz'.

        :type ending: str
        """
        index = self.get_yaml_index(ending)
        cur_value = self.param_data['FileTypes'][index[0]][ending]['Standard']
        if cur_value is not None:
            widget.setCurrentIndex(widget.findText(cur_value))
        else:
            # Default for first run through is everything set to none.
            widget.setCurrentIndex(widget.findText('none'))
            self.update_yaml_value(ending, 'Standard', None)

    def set_default_product_type(self, widget, ending):
        """
        Selects an appropriate default choice for the Template Product
            Type drop-down.  Keep previous saved values if present.

        :param widget: The widget containing the drop-down box.

        :type widget: (PyQt).QtWidgets.QComboBox

        :param ending: The file ending, e.g., 'llc.fits' or 'spec.tar.gz'.

        :type ending: str
        """

        index = self.get_yaml_index(ending)
        cur_value = self.param_data['FileTypes'][index[0]][ending]['ProductType']
        if cur_value is not None:
            widget.setCurrentIndex(widget.findText(cur_value))
        else:
            # Default for first run through is everything set to none.
            widget.setCurrentIndex(widget.findText('none'))
            self.update_yaml_value(ending, 'ProductType', None)

    def set_default_file_type(self, widget, ending):
        """
        Selects an appropriate default choice for the File Type drop-down based
            on the extension.

        :param widget: The widget containing the drop-down box.

        :type widget: (PyQt).QtWidgets.QComboBox

        :param ending: The file ending, e.g., 'llc.fits' or 'spec.tar.gz'.

        :type ending: str
        """

        index = self.get_yaml_index(ending)
        cur_value = self.param_data['FileTypes'][index[0]][ending]['FileType']
        if cur_value is not None:
            widget.setCurrentIndex(widget.findText(cur_value))
        else:
            # Note: This will ignore the zipped part of the ending if gzipped.
            exten = ending.rstrip('.gz').split('.')[-1]
            if exten == 'fits':
                widget.setCurrentIndex(widget.findText("fits"))
                self.update_yaml_value(ending, "FileType", "fits")
            elif exten == 'png':
                widget.setCurrentIndex(widget.findText("graphic"))
                self.update_yaml_value(ending, "FileType", "graphic")
            elif exten == 'tiff':
                widget.setCurrentIndex(widget.findText("graphic"))
                self.update_yaml_value(ending, "FileType", "graphic")
            elif exten == 'jpg':
                widget.setCurrentIndex(widget.findText("graphic"))
                self.update_yaml_value(ending, "FileType", "graphic")
            elif exten == 'jpeg':
                widget.setCurrentIndex(widget.findText("graphic"))
                self.update_yaml_value(ending, "FileType", "graphic")
            elif exten == 'txt':
                widget.setCurrentIndex(widget.findText("text"))
                self.update_yaml_value(ending, "FileType", "text")
            else:
                widget.setCurrentIndex(widget.findText('none'))
                self.update_yaml_value(ending, "FileType", None)

    def set_default_runcheck(self, widget, ending):
        """
        Selects an appropriate default choice for the checkbox to run HLSP format
            checking or not.  Keep previous saved values if present.

        :param widget: The widget containing the checkbox.

        :type widget: (PyQt).QtWidgets.QCheckBox

        :param ending: The file ending, e.g., 'llc.fits' or 'spec.tar.gz'.

        :type ending: str
        """

        index = self.get_yaml_index(ending)
        cur_value = self.param_data['FileTypes'][index[0]][ending]['RunCheck']
        if cur_value is not None:
            widget.setChecked(cur_value)
        else:
            # Note: This will ignore the zipped part of the ending if gzipped.
            exten = ending.rstrip('.gz').split('.')[-1]
            # Default for the first run through depends on file extension.
            if (exten == 'png' or exten == 'tiff' or exten == 'jpg' or
                    exten == 'jpeg'):
                widget.setChecked(False)
                self.update_yaml_value(ending, 'RunCheck', False)
            else:
                widget.setChecked(True)
                self.update_yaml_value(ending, 'RunCheck', True)

    def set_default_mrpcheck(self, widget, ending):
        """
        Selects an appropriate default choice for the checkbox indicating this
            should be an MRP or not.  Keep previous saved values if present.

        :param widget: The widget containing the checkbox.

        :type widget: (PyQt).QtWidgets.QCheckBox

        :param ending: The file ending, e.g., 'llc.fits' or 'spec.tar.gz'.

        :type ending: str
        """

        index = self.get_yaml_index(ending)
        cur_value = self.param_data['FileTypes'][index[0]][ending]['MRPCheck']
        if cur_value is not None:
            widget.setChecked(cur_value)
        else:
            # Default for first run through is everything set to MRP = True.
            widget.setChecked(True)
            self.update_yaml_value(ending, 'MRPCheck', True)

    def set_default_caomproduct_type(self, widget, ending):
        """
        Selects an appropriate default choice for the CAOM Product
            Type drop-down.  Keep previous saved values if present.

        :param widget: The widget containing the drop-down box.

        :type widget: (PyQt).QtWidgets.QComboBox

        :param ending: The file ending, e.g., 'llc.fits' or 'spec.tar.gz'.

        :type ending: str
        """

        index = self.get_yaml_index(ending)
        cur_value = (
            self.param_data['FileTypes'][index[0]][ending]['CAOMProductType'])
        if cur_value is not None:
            widget.setCurrentIndex(widget.findText(cur_value))
        else:
            # Default for first run through is everything set to science.
            widget.setCurrentIndex(widget.findText('science'))
            self.update_yaml_value(ending, 'CAOMProductType', None)

    def update_param_file(self):
        """
        Updates the parameter file using the values in the GUI.
        """
        for this_ending in self.all_ending_widgets:
            for key in this_ending.keys():
                if key == 'template_widget':
                    # Update the template type in the YAML structure.
                    self.update_yaml_value(
                        this_ending['ending'],
                        'Standard',
                        this_ending['template_widget'].currentText())
                elif key == 'product_widget':
                    # Update the product type in the YAML structure.
                    self.update_yaml_value(
                        this_ending['ending'],
                        'ProductType',
                        this_ending['product_widget'].currentText())
                elif key == 'filetype_widget':
                    # Update the file type in the YAML structure.
                    self.update_yaml_value(
                        this_ending['ending'],
                        'FileType',
                        this_ending['filetype_widget'].currentText())
                elif key == 'runcheck_widget':
                    # Update the run check choice in the YAML structure.
                    self.update_yaml_value(
                        this_ending['ending'],
                        'RunCheck',
                        this_ending['runcheck_widget'].isChecked())
                elif key == 'mrpcheck_widget':
                    # Update the MRP choice in the YAML structure.
                    self.update_yaml_value(
                        this_ending['ending'],
                        'MRPCheck',
                        this_ending['mrpcheck_widget'].isChecked())
                elif key == 'caomproduct_widget':
                    # Update the CAOM product type in the YAML structure.
                    self.update_yaml_value(
                        this_ending['ending'],
                        'CAOMProductType',
                        this_ending['caomproduct_widget'].currentText())

        write_parameter_file(self.param_file, self.param_data)

    def init_ui(self):
        """
        Defines the GUI layout, text fields, buttons, etc.
        """
        # Read in the YAML parameter file.
        self.param_file = sys.argv[1]
        self.param_data = read_parameter_file(self.param_file)

        # Read in allowed template, file, and product types.
        template_choices = read_allowed_template_types()
        template_choices.sort()
        filetype_choices = read_allowed_file_types()
        filetype_choices.sort()
        product_choices = read_allowed_product_types()
        product_choices.sort()
        caomproduct_choices = read_allowed_caomproduct_types()
        caomproduct_choices.sort()

        # Create a grid layout and add all the widgets.
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        # Input directory space.
        input_dir_master = QtWidgets.QLabel("", self)
        input_dir_master.setFrameStyle(QtWidgets.QFrame.Box)
        input_dir_master.setLineWidth(1)
        input_dir_label = QtWidgets.QLabel(
            "Input Directory: " + self.param_data['FilePaths']['InputDir'],
            input_dir_master)
        input_dir_label.setAlignment(Qt.AlignLeft)
        input_dir_label.setFont(QFont("Arial", 14, QFont.Bold))

        # Add input directory widgets to this grid.
        self.grid.addWidget(input_dir_master, 0, 0, 1, 4)
        # Add a button that allows the user to update the parameter file
        # based on the options selected in the GUI.
        update_button = QtWidgets.QPushButton("Update")
        update_button.setStyleSheet("background-color:#00FF00")
        update_button.clicked.connect(self.update_param_file)
        self.grid.addWidget(update_button, 0, 6, 1, 1)

        # Add column labels to the grid.
        label_font_size = 16

        label_col0hdr1_widget = QtWidgets.QLabel("Template Params", self)
        label_col0hdr1_widget.setAlignment(Qt.AlignCenter)
        label_col0hdr1_widget.setFont(QFont("Arial", label_font_size,
                                            QFont.Bold))
        self.grid.addWidget(label_col0hdr1_widget, 1, 1, 1, 3)

        label_col0hdr2_widget = QtWidgets.QLabel("CAOM Params", self)
        label_col0hdr2_widget.setAlignment(Qt.AlignCenter)
        label_col0hdr2_widget.setFont(QFont("Arial", label_font_size,
                                            QFont.Bold))
        self.grid.addWidget(label_col0hdr2_widget, 1, 4, 1, 3)

        label_col0_widget = QtWidgets.QLabel("File Ending", self)
        label_col0_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col1_widget = QtWidgets.QLabel("Standard", self)
        label_col1_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col2_widget = QtWidgets.QLabel("Product Type", self)
        label_col2_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col3_widget = QtWidgets.QLabel("File Type", self)
        label_col3_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col4_widget = QtWidgets.QLabel("Check?", self)
        label_col4_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col5_widget = QtWidgets.QLabel("MRP?", self)
        label_col5_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col6_widget = QtWidgets.QLabel("Product Type", self)
        label_col6_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))

        self.grid.addWidget(label_col0_widget, 2, 0)
        self.grid.addWidget(label_col1_widget, 2, 1)
        self.grid.addWidget(label_col2_widget, 2, 2)
        self.grid.addWidget(label_col3_widget, 2, 3)
        self.grid.addWidget(label_col4_widget, 2, 4)
        self.grid.addWidget(label_col5_widget, 2, 5)
        self.grid.addWidget(label_col6_widget, 2, 6)

        # Add in a grid for each file endings.
        row_entry = 3
        self.all_ending_widgets = []
        for extension in self.param_data['FileTypes']:
            for ending in extension.keys():
                # This is the widget for the ending label.
                ending_widget = QtWidgets.QLabel(ending)
                # Place this ending label widget in Column 0.
                self.grid.addWidget(ending_widget,
                                    row_entry, 0)

                # This is the template drop-down widget.
                this_template_widget = QtWidgets.QComboBox()
                # Populate with choices.
                this_template_widget.addItems(template_choices)
                # Define a default or load previous.
                self.set_default_standard(this_template_widget, ending)
                # Add this template widget to Column 1.
                self.grid.addWidget(this_template_widget, row_entry, 1)

                # This is the product drop-down widget.
                this_product_widget = QtWidgets.QComboBox()
                # Populate with choices.
                this_product_widget.addItems(product_choices)
                # Define a default or load previous.
                self.set_default_product_type(this_product_widget, ending)
                # Add this product widget to Column 2.
                self.grid.addWidget(this_product_widget, row_entry, 2)

                # This is the filetype drop-down widget.
                this_file_widget = QtWidgets.QComboBox()
                # Populate with choices.
                this_file_widget.addItems(filetype_choices)
                # Guess a good default based on the extension, or keep
                # existing values if present.
                self.set_default_file_type(this_file_widget, ending)
                # Add this filetype widget to Column 3.
                self.grid.addWidget(this_file_widget, row_entry, 3)

                # This is the RunCheck checkbox widget.
                this_run_checkbox = QtWidgets.QCheckBox()
                # Guess whether this will be subject to review or not
                # based on the file extension.
                self.set_default_runcheck(this_run_checkbox, ending)
                # Add this RunCheck checkbox widget to Column 4.
                self.grid.addWidget(this_run_checkbox, row_entry, 4)

                # This is the MRP checkbox widget.
                this_mrp_checkbox = QtWidgets.QCheckBox()
                # Default to whatever is in the parameter file.
                self.set_default_mrpcheck(this_mrp_checkbox, ending)
                # Add this MRP checkbox widget to Column 5.
                self.grid.addWidget(this_mrp_checkbox, row_entry, 5)

                # This is the CAOM Product Type drop-down widget.
                this_caomproduct_widget = QtWidgets.QComboBox()
                # Populate with choices.
                this_caomproduct_widget.addItems(caomproduct_choices)
                # Define a default or load previous.
                self.set_default_caomproduct_type(this_caomproduct_widget,
                                                  ending)
                # Add this caomproduct widget to Column 2.
                self.grid.addWidget(this_caomproduct_widget, row_entry, 6)

                # We add these widgets to the list of ending widgets
                # available so we can easily access their form values.
                self.all_ending_widgets.append({
                    'extension' : extension,
                    'ending' : ending,
                    'ending_widget' : ending_widget,
                    'template_widget' : this_template_widget,
                    'product_widget' : this_product_widget,
                    'filetype_widget' : this_file_widget,
                    'runcheck_widget' : this_run_checkbox,
                    'mrpcheck_widget' : this_mrp_checkbox,
                    'caomproduct_widget' : this_caomproduct_widget
                })

                # Increment the row entry count for the next line in the GUI.
                row_entry = row_entry + 1

        # Set the window layout and show it.
        self.setLayout(self.grid)
        self.resize(800, 300)
        self.setWindowTitle("HLSP Template Selection Tool")
        self.show()

#--------------------

def read_parameter_file(ifile):
    """
    Reads existing parameter file.

    :param ifile: The name of the parameter file previously created by
        precheck_data_format.

    :type ifile: str
    """

    # Read in parameter file.
    if os.path.isfile(ifile):
        with open(ifile, 'r') as istream:
            yaml_data = yaml.load(istream)
        return yaml_data
    else:
        raise OSError('Input parameter file not found.  Looking for "' +
                      ifile + '".')

#--------------------

#--------------------

def write_parameter_file(ofile, yaml_data):
    """
    Writes to an existing parameter file.

    :param ofile: The name of the parameter file to write to.

    :type ofile: str

    :param yaml_data: The YAML data to write to the parameter file.

    :type yaml_data: dict
    """

    # Write to the parameter file.
    if os.path.isfile(ofile):
        try:
            with open(ofile, 'w') as ostream:
                yaml.dump(yaml_data, ostream, default_flow_style=False)
        except IOError:
            logging.warning("Could not save output file to %s, might be"
                            " read-only.", ofile)
    else:
        raise OSError('Input parameter file not found.  Looking for "' +
                      ofile + '".')

#--------------------
