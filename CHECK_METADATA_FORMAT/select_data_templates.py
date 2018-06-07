"""
.. module:: select_data_templates
    :synopsis: GUI to allow the user to specify templates and data types for
        HLSP files before running check_metadata_format on them.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse
import datetime
import logging
import sys

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PyQt4.QtWidgets import QApplication

from select_data_templates_gui import SelectDataTemplatesGUI

#--------------------

def setup_args():
    """
    Set up command-line arguments and options.

    :returns: ArgumentParser -- Stores arguments and options.
    """

    parser = argparse.ArgumentParser(description="Select templates and data"
                                     " types for HLSP files before checking"
                                     " their data formats.")

    parser.add_argument("ifile", action="store", type=str, help="[Required]"
                        " Parameter file created by precheck_data_format ("
                        "ends in .hlsp).")

    return parser

#--------------------

if __name__ == "__main__":

    # Start logging to an output file.
    logging.basicConfig(filename="select_data_templates.log",
                        format='%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')
    logging.info('Started at %s', datetime.datetime.now().isoformat())

    # Create ArgumentParser object that holds command-line args and options.
    INPUT_ARGS = setup_args().parse_args()

    # Start the GUI
    APP = QApplication(sys.argv)
    WIDGET = SelectDataTemplatesGUI()
    sys.exit(APP.exec_())
    # NOTE: This logging statement does not show up in the log file. To-do item
    # would be to determine how to log when the QT window is closed by the user
    # but is not a high priority item.
    logging.info('Finished at %s', datetime.datetime.now().isoformat())

#--------------------
