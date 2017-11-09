"""
This is the primary script for generating a template XML file to feed into
CAOM ingestion software.  The user must provide a .yaml config file with some
required parameters, which is specific to the HLSP being operated on.

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

from CAOMxml import *
from lxml import etree
from add_header_entries import add_header_entries
from add_productlist_xml import add_productlist_xml
from add_static_values import add_static_values
from util.add_value_caomxml import add_value_caomxml
from util.check_log import check_log
from util.read_yaml import read_yaml
import util.check_paths as cp
import logging
import os
import sys
import yaml

#Set global variables
global EXPECTED_CONFIGS
EXPECTED_CONFIGS = ["filepaths",
                    "header_type",
                    "data_types",
                    "unique_parameters"]
global EXPECTED_PATHS
EXPECTED_PATHS = ["extensions",
                  "hlsppath",
                  "output",
                  "overwrite"]
global LOG
LOG = "hlsp_to_xml.log"
global STATICS
STATICS = "resources/hlsp_caom_staticvalues.yaml"
global KEYWORD_TABLE
KEYWORD_TABLE = "resources/hlsp_keywords_test.csv"

#--------------------

def hlsp_to_xml(config):
    """
    Executes all necessary steps to generate an XML template file for CAOM
    ingestion of files associated with an HLSP.

    :param config: The file path to the user-provided .yaml file containing
    necessary information specific to the HLSP being processed.
    :type config: string
    """
    
    #Check the user-provided config file path.
    config = cp.check_existing_file(config)

    #Try to read in the yaml config file.
    parameters = read_yaml(config)

    #Make sure the config file has all the expected sections
    for section in EXPECTED_CONFIGS:
        if section not in parameters:
            print("{0} does not define '{1}'!".format(config, section))
            quit()

    #Make sure all necessary filepaths have been provided
    for path in EXPECTED_PATHS:
        if path not in parameters["filepaths"]:
            print("{0} is missing an '{1}' filepath!".format(config, path))
            quit()

    #Config parameters have been checked, now read into variables
    paths = parameters["filepaths"]
    extensions = paths["extensions"]
    hlsppath = paths["hlsppath"]
    output = paths["output"]
    overwrite = paths["overwrite"]
    header_type = parameters["header_type"]
    data_types = parameters["data_types"]
    uniques = parameters["unique_parameters"]

    #Set up logging
    outdir = os.path.dirname(output)
    logfile = os.path.join(outdir, LOG)
    logfile = cp.check_new_file(logfile)
    logging.basicConfig(filename=logfile,
                        format='***%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')

    #Prepare the output file
    output = cp.check_new_file(output)
    print("Opening {0}...".format(output))
    if overwrite or not os.path.isfile(output):
        with open(output, 'w') as xmlfile:
            xmlfile.close()
    else:
        logging.error("{0} already exists. Set overwrite=True to proceed."
                      .format(output))
        print("Aborting, see log!")
        quit()

    #Read the static CAOM values from the yaml file, begin a list of CAOMxml
    #elements.
    statics = cp.check_existing_file(STATICS)
    static_values = read_yaml(statics)
    xmllist = []
    xmllist = add_static_values(xmllist,
                                static_values,
                                data_types,
                                header_type)

    #Add information from the header keywords table.
    xmllist = add_header_entries(xmllist, KEYWORD_TABLE, header_type)

    #Add CAOMxml entries for HLSP-specifiic CAOM parameters.
    xmllist = add_value_caomxml(xmllist, uniques)

    #Begin the lxml tree and add the main subelements
    composite = etree.Element("CompositeObservation")
    xmltree = etree.ElementTree(composite)
    metadata = etree.SubElement(composite, "metadataList")
    provenance = etree.SubElement(composite, "provenance")
    products = etree.SubElement(composite, "productList")

    #Add the product list to the xml tree
    xmltree = add_productlist_xml(hlsppath, extensions, static_values, xmltree)

    #Create the head string to write to doctype
    head_strings = []
    head_strings.append("<!-- Process HLSP for CAOM ingestion -->")
    head_strings.append("")
    head = "\n".join(head_strings)

    #Add CAOMxml elements to xmltree with some final tweaks
    for entry in xmllist:
        if header_type == "kepler":
            if entry.label == "instrument_keywords" and entry.headerKeyword == "FILTER":
                entry.headerDefaultValue = "K"
        #Skip extra top-level entries caused by recursion in add_value_caomxml
        if xmltree.find(entry.label) is None:
            entry.send_to_lxml(xmltree)

    #Write the xml tree to the OUTPUT file
    #(doctype not a valid argument for python 2.x)
    xmltree.write(output, encoding="utf-8", xml_declaration=True, doctype=head,
               pretty_print=True)
    print("XML file generated!")

    #Print out log stats before finishing
    check_log(logfile)

#--------------------

if __name__ == "__main__":
    #User must provide a path to the yaml config file in order to run.
    try:
        config = sys.argv[1]
    except IndexError:
        print("hlsp_to_xml needs a filepath to yaml config file as well!")
        quit()

    hlsp_to_xml(config)
