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
    import PyQt5.QtWidgets as QtWidgets
except ImportError:
    from PyQt4.QtCore import Qt
    import PyQt4.QtWidgets as QtWidgets

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

        # Create a grid layout and add all the widgets.
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        # Input directory space.
        input_dir_label = QtWidgets.QLabel("Input Directory: ", self)
        input_dir_data = QtWidgets.QLabel(param_data['InputDir'],
                                          self)
        input_dir_label.setAlignment(Qt.AlignLeft)
        input_dir_data.setAlignment(Qt.AlignLeft)

        # Add in a grid for each file endings.
        row_entry = 1
        for extension in param_data.keys():
            if extension != 'InputDir':
                # Add a label for this extension.
                self.grid.addWidget(QtWidgets.QLabel(extension.upper(), self),
                                    row_entry, 0)
                row_entry = row_entry + 1
                # Add a row for each ending with this extension.
                # These are an entry for that extension, a drop-down for
                # template type, a drop-down for product type, a drop-down for
                # file type.
                for ending in param_data[extension]:
                    self.grid.addWidget(QtWidgets.QLabel(ending), row_entry, 0)
                    self.grid.addWidget(QtWidgets.QComboBox(), row_entry, 1)
                    self.grid.addWidget(QtWidgets.QComboBox(), row_entry, 2)
                    self.grid.addWidget(QtWidgets.QComboBox(), row_entry, 3)
                    row_entry = row_entry + 1

        # Add widgets to this grid.
        self.grid.addWidget(input_dir_label, 0, 0)
        self.grid.addWidget(input_dir_data, 0, 1)

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
