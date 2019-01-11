"""
.. module:: precheck_data_format
    :synopsis: Given a directory, will search for all files within it and start
        a parameter file to use in check_metadata_format, based on the ending of
        files recursively found inside the directory.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse
import datetime
import logging
import sys

sys.path.append("../")
from bin.new_logger import new_logger
from lib.HLSPFile import HLSPFile
from lib.FileType import FileType
from get_all_file_endings import get_all_file_endings
from make_parameter_file import make_parameter_file

# --------------------


def precheck_data_format(idir, hlsp_name):
    """
    Generates parameter file for check_metadata_format based on file endings.

    :param idir: The directory containing HLSP files to check.

    :type idir: str

    :param hlsp_name: The name of the HLSP.

    :type hlsp_name: str
    """

    # Start logging to an output file.
    """
    logging.basicConfig(filename="precheck_data_format.log",
                        format='%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')
    """
    logname = "precheck_data_format.log"
    precheck_log = new_logger(logname)
    precheck_log.info('Started at ' + datetime.datetime.now().isoformat())

    # Initialize a new HLSPFile object.
    new_file = HLSPFile(name=hlsp_name)

    # Get unique set of file endings.
    all_file_endings = get_all_file_endings(idir)

    # Sort these based on the extension type.
    file_endings = set([x.split('.')[-1] for x in all_file_endings])

    for fe in all_file_endings:
        new_type = FileType(fe)
        new_file.add_filetype(new_type)

    # Create the output file, based on the name of the HLSP.
    new_file.toggle_ingest(1, state=True)
    filename = new_file.save(caller=__file__)
    #make_parameter_file(filename, file_endings, all_file_endings, idir)

    precheck_log.info('Finished at ' + datetime.datetime.now().isoformat())

    return filename

# --------------------


def setup_args():
    """
    Set up command-line arguments and options.

    :returns: ArgumentParser -- Stores arguments and options.
    """

    parser = argparse.ArgumentParser(description="Create a parameter file to"
                                     " use with check_metadata_format, based on"
                                     " file endings.")

    parser.add_argument("idir", action="store", type=str, help="[Required]"
                        " Full path to the folder containing HLSP files to"
                        " check.")

    parser.add_argument("hlsp_name", action="store", type=str.lower,
                        help="[Required] Name of the HLSP.")

    return parser

# --------------------


if __name__ == "__main__":

    # Create ArgumentParser object that holds command-line args and options.
    INPUT_ARGS = setup_args().parse_args()

    # Call main function.
    precheck_data_format(INPUT_ARGS.idir, INPUT_ARGS.hlsp_name)

# --------------------
