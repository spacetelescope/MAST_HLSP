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
import sys
import numpy
import yaml
from apply_metadata_check import apply_metadata_check

sys.path.append("../")
from bin.new_logger import new_logger
from lib.FitsKeyword import FitsKeyword, FitsKeywordList

# --------------------


def _read_from_file(paramfile):
    """
    Code to load parameter data from a YAML file, moved out of
    check_metadata_format to allow different inputs to that function.

    :param paramfile: The parameter file created by 'precheck_data_format' and
        'select_data_templates'.

    :type paramfile: str
    """

    # Read in the parameter file.
    if os.path.isfile(paramfile):
        with open(paramfile, 'r') as istream:
            param_data = yaml.load(istream)
    else:
        raise OSError('Input parameter file not found.  Looking for "' +
                      paramfile + '".')

    return param_data

# --------------------


def check_metadata_format(paramfile, is_file=True):
    """
    Checks HLSP files for compliance.  Logs errors and warnings to log file.

    :param paramfile: The parameter file created by 'precheck_data_format' and
        'select_data_templates'.

    :type paramfile: str
    """

    # Read in all the YAML standard template files once to pass along.
#    templates_to_read = ["TEMPLATES/timeseries_mast.yml",
#                         "TEMPLATES/timeseries_k2.yml"]
    templates_to_read = ["TEMPLATES/timeseries_k2.yml",
                         # "TEMPLATES/image_hst.yml"
                         ]

    # Create FitsKeywordList object for each standard in all_standards array.
    # These are used to define the expected keywords for a given template
    # standard, but can have any part overwritten by the .hlsp file.
    all_standards = numpy.asarray([])
    for ttr in templates_to_read:
        this_file = os.path.realpath(__file__)
        this_dir = "/".join(this_file.split("/")[:-1])
        ttr = os.path.join(this_dir, ttr)
        if os.path.isfile(ttr):
            with open(ttr, 'r') as istream:
                yaml_data = yaml.load(istream)
                all_standards = numpy.append(all_standards,
                                             FitsKeywordList(
                                                 yaml_data['PRODUCT'],
                                                 yaml_data['STANDARD'],
                                                 yaml_data['KEYWORDS']))
        else:
            raise IOError("Template file not found: " + ttr)

    # Start logging to an output file.
    log_file_name = "check_metadata_format.log"
    metadata_log = new_logger(log_file_name)
    metadata_log.info('Started at ' + datetime.datetime.now().isoformat())

    # This will allow us to support running via script by default with a
    # previously saved metadata precheck file, or live via the GUI with an
    # HLSPFile class object.
    param_data = (_read_from_file(paramfile) if is_file else paramfile)

    # The root directory of the HLSP files is stored in the parameter file.
    if 'InputDir' in param_data['FilePaths']:
        file_base_dir = param_data['FilePaths']['InputDir']
    else:
        raise ValueError("Parameter file missing 'InputDir' field: " +
                         '"' + paramfile + '".')

    # Loop over each file ending.  Run the metadata checks on any file ending
    # marked to be checked for HLSP requirements.
    endings_to_check = []
    for ending in param_data['FileTypes']:
        this_key = [*ending][0]
        if ending[this_key]['RunCheck']:
            endings_to_check.append(ending)

    # Pull any FITS keyword updates out of paramfile.  (this can be either the
    # file created by precheck_data_format.py or the HLSPFile provided by
    # running through the GUI)
    try:
        kw_updates = param_data['KeywordUpdates']
    except KeyError:
        kw_updates = None

    if isinstance(kw_updates, list):
        new_list = FitsKeywordList.empty_list()
        new_list.fill_from_list(kw_updates)
        kw_updates = new_list

    # Apply the metadata correction on the requested file endings.
    log_message_counts = apply_metadata_check(file_base_dir,
                                              endings_to_check,
                                              all_standards,
                                              kw_updates
                                              )

    metadata_log.info('Finished at %s', datetime.datetime.now().isoformat())

    # Add a summary of the number of log messages to the top of the log file.
    with open(log_file_name, 'r') as ilogfile:
        all_log_messages = ilogfile.read()
    with open(log_file_name, 'w') as ologfile:
        ologfile.write('# ------------------------------\n')
        ologfile.write('Message Summary (# Files: [Type] Message)\n')
        for dkey in log_message_counts:
            ologfile.write(str(log_message_counts[dkey]['count']) + ': [' +
                           log_message_counts[dkey]['type'] + '] ' + dkey +
                           '\n')
        ologfile.write('# ------------------------------\n')
        ologfile.write(all_log_messages)

# --------------------


def setup_args():
    """
    Set up command-line arguments and options.

    :returns: ArgumentParser -- Stores arguments and options.
    """

    parser = argparse.ArgumentParser(description="Check that file formats "
                                     "follow MAST HLSP convention.")

    parser.add_argument("paramfile", action="store", type=str, help="[Required]"
                        " Parameter file from 'select_data_templates'.")

    return parser

# --------------------


if __name__ == "__main__":

    # Create ArgumentParser object that holds command-line args and options.
    INPUT_ARGS = setup_args().parse_args()

    # Call main function.
    check_metadata_format(INPUT_ARGS.paramfile)

# --------------------
