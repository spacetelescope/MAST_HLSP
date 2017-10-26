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

-OUTPUT (filepath)
Desired filepath for the final XML result output.

-TABLE (filepath)
A general csv table translating CAOM metadata and provenance entries to fits
headers.

-TYPE (default, kepler)
The user must specify which set of fits header keywords are used for this HLSP.

..module::  add_unique_xml
    :synopsis:  Adds CAOM parameters that are unique to this HLSP.
"""

import add_xml_entries as axe
from lxml import etree
from start_hlsp_xml import start_hlsp_xml
from add_lightcurve_xml import add_lightcurve_xml
from add_productlist_xml import add_productlist_xml

#Set global variables
EXTENSIONS = "fake_hlsp_extensions.csv"
HLSPPATH = "../../hlsp_data"
OUTPUT = "../../COOL/ididit.xml"
TABLE = "hlsp_keywords_test.csv"
TYPE = "kepler"

#--------------------

def add_unique_xml(tree):
    """
    Add CAOM parameters that are unique to this HLSP.

    :param tree:  The xml tree object that these subelements will be added to.
    :type tree:  _ElementTree from lxml
    """

    print("Adding unique HLSP information...")

    #Define the parents to look for
    metadata = "metadataList"
    provenance = "provenance"
    products = "productList"

    hlsp_provenance = {"name": "<!--HLSP name-->",
                       "reference": "<!--HLSP url-->"}

    tree = axe.add_value_subelements(tree, hlsp_provenance, provenance)

    print("...done!")
    return tree

#--------------------

if __name__ == "__main__":

    #Create the xml file and add initial HLSP information
    tree = start_hlsp_xml(OUTPUT, TABLE, TYPE)

    #Add light curve HLSP information to the xml tree
    tree = add_lightcurve_xml(tree)

    #Add the product list to the xml tree
    tree = add_productlist_xml(HLSPPATH, EXTENSIONS, tree)

    #Add HLSP-specifiic CAOM parameters to the xml tree
    tree = add_unique_xml(tree)

    #Create the head string to write to doctype
    head_strings = []
    head_strings.append("<!-- Process HLSP for CAOM ingestion -->")
    head_strings.append("")
    head = "\n".join(head_strings)

    #Write the xml tree to the OUTPUT file
    tree.write(OUTPUT, encoding="utf-8", xml_declaration=True, #doctype=head,
               pretty_print=True)
    print("XML file generated!")
