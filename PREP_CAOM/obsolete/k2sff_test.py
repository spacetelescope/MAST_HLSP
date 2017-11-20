"""
k2sff test wrapper.
"""

from lxml import etree
from start_hlsp_xml import start_hlsp_xml
from add_lightcurve_xml import add_lightcurve_xml
from add_productlist_xml import add_productlist_xml
from check_log import check_log
import add_xml_entries as axe

#Set global variables
EXTENSIONS = "k2sff_extensions.csv"
HLSPPATH = "/ifs/archive/ops/mast/public/hlsp/k2sff/c102"
LOG = "results/k2sff_test.log"
OUTPUT = "results/k2sff_caom_test.xml"
TABLE = "hlsp_keywords_test.csv"
TYPE = "kepler"

#--------------------

def add_k2sff_xml(tree):
    metadata = tree.find("metadataList")
    provenance = tree.find("provenance")
    products = tree.find("productList")

    k2sff_provenance = {"name": "K2SFF",
                        "reference": "https://archive.stsci.edu/prepds/k2sff/"}

    tree = axe.add_value_subelements(tree, k2sff_provenance, "provenance")

    return tree

#--------------------

if __name__ == "__main__":

    #Create the xml file and add initial HLSP information
    tree = start_hlsp_xml(LOG, OUTPUT, TABLE, TYPE)

    #Add light curve HLSP information to the xml tree
    tree = add_lightcurve_xml(tree)

    #Add the product list to the xml tree
    tree = add_productlist_xml(HLSPPATH, EXTENSIONS, tree)

    #Add HLSP-specific information to the xml tree
    tree = add_k2sff_xml(tree)

    #Create the head string to write to doctype
    head_strings = []
    head_strings.append("<!-- Process HLSP for CAOM ingestion -->")
    head_strings.append("")
    head = "\n".join(head_strings)

    #Write the xml tree to the OUTPUT file
    tree.write(OUTPUT, encoding="UTF-8", xml_declaration=True, #doctype=head,
               pretty_print=True)
    print("XML file generated!")

    #Print out log stats before finishing
    check_log(LOG)
