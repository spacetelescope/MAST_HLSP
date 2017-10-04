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
import os

from check_dirpath_lower import check_dirpath_lower
from check_file_compliance import check_file_compliance
from get_all_files import get_all_files

# This file contains a list of known values for the "mission" part of a MAST
# HLSP file.
KNOWN_MISSIONS_FILE = "known_missions.dat"
KNOWN_FILTERS_FILE = "known_filters.dat"

#--------------------

def check_file_names(idir, hlsp_name, root_dir="", exclude_missions=None,
                     exclude_filters=None):
    """
    Checks all files contained below this directory for MAST HLSP compliance.

    :param idir: The directory containing HLSP files to check.

    :type idir: str

    :param hlsp_name: The name of the HLSP.

    :type hlsp_name: str

    :param root_dir: Optional root directory to skip when checking compliance.

    :type root_dir: str

    :param exclude_missions: Optional list of values for the "mission" part of
        the file names that will be temporarily accepted (for this run only).

    :type exclude_missions: list

    :param exclude_filters: Optional list of values for the "filter" part of
        the file names that will be temporarily accepted (for this run only).

    :type exclude_filters: list
    """

    # Start logging to an output file.
    logging.basicConfig(filename="check_file_names.log",
                        format='%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')
    logging.info('Started at ' + datetime.datetime.now().isoformat())

    # Read in list of known missions from reference file.
    if os.path.isfile(KNOWN_MISSIONS_FILE):
        with open(KNOWN_MISSIONS_FILE, 'r') as km_file:
            known_missions = set([x.strip() for x in km_file.readlines()])
    else:
        raise OSError('Known Missions file not found.  Looking for "' +
                      KNOWN_MISSIONS_FILE + '".')

    # Read in list of known filters from reference file.
    if os.path.isfile(KNOWN_FILTERS_FILE):
        with open(KNOWN_FILTERS_FILE, 'r') as kf_file:
            known_filters = set([x.strip() for x in kf_file.readlines()])
    else:
        raise OSError('Known Filters file not found.  Looking for "' +
                      KNOWN_FILTERS_FILE + '".')

    # Get list of all files.
    all_file_list = get_all_files(idir)

    # Make sure all sub-directories are lowercase.
    check_dirpath_lower(all_file_list, root_dir)

    # Check file names for compliance.
    check_file_compliance(all_file_list, hlsp_name, known_missions,
                          known_filters, exclude_missions, exclude_filters)

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

    parser.add_argument("hlsp_name", action="store", type=str.lower,
                        help="[Required] Name of the HLSP.")

    parser.add_argument("--root_dir", dest="root_dir", action="store", type=str,
                        help="Optional root path to HLSP directory. This part"
                        " of the file path will not be subject to MAST HLSP"
                        " requirements (e.g., lowercase will not be checked).")

    parser.add_argument("--exclude_missions", dest="exclude_missions", nargs='*',
                        action="store", help="Optional list of mission values"
                        " to temporarily accept as valid values.")

    parser.add_argument("--exclude_filters", dest="exclude_filters", nargs='*',
                        action="store", help="Optional list of filter values"
                        " to temporarily accept as valid values.")

    return parser

#--------------------

if __name__ == "__main__":

    # Create ArgumentParser object that holds command-line args and options.
    INPUT_ARGS = setup_args().parse_args()

    # Call main function.
    check_file_names(INPUT_ARGS.idir, INPUT_ARGS.hlsp_name, INPUT_ARGS.root_dir,
                     INPUT_ARGS.exclude_missions, INPUT_ARGS.exclude_filters)

#--------------------
