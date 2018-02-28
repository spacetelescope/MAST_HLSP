"""
.. module:: check_metadata_format
    :synopsis: Given a directory, will search for all files within it and check
        that files follow HLSP guidelines.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse
import datetime
import logging
import os

#--------------------

def check_metadata_format(ifile):
    """
    Checks HLSP files for compliance.

    :param ifile: The parameter file created by precheck_data_format and
        select_data_templates.

    :type idir: str
    """

    # Start logging to an output file.
    logging.basicConfig(filename="check_metadata_format.log",
                        format='%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')
    logging.info('Started at ' + datetime.datetime.now().isoformat())

    # Read in the parameter file.
    if os.path.isfile(ifile):
        pass
    else:
        raise OSError('Input parameter file not found.  Looking for "' +
                      ifile + '".')

    logging.info('Finished at ' + datetime.datetime.now().isoformat())

#--------------------

def setup_args():
    """
    Set up command-line arguments and options.

    :returns: ArgumentParser -- Stores arguments and options.
    """

    parser = argparse.ArgumentParser(description="Check that file formats "
                                     "follow MAST HLSP convention.")

    parser.add_argument("idir", action="store", type=str, help="[Required]"
                        " Full path to the folder containing HLSP files to"
                        " check.")

    return parser

#--------------------

if __name__ == "__main__":

    # Create ArgumentParser object that holds command-line args and options.
    INPUT_ARGS = setup_args().parse_args()

    # Call main function.
    check_metadata_format(INPUT_ARGS.idir)

#--------------------
