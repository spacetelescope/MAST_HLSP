"""
This is a template for the wrapper script to create an XML file for ingestion
into CAOM.  This script will need to be created individually for each HLSP, so
we try to keep this as light as possible. We will create as much of the XML as
possible with library scripts and cover remaining corner cases manually here.

Global variables:
-EXTENSIONS (filepath)
An HLSP-specific csv table of expected file extensions and corresponding CAOM
product parameters.

-HLSPPATH (filepath)
Where the HLSP files reside.

-LOG (filepath)
Desired filepath to save log entries.

-OUTPUT (filepath)
Desired filepath for the final XML result output.

-KEYWORD_TABLE (filepath)
A general csv table translating CAOM metadata and provenance entries to fits
headers.

-TYPE (default, kepler)
The user must specify which set of fits header keywords are used for this HLSP.
"""

from lxml import etree
from add_header_entries import add_header_entries
from add_productlist_xml import add_productlist_xml
from add_static_values import add_static_values
from add_unique_xml import add_unique_xml
from util.check_log import check_log
from util.fudge_for_kepler import fudge_for_kepler
from util.read_yaml import read_yaml
import util.add_xml_entries as axe
import util.check_paths as cp
from CAOMxml import *
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

if __name__ == "__main__":
    #User must provide a path to the yaml config file in order to run.
    try:
        config = sys.argv[1]
    except IndexError:
        print("hlsp_to_xml needs a filepath to yaml config file as well!")
        quit()
    config = cp.check_existing_file(config)

    #Try to read in the yaml config file.
    parameters = read_yaml(config)

    #Make sure the config file has all the expected sections
    for section in EXPECTED_CONFIGS:
        if not section in parameters:
            print("{0} does not define '{1}'!".format(config, section))
            quit()

    #Make sure all necessary filepaths have been provided
    for path in EXPECTED_PATHS:
        if not path in parameters["filepaths"]:
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

    #Begin the lxml tree and add the main subelements
    composite = etree.Element("CompositeObservation")
    xmltree = etree.ElementTree(composite)
    metadata = etree.SubElement(composite, "metadataList")
    provenance = etree.SubElement(composite, "provenance")
    products = etree.SubElement(composite, "productList")

    #Read the static CAOM values from the yaml file, and add to the tree.
    statics = cp.check_existing_file(STATICS)
    static_values = read_yaml(statics)
    xmltree = add_static_values(xmltree, static_values, data_types, header_type)

    #Add information from the header keywords table.
    xmltree = add_header_entries(xmltree, KEYWORD_TABLE, header_type)

    #Add the product list to the xml tree
    xmltree = add_productlist_xml(hlsppath, extensions, static_values, xmltree)

    #Add HLSP-specifiic CAOM parameters to the xml tree
    xmltree = add_unique_xml(uniques, xmltree)

    if header_type == "kepler":
        xmltree = fudge_for_kepler(xmltree)

    #Create the head string to write to doctype
    head_strings = []
    head_strings.append("<!-- Process HLSP for CAOM ingestion -->")
    head_strings.append("")
    head = "\n".join(head_strings)

    #TESTING
    xmltree = axe.update_xml_entry(xmltree, "FILTER", "headerDefaultValue", "DARP")
    test = CAOMxml("test")
    test.parent = "NOPE"
    test.source = "VALUE"
    test.value = "HUGE"
    test.send_to_lxml(xmltree)

    #Write the xml tree to the OUTPUT file
    #(doctype not a valid argument for python 2.x)
    xmltree.write(output, encoding="utf-8", xml_declaration=True, doctype=head,
               pretty_print=True)
    print("XML file generated!")

    #Print out log stats before finishing
    check_log(logfile)
