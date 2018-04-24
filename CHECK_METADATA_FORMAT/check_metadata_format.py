"""
.. module:: check_metadata_format
    :synopsis: Given a directory, will search for all files within it and check
        that files follow HLSP guidelines.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse
import datetime
import logging
import numpy
import os
import yaml

from apply_metadata_check import apply_metadata_check
#--------------------

def check_metadata_format(paramfile):
    """
    Checks HLSP files for compliance.  Logs errors and warnings to log file.

    :param paramfile: The parameter file created by 'precheck_data_format' and
        'select_data_templates'.

    :type paramfile: str
    """

    # Read in all the YAML standard template files once to pass along.
#    templates_to_read = ["TEMPLATES/timeseries_mast.yml",
#                         "TEMPLATES/timeseries_k2.yml"]
    templates_to_read = ["TEMPLATES/timeseries_k2.yml"]
    all_standards = numpy.asarray([])
    for ttr in templates_to_read:
        if os.path.isfile(ttr):
            with open(ttr, 'r') as istream:
                all_standards = numpy.append(all_standards, yaml.load(istream))
        else:
            raise IOError("Template file not found: " + ttr)

    # Start logging to an output file.
    logging.basicConfig(filename="check_metadata_format.log",
                        format='%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')
    logging.info('Started at ' + datetime.datetime.now().isoformat())

    # Read in the parameter file.
    if os.path.isfile(paramfile):
        with open(paramfile, 'r') as istream:
            param_data = yaml.load(istream)
    else:
        raise OSError('Input parameter file not found.  Looking for "' +
                      paramfile + '".')

    # The root directory of the HLSP files is stored in the parameter file.
    if 'InputDir' in param_data:
        file_base_dir = param_data['InputDir']
    else:
        raise ValueError("Parameter file missing 'InputDir' field: " +
                         '"' + paramfile + '".')

    # Loop over each extension, and then each file ending.  Run the metadata
    # checks on any file ending marked to be checked for HLSP requirements.
    # NOTE: One of the "extension" keys is the InputDir where the files are, so
    # skip over that one.
    endings_to_check = []
    for exten in param_data.keys():
        if exten != 'InputDir':
            for ending in param_data[exten]:
                if ending['FileParams']['RunCheck']:
                    endings_to_check.append(ending)

    # Apply the metadata correction on the requested file endings.
    apply_metadata_check(file_base_dir, endings_to_check, all_standards)

    logging.info('Finished at ' + datetime.datetime.now().isoformat())

#--------------------

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

#--------------------

if __name__ == "__main__":

    # Create ArgumentParser object that holds command-line args and options.
    INPUT_ARGS = setup_args().parse_args()

    # Call main function.
    check_metadata_format(INPUT_ARGS.paramfile)

#--------------------
