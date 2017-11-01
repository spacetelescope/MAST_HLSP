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

import add_xml_entries as axe
from lxml import etree
from start_hlsp_xml import start_hlsp_xml
from add_lightcurve_xml import add_lightcurve_xml
from add_productlist_xml import add_productlist_xml
from add_unique_xml import add_unique_xml
from check_log import check_log
import os
import sys
import yaml

#Set global variables
global LOG
LOG = "results/hlsp_to_xml.log"
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
        print("{0} is not a yaml formatted file!".format(config))
        quit()
    try:
        extensions = paths["extensions"]
    except KeyError:
        print("{0} is missing 'extensions'!".format(config))
        quit()
    hlsppath = paths["hlsppath"]
    output = paths["output"]
    header_type = parameters["header_type"]
    uniques = parameters["unique_parameters"]

    #Create the xml file and add initial HLSP information
    tree = start_hlsp_xml(LOG, output, STATICS, TABLE, header_type,
                          overwrite=True)

    #Add light curve HLSP information to the xml tree
    tree = add_lightcurve_xml(tree)

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
    tree.write(output, encoding="utf-8", xml_declaration=True, #doctype=head,
               pretty_print=True)
    print("XML file generated!")

    #Print out log stats before finishing
    check_log(LOG)
