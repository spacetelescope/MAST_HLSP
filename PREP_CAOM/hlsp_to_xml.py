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

-TABLE (filepath)
A general csv table translating CAOM metadata and provenance entries to fits
headers.

-TYPE (default, kepler)
The user must specify which set of fits header keywords are used for this HLSP.
"""

from lxml import etree
from start_hlsp_xml import start_hlsp_xml
from add_lightcurve_xml import add_lightcurve_xml
from add_productlist_xml import add_productlist_xml
from add_unique_xml import add_unique_xml
from util.check_log import check_log
import util.add_xml_entries as axe
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
                  "output"]
global LOG
LOG = "hlsp_to_xml.log"
global STATICS
STATICS = "resources/hlsp_caom_staticvalues.yaml"
global TABLE
TABLE = "resources/hlsp_keywords_test.csv"

#--------------------

if __name__ == "__main__":
    #User must provide a path to the yaml config file in order to run.
    try:
        config = sys.argv[1]
    except IndexError:
        print("hlsp_to_xml needs a filepath to yaml config file as well!")
        quit()
    config = os.path.abspath(config)

    #Try to open the yaml config file.
    try:
        stream = open(config, 'r')
        print("Opening {0}...".format(config))
    except FileNotFoundError:
        print("{0} does not exist!".format(config))
        quit()

    #Use yaml.load to read the contents into a dictionary.
    try:
        parameters = yaml.load(stream)
    except yaml.scanner.ScannerError:
        print("{0} is not a yaml formatted file!".format(config))
        quit()

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
    header_type = parameters["header_type"]
    types = parameters["data_types"]
    uniques = parameters["unique_parameters"]

    #Set up logging
    outdir = os.path.dirname(output)
    logfile = os.path.join(outdir, LOG)
    logfile = cp.check_new_file(logfile)
    logging.basicConfig(filename=logfile,
                        format='***%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')

    #Create the xml file and add initial HLSP information
    tree = start_hlsp_xml(output, STATICS, TABLE, header_type, overwrite=True)

    #Launch module for each data type specified in yaml config.
    data_types = []
    try:
        data_types.extend(types)
    except TypeError:
        print("No data_types listed in {0}".format(config))
        quit()
    for dt in data_types:
        if dt == "lightcurve":
            tree = add_lightcurve_xml(tree)
        elif dt == "spectrum" or dt == "sepctra" or dt == "spectral":
            pass
        elif dt == "catalog":
            pass
        elif dt == "simulation":
            pass
        elif dt == "model":
            pass
        else:
            logging.warning("Skipping '{0}' from 'data_types', not valid type."
                            .format(dt))

    #Add the product list to the xml tree
    tree = add_productlist_xml(hlsppath, extensions, tree)

    #Add HLSP-specifiic CAOM parameters to the xml tree
    tree = add_unique_xml(uniques, tree)

    #Create the head string to write to doctype
    head_strings = []
    head_strings.append("<!-- Process HLSP for CAOM ingestion -->")
    head_strings.append("")
    head = "\n".join(head_strings)

    #Write the xml tree to the OUTPUT file
    #(doctype not a valid argument for python 2.x)
    tree.write(output, encoding="utf-8", xml_declaration=True, #doctype=head,
               pretty_print=True)
    print("XML file generated!")

    #Print out log stats before finishing
    check_log(logfile)
