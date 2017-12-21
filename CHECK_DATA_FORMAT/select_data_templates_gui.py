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

class SelectDataTemplatesGUI(QtWidgets.QWidget):
    """
    This class builds a pyqt GUI for defining templates and data format types
        of HLSP files to check with check_data_format.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def update_yaml_value(self, exten, ending, update_key, update_value):
        """
        Updates a value in the YAML data object.

        :param exten: str

        :type exten: str

        :param ending: The information associated with this file ending.

        :type ending: dict

        :param update_key: The key to update with the update_value in the
            YAML data object.

        :type update_key: str

        :param update_value: The value to update with in the YAML data object.

        :type update_value: str or bool
        """

        file_ending_list = numpy.asarray(
            [x['FileEnding'] for x in self.param_data[exten]])
        index = numpy.where(file_ending_list == ending['FileEnding'])[0]
        if len(index) == 1:
            self.param_data[exten][index[0]]['FileParams'][update_key] = (
                update_value)
        else:
            raise ValueError("Multiple entries with the same FileEnding"
                             " found.")

    def set_default_file_type(self, widget, exten, ending):
        """
        Selects an appropriate default choice for the File Type drop-down based
            on the extension.

        :param widget: The widget containing the drop-down box.

        :type widget: (PyQt).QtWidgets.QComboBox

        :param exten: The file name extension, used to pre-populate the
            drop-down.

        :type exten: str

        :param ending: The information associated with this file ending.

        :type ending: dict
        """

        if exten == 'fits':
            widget.setCurrentIndex(widget.findText("fits"))
            self.update_yaml_value(exten, ending, "FileType", "fits")
        elif exten == 'png':
            widget.setCurrentIndex(widget.findText("graphic"))
            self.update_yaml_value(exten, ending, "FileType", "graphic")
        elif exten == 'tiff':
            widget.setCurrentIndex(widget.findText("graphic"))
            self.update_yaml_value(exten, ending, "FileType", "graphic")
        elif exten == 'jpg':
            widget.setCurrentIndex(widget.findText("graphic"))
            self.update_yaml_value(exten, ending, "FileType", "graphic")
        elif exten == 'jpeg':
            widget.setCurrentIndex(widget.findText("graphic"))
            self.update_yaml_value(exten, ending, "FileType", "graphic")
        elif exten == 'txt':
            widget.setCurrentIndex(widget.findText("text"))
            self.update_yaml_value(exten, ending, "FileType", "text")
        else:
            widget.setCurrentIndex(widget.findText(None))
            self.update_yaml_value(exten, ending, "FileType", None)

    def set_default_checkfile(self, widget, exten, ending):
        """
        Selects an appropriate default choice for the checkbox to run HLSP format
            checking or not.

        :param widget: The widget containing the checkbox.

        :type widget: (PyQt).QtWidgets.QCheckBox

        :param exten: The file name extension, used to pre-populate the
            drop-down.

        :type exten: str

        :param ending: The information associated with this file ending.

        :type ending: dict
        """

        if (exten == 'png' or exten == 'tiff' or exten == 'jpg' or
                exten == 'jpeg'):
            widget.setChecked(False)
            self.update_yaml_value(exten, ending, 'RunCheck', False)
        else:
            widget.setChecked(True)
            self.update_yaml_value(exten, ending, 'RunCheck', True)

    def update_param_file(self):
        """
        Updates the parameter file using the values in the GUI.
        """
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

        # Create a grid layout and add all the widgets.
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        # Input directory space.
        input_dir_master = QtWidgets.QLabel("", self)
        input_dir_master.setFrameStyle(QtWidgets.QFrame.Box)
        input_dir_master.setLineWidth(1)
        input_dir_label = QtWidgets.QLabel("Input Directory: " +
                                           self.param_data['InputDir'],
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
        self.grid.addWidget(update_button, 0, 4, 1, 1)

        # Add column labels to the grid.
        label_font_size = 16
        label_col0_widget = QtWidgets.QLabel("File Ending", self)
        label_col0_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col1_widget = QtWidgets.QLabel("Template Type", self)
        label_col1_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col2_widget = QtWidgets.QLabel("Product Type", self)
        label_col2_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col3_widget = QtWidgets.QLabel("File Type", self)
        label_col3_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))
        label_col4_widget = QtWidgets.QLabel("Run Check?", self)
        label_col4_widget.setFont(QFont("Arial", label_font_size, QFont.Bold))

        self.grid.addWidget(label_col0_widget, 1, 0)
        self.grid.addWidget(label_col1_widget, 1, 1)
        self.grid.addWidget(label_col2_widget, 1, 2)
        self.grid.addWidget(label_col3_widget, 1, 3)
        self.grid.addWidget(label_col4_widget, 1, 4)

        # Add in a grid for each file endings.
        row_entry = 2
        for extension in self.param_data.keys():
            if extension != 'InputDir':
                # Add a label for this extension.
                this_extension_widget = QtWidgets.QLabel(extension.upper(),
                                                         self)
                this_extension_widget.setFrameStyle(QtWidgets.QFrame.Box)
                this_extension_widget.setLineWidth(1)
                self.grid.addWidget(this_extension_widget,
                                    row_entry, 0, 1, 5)
                row_entry = row_entry + 1
                # Add a row for each ending with this extension.
                # These are an entry for that extension, a drop-down for
                # template type, a drop-down for product type, a drop-down for
                # file type.
                for ending in self.param_data[extension]:
                    self.grid.addWidget(QtWidgets.QLabel(ending['FileEnding']),
                                        row_entry, 0)
                    this_template_widget = QtWidgets.QComboBox()
                    this_template_widget.addItems(template_choices)
                    # Default to "none".
                    this_template_widget.setCurrentIndex(
                        this_template_widget.findText("none"))
                    self.grid.addWidget(this_template_widget, row_entry, 1)
                    this_product_widget = QtWidgets.QComboBox()
                    this_product_widget.addItems(product_choices)
                    # Default to "none".
                    this_product_widget.setCurrentIndex(
                        this_product_widget.findText("none"))
                    self.grid.addWidget(this_product_widget, row_entry, 2)
                    this_file_widget = QtWidgets.QComboBox()
                    this_file_widget.addItems(filetype_choices)
                    # Guess a good default based on the extension.
                    self.set_default_file_type(this_file_widget, extension,
                                               ending)
                    self.grid.addWidget(this_file_widget, row_entry, 3)
                    this_run_checkbox = QtWidgets.QCheckBox()
                    # Guess whether this will be subject to review or not
                    # based on the file extension.
                    self.set_default_checkfile(this_run_checkbox, extension,
                                               ending)
                    self.grid.addWidget(this_run_checkbox, row_entry, 4)
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
            logging.warning("Could not save output file to " + ofile + ", file"
                            " might be read-only.")
    else:
        raise OSError('Input parameter file not found.  Looking for "' +
                      ofile + '".')

#--------------------
