"""
.. module:: check_file_names
    :synopsis: Given a directory, will search for all files within it and all
        sub-directories to check that file names follow MAST HLSP guidelines.
        It will identify any files that do not follow the convention, and will
        produce warnings for files that might have strange values for some
        fields, e.g., a filter name that it does not recognize.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse
import datetime
import logging

from get_all_files import get_all_files

#--------------------

def check_file_names(idir):
    """
    Checks all files contained below this directory for MAST HLSP compliance.

    :param idir: The directory containing HLSP files to check.

    :type idir: str
    """

    # Start logging to an output file.
    logging.basicConfig(filename="check_file_names.log",
                        format='%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')
    logging.info('Started at ' + datetime.datetime.now().isoformat())

    # Get list of all files.
    all_file_list = get_all_files(idir)

    logging.info('Finished at ' + datetime.datetime.now().isoformat())

#--------------------

def setup_args():
    """
    Set up command-line arguments and options.

    :returns: ArgumentParser -- Stores arguments and options.
    """

    parser = argparse.ArgumentParser(description="Check that file names follow"
                                     " MAST HLSP convention.")

    parser.add_argument("idir", action="store", type=str, help="[Required]"
                        " Full path to the folder containing HLSP files to"
                        " check.")

    return parser

#--------------------

if __name__ == "__main__":

    # Create ArgumentParser object that holds command-line args and options.
    INPUT_ARGS = setup_args().parse_args()

    # Call main function.
    check_file_names(INPUT_ARGS.idir)

#--------------------
