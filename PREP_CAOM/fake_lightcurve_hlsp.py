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
from check_log import check_log
import add_xml_entries as axe
import check_paths as cp
import logging
import os
import sys
import yaml

#Set global variables
global LOG
LOG = "hlsp_to_xml.log"
global STATICS
STATICS = "hlsp_caom_staticvalues.yaml"
global TABLE
TABLE = "hlsp_keywords_test.csv"

#--------------------

if __name__ == "__main__":
    #Read in the user-made yaml config file and set variables
    try:
        config = sys.argv[1]
    except IndexError:
        print("hlsp_to_xml needs a filepath to yaml config file as well!")
        quit()
    config = os.path.abspath(config)
    try:
        stream = open(config, 'r')
        print("Opening {0}...".format(config))
    except FileNotFoundError:
        print("{0} does not exist!".format(config))
        quit()
    try:
        parameters = yaml.load(stream)
    except yaml.scanner.ScannerError:
        print("{0} is not a yaml formatted file!".format(config))
        quit()
    try:
        paths = parameters["filepaths"]
    except TypeError:
        print("{0} is missing 'filepaths'!".format(config))
        quit()
    try:
        extensions = paths["extensions"]
    except KeyError:
        print("{0} is missing 'extensions'!".format(config))
        quit()
    try:
        hlsppath = paths["hlsppath"]
    except KeyError:
        print("{0} is missing 'hlsppath'!".format(config))
        quit()
    try:
        output = paths["output"]
    except KeyError:
        print("{0} is missing 'output'!".format(config))
        quit()
    outdir = os.path.dirname(output)
    logfile = os.path.join(outdir, LOG)
    logfile = cp.check_new_file(logfile)
    try:
        header_type = parameters["header_type"]
    except KeyError:
        print("{0} is missing 'header_type'!".format(config))
        quit()
    try:
        uniques = parameters["unique_parameters"]
    except KeyError:
        print("{0} is missing 'unique_parameters'!".format(config))
        quit()

    #Set up logging
    logging.basicConfig(filename=logfile,
                        format='***%(levelname)s from %(module)s: %(message)s',
                        level=logging.DEBUG, filemode='w')

    #Create the xml file and add initial HLSP information
    tree = start_hlsp_xml(output, STATICS, TABLE, header_type,
                          overwrite=True)

    #Launch module for each data type specified in yaml config.
    data_types = []
    data_types.extend(parameters["data_types"])
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
    #doctype not a valid argument for python 2.x
    tree.write(output, encoding="utf-8", xml_declaration=True, #doctype=head,
               pretty_print=True)
    print("XML file generated!")

    #Print out log stats before finishing
    check_log(logfile)
