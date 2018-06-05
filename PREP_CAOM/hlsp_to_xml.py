"""
..module:: hlsp_to_xml
    :synopsis: This is the primary script for generating a template XML file
    to feed into CAOM ingestion software.  The user must provide a .yaml
    config file with some required parameters, which is specific to the HLSP
    being operated on.

Global variables:
EXPECTED_CONFIGS:
These top-level sections are all required within the .yaml config file.

EXPECTED_PATHS:
These path values are required within the "filepaths" section of the .yaml
config file.

KEYWORD_TABLE:
A general csv table translating CAOM metadata and provenance entries to fits
headers.

LOG:
The desired filename for the generated log file.  Will be placed in the
'output' file path provided in the .yaml config file.

STATICS:
A .yaml file with constant entries to insert for various kinds of HLSPs and
file types.
"""

import argparse
import datetime
import logging
import os
import sys
import yaml
from add_header_entries import add_header_entries
from add_product_caomxml import add_product_caomxml
from add_value_caomxml import add_value_caomxml
from adjust_defaults import adjust_defaults
from lxml import etree

from lib.CAOMxml import *

import util.check_paths as cp
from util.check_log import check_log
from util.read_yaml import read_yaml

# Set global variables
EXPECTED_CONFIGS = ["data_type",
                    "filepaths",
                    "file_types",
                    "header_type",
                    "unique_parameters",]
EXPECTED_PATHS = ["hlsppath",
                  "output",
                  "overwrite",]
KEYWORD_TABLE = "resources/hlsp_keywords.csv"
LOG = "hlsp_to_xml.log"
STATICS = "resources/hlsp_caom_staticvalues.yaml"

#--------------------

def hlsp_to_xml(config):
    """ Executes all necessary steps to generate an XML template file for CAOM
    ingestion of files associated with an HLSP.

    :param config: The file path to the user-provided .yaml file containing
                   necessary information specific to the HLSP being processed.
    :type config: str
    """

    # Check the user-provided config file path.
    config = cp.check_existing_file(config)
    if config is None:
        return

    # Try to read in the yaml config file.
    try:
        parameters = read_yaml(config)
    except (FileNotFoundError, TypeError) as err:
        print(err)
        return

    # Make sure the config file has all the expected sections
    for section in EXPECTED_CONFIGS:
        if section not in parameters:
            print("{0} does not define '{1}'!".format(config, section))
            return

    # Make sure all necessary filepaths have been provided
    for path in EXPECTED_PATHS:
        if path not in parameters["filepaths"]:
            print("{0} is missing an '{1}' filepath!".format(config, path))
            return

    # Config parameters have been checked, now read into variables
    paths = parameters["filepaths"]
    hlsppath = paths["hlsppath"]
    output = paths["output"]
    overwrite = paths["overwrite"]

    extensions = parameters["file_types"]
    header_type = parameters["header_type"]
    data_type = parameters["data_type"]
    keyword_updates = parameters["keyword_updates"]
    uniques = parameters["unique_parameters"]

    # Set up logging
    outdir = os.path.dirname(output)
    logfile = os.path.join(outdir, LOG)
    logfile = cp.check_new_file(logfile)
    if logfile is None:
        return
    logging.basicConfig(filename=logfile,
                        format='***%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')
    logging.info("Logging started at {0}".format(
                                        datetime.datetime.now().isoformat()))

    # Prepare the output file
    output = cp.check_new_file(output)
    if output is None:
        return
    print("Opening {0}".format(output))
    if overwrite or not os.path.isfile(output):
        with open(output, 'w') as xmlfile:
            xmlfile.close()
    else:
        err = "{0} already exists. Set overwrite=True to proceed.".format(
                                                                       output)
        logging.error(err)
        print(err)
        return

    # Begin the lxml tree and add the main subelements
    composite = etree.Element("CompositeObservation")
    xmltree = etree.ElementTree(composite)
    metadata = etree.SubElement(composite, "metadataList")
    provenance = etree.SubElement(composite, "provenance")
    products = etree.SubElement(composite, "productList")

    # Create the CAOMxmlList we will save CAOMxml objects into
    caomlist = CAOMxmlList()

    # Read the static CAOM values from the yaml file
    print("Creating standard HLSP entries...")
    statics = cp.check_existing_file(STATICS)
    if statics is None:
        return
    try:
        static_values = read_yaml(statics)
    except (FileNotFoundError, TypeError) as err:
        logging.error(err)
        print(err)
        return

    # Add standard entries
    caomlist = add_value_caomxml(caomlist, static_values["hlsp"])

    # Add some conditional entries
    if data_type == "timeseries":
        caomlist = add_value_caomxml(caomlist, static_values["timeseries"])
    if header_type == "kepler":
        caomlist = add_value_caomxml(caomlist, static_values["kepler"])
    print("...done!")

    # Add information from the header keywords table.
    print("Adding entries from fits headers...")
    caomlist = add_header_entries(caomlist, KEYWORD_TABLE, header_type)
    print("...done!")

    # Add CAOMxml entries for HLSP-specifiic CAOM parameters.
    print("Adding unique entries for this HLSP...")
    if uniques is None:
        logging.warning("No unique parameters provided in the yaml config.")
    else:
        caomlist = add_value_caomxml(caomlist, uniques)
    print("...done!")

    # Add product entries to the list of CAOMxml objects
    print("Generating the productList...")
    caomlist = add_product_caomxml(caomlist, hlsppath, extensions, data_type)
    print("...done!")

    # Make final tweaks to caomlist
    print("Making final adjustments...")
    caomlist = adjust_defaults(caomlist, header_type, keyword_updates)
    print("...done!")

    # Create the head string to write to doctype
    head_strings = []
    head_strings.append("<!-- Process HLSP for CAOM ingestion -->")
    head_strings.append("")
    head = "\n".join(head_strings)

    # Add CAOMxml elements to xmltree
    print("Writing everything to XML...")
    for entry in sorted(caomlist):

        # Skip extra top-level entries caused by recursion in add_value_caomxml
        if xmltree.find(entry.label) is None:
            entry.send_to_lxml(xmltree)

    # Write the xml tree to the OUTPUT file
    # (doctype not a valid argument for python 2.x)
    xmltree.write(output,
                  encoding="utf-8",
                  xml_declaration=True,
                  #doctype=head,
                  pretty_print=True)
    print("...XML file generated!")

    # Print out log stats before finishing
    check_log(logfile)
    logging.info("Logging finished at {0}".format(
                                        datetime.datetime.now().isoformat()))

#--------------------

if __name__ == "__main__":
    """ User must provide a path to the yaml config file in order to run.
    """

    parser = argparse.ArgumentParser(description="""Generate a template XML
                                     file to prep for CAOM ingest.""")
    parser.add_argument('config', help="""The user must provide a filepath to
                        a .yaml config file.""")
    line_input = parser.parse_args()
    hlsp_to_xml(line_input.config)
