"""
.. module:: select_data_templates_gui
    :synopsis: Defines the GUI used by select_data_templates.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------

import os
import sys
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

def set_default_file_type(widget, exten):
    """
    Selects an appropriate default choice for the File Type drop-down based
        on the extension.

    :param widget: The widget containing the drop-down box.

    :type widget: (PyQt).QtWidgets.QComboBox

    :param exten: The file name extension, used to pre-populate the drop-down.

    :type exten: str
    """

    if exten == 'fits':
        widget.setCurrentIndex(widget.findText("fits"))
    elif exten == 'png':
        widget.setCurrentIndex(widget.findText("graphic"))
    elif exten == 'tiff':
        widget.setCurrentIndex(widget.findText("graphic"))
    elif exten == 'jpg':
        widget.setCurrentIndex(widget.findText("graphic"))
    elif exten == 'jpeg':
        widget.setCurrentIndex(widget.findText("graphic"))
    elif exten == 'txt':
        widget.setCurrentIndex(widget.findText("text"))
    else:
        widget.setCurrentIndex(widget.findText("none"))

#--------------------

def set_default_checkfile(widget, exten):
    """
    Selects an appropriate default choice for the checkbox to run HLSP format
        checking or not.

    :param widget: The widget containing the checkbox.

    :type widget: (PyQt).QtWidgets.QCheckBox

    :param exten: The file name extension, used to pre-populate the drop-down.

    :type exten: str
    """

    if exten == 'png' or exten == 'tiff' or exten == 'jpg' or exten == 'jpeg':
        widget.setChecked(False)
    else:
        widget.setChecked(True)

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

    def init_ui(self):
        """
        Defines the GUI layout, text fields, buttons, etc.
        """

        # Read in the YAML parameter file.
        param_data = read_parameter_file(sys.argv[1])

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
                                           param_data['InputDir'],
                                           input_dir_master)
        input_dir_label.setAlignment(Qt.AlignLeft)
        input_dir_label.setFont(QFont("Arial", 14, QFont.Bold))

        # Add input directory widgets to this grid.
        self.grid.addWidget(input_dir_master, 0, 0, 1, 5)

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
        for extension in param_data.keys():
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
                for ending in param_data[extension]:
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
                    set_default_file_type(this_file_widget, extension)
                    self.grid.addWidget(this_file_widget, row_entry, 3)
                    this_run_checkbox = QtWidgets.QCheckBox()
                    # Guess whether this will be subject to review or not
                    # based on the file extension.
                    set_default_checkfile(this_run_checkbox, extension)
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

    :type idir: str
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
