"""
.. module:: check_file_names
    :synopsis: Given a directory, will search for all files within it and all
        sub-directories to check that file names follow MAST HLSP guidelines.
        It will identify any files that do not follow the convention, and will
        produce warnings for files that might have strange values for some
        fields, e.g., a filter name that it does not recognize.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
.. moduleeditor:: Jinm Yoon <jyoon@stsci.edu>
"""

import argparse
import datetime
import logging
import os
import sys

sys.path.append("../")
from bin.new_logger import new_logger
from check_dirpath_lower import check_dirpath_lower
from change_dirpath_sign import change_dirpath_sign
from check_file_compliance import check_file_compliance
from get_all_files import get_all_files
from lib.HLSPFile import HLSPFile

# This file contains a list of known values for the "mission" part of a MAST
# HLSP file.
KNOWN_MISSIONS_FILE = "known_missions.dat"
KNOWN_FILTERS_FILE = "known_filters.dat"
TEMPLATE_RADEC_NAMED_CATALOGS_FILE = "radec_named_catalogs.dat"

# CURRENT_DIR will allow this script to find the .dat files when run from
# outside the CHECK_FILE_NAMES directory as well.
CURRENT_DIR = os.path.dirname(__file__)

# --------------------


def read_known_missions():
    """ Reads in a list of known missions from a file on disk. """
    missions_file = os.path.join(CURRENT_DIR, KNOWN_MISSIONS_FILE)
    if os.path.isfile(missions_file):
        with open(missions_file, 'r') as km_file:
            return set([x.strip() for x in km_file.readlines()])
    else:
        raise OSError('Known Missions file not found.  Looking for "' +
                      missions_file + '".')

# --------------------


def read_known_filters():
    """ Reads in a list of known filters from a file on disk. """
    filters_file = os.path.join(CURRENT_DIR, KNOWN_FILTERS_FILE)
    if os.path.isfile(filters_file):
        with open(filters_file, 'r') as kf_file:
            return set([x.strip() for x in kf_file.readlines()])
    else:
        raise OSError('Known Filters file not found.  Looking for "' +
                      filters_file + '".')

def read_radec_named_catalogs(hlsp_name):
    """ Reads in a list of radec named catalogs from a file on disk. """
    global catalogs_file
    catalogs_file = os.path.join(CURRENT_DIR, TEMPLATE_RADEC_NAMED_CATALOGS_FILE.replace(".dat", "_"+hlsp_name+".dat"))
    #print("catalog files:", catalogs_file)
    if os.path.isfile(catalogs_file):
        with open(catalogs_file, 'r') as kc_file:
            return set([x.strip() for x in kc_file.readlines()])
    else:
        raise OSError('RADEC Named Catalogs file not found.  Looking for "' +
                      catalogs_file + '".')

# --------------------


def check_file_names(idir, hlsp_name, root_dir="", exclude_missions=None,
                     exclude_filters=None, skip_sym=False, lowercase_dirname = False , 
                     lowercase_filename = False, update_dirname_sign = False,
                     update_filename_sign = False):
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

    :param skip_sym: If True, will ignore symbolic links.
    :type skip_sym: Boolean

    :param lowercase_dirname: If True, will make directory names lowercase.
    :type lowercase_dirname: Boolean

    :param lowercase_filename: If True, will make directory names lowercase.
    :type lowercase_filename: Boolean

    :param update_dirname_sign : if True, will change the sign '+' or '-' 
                         in coordinated dirnames to '-p' or '-m' respectively.
    :type update_dirname_sign : Boolean
 
    :param update_filename_sign : if True, will change the sign '+' or '-' 
                         in coordinated filenames to '-p' or '-m' respectively.
    :type update_filename_sign : Boolean

    """

   # Start logging to an output file.
    logfile = "check_file_names_"+hlsp_name+".log"
    """
    logging.basicConfig(filename=logfile,
                        format='%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')
    """
    filenames_log = new_logger(logfile)
    filenames_log.info('Started at ' + datetime.datetime.now().isoformat())

 
    # Read in list of known missions from reference file.
    known_missions = read_known_missions()

    # Read in list of known filters from reference file.
    known_filters = read_known_filters()

    # Read in list of radec named catalogs from reference file.
    radec_named_catalogs = read_radec_named_catalogs(hlsp_name)


    # Get list of all files.
    all_file_list = get_all_files(idir, skip_sym=skip_sym)
    # Record the total number of files found, in case user needs to confirm.
    filenames_log.info('Total files found: ' + str(len(all_file_list)))

    # Make sure all sub-directories are lowercase.
    check_dirpath_lower(all_file_list, root_dir, hlsp_name, 
                        lowercase_dirname = lowercase_dirname)

    change_dirpath_sign(idir, all_file_list, root_dir, radec_named_catalogs, 
                        update_dirname_sign = update_dirname_sign)

    # Check file names for compliance.
    check_file_compliance(all_file_list, hlsp_name, known_missions,
                          known_filters, radec_named_catalogs, exclude_missions, exclude_filters, 
                          lowercase_filename = lowercase_filename, update_filename_sign = update_filename_sign)

    # Start a new HLSPFile.
    new_file = HLSPFile(name=hlsp_name.strip().lower())
    new_file.update_filepaths(input=os.path.abspath(idir))
    new_file.toggle_ingest(0, state=True)
    new_file.save(caller=__file__)

    filenames_log.info('Finished at ' + datetime.datetime.now().isoformat())

    return logfile

# --------------------

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

    parser.add_argument("--skip_sym", dest="skip_sym", action="store_true",
                        help="If set, will ignore symbolic links",
                        default=False)

    parser.add_argument("--lowercase_dirname", dest="lowercase_dirname", action="store_true",
                        help="If set, will change the directory names to lowercase",
                        default=False)
   
    parser.add_argument("--lowercase_filename", dest="lowercase_filename", action="store_true",
                        help="If set, will change the file names to lowercase",
                        default=False)

    parser.add_argument("--update_dirname_sign", dest="update_dirname_sign", action="store_true",
                        help="If set, will change the sign of the dir names to '-p/-m'"
                        "If your hlsp has a complex folder structure, use --root-dir option to point"
                        " directly to the targetname-based directories. ",
                        default=False)
    
    parser.add_argument("--update_filename_sign", dest="update_filename_sign", action="store_true",
                        help="If set, will change the sign of the file names to '-p/-m'" ,
                        default=False)
   

    return parser

# --------------------

if __name__ == "__main__":

    # Create ArgumentParser object that holds command-line args and options.
    INPUT_ARGS = setup_args().parse_args()

    # Call main function.
    check_file_names(INPUT_ARGS.idir, INPUT_ARGS.hlsp_name, INPUT_ARGS.root_dir,
                     INPUT_ARGS.exclude_missions, INPUT_ARGS.exclude_filters,
                     INPUT_ARGS.skip_sym, INPUT_ARGS.lowercase_dirname,
                     INPUT_ARGS.lowercase_filename, INPUT_ARGS.update_dirname_sign,
                     INPUT_ARGS.update_filename_sign)
    if INPUT_ARGS.update_filename_sign:
        os.rename(catalogs_file, catalogs_file+".Changed")
# --------------------
