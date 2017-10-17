"""
..module:: add_lightcurve_xml
    :synopsis: Add light curve information to an xml file for CAOM ingestion.

..moduleauthor:: Peter Forshay <pforshay@stsci.edu>
"""

from lxml import etree
import os
import sys

#--------------------

def add_lightcurve_xml(filepath):
    """
    Add light curve information to an xml file for CAOM ingestion.

    :param filepath: Location and filename of new xml file to add to.

    :type filepath: string
    """

    #Open the designated filepath and parse the xml file
    print("Reopening {}...".format(filepath))
    absfile = os.path.abspath(filepath)
    if not os.path.isfile(absfile):
        print("add_lightcurve_xml was not sent a valid XML file!")
        sys.exit()
    with open(absfile) as xmlfile:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xmlfile, parser)
        xmlfile.close()

    #Form the light curve elements to add
    root = tree.getroot()
    lightcurve = etree.SubElement(root, "lightCurve")
    data1 = etree.SubElement(lightcurve, "Data")
    data1.text = "1"
    data2 = etree.SubElement(lightcurve, "Data")
    data2.text = "2"

    #Write the modified ElementTree to file
    print("Adding light curve data...")
    tree.write(filepath, encoding="UTF-8", xml_declaration=True,
               pretty_print=True)

#--------------------
