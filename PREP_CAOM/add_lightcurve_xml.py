"""
..module:: add_lightcurve_xml
    :synopsis: Add light curve information to an xml file for CAOM ingestion.

..moduleauthor:: Peter Forshay <pforshay@stsci.edu>
"""

from lxml import etree
import add_xml_entries as axe
import os

#--------------------

def add_lightcurve_xml(xmltree):
    """
    Add light curve information to an xml file for CAOM ingestion.

    :param filepath: Location and filename of new xml file to add to.

    :type filepath: string


    #Open the designated filepath and parse the xml file
    print("Reopening {}...".format(filepath))
    absfile = os.path.abspath(filepath)
    if not os.path.isfile(absfile):
        print("add_lightcurve_xml was not sent a valid filepath!")
        quit()
    with open(absfile) as xmlfile:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xmlfile, parser)
        xmlfile.close()
    """

    statics_lightcurve = {"algorithm": "timeseries"}

    #Form the light curve elements to add
    newtree = axe.add_value_subelements(xmltree, statics_lightcurve, "metadataList")

    #Write the modified ElementTree to file
    print("Adding light curve data...")
    return newtree
    #tree.write(filepath, encoding="UTF-8", xml_declaration=True, pretty_print=True)

#--------------------
