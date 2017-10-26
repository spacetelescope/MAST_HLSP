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

    :param xmltree: The xml tree object to add light curve subelements to.
    :type xmltree: _ElementTree from lxml
    """

    statics_lightcurve = {"algorithm": "timeseries"}

    #Form the light curve elements to add
    print("Adding light curve information...")
    newtree = axe.add_value_subelements(xmltree,
                                        statics_lightcurve,
                                        "metadataList")

    #Write the modified ElementTree to file
    print("...done!")
    return newtree
    #tree.write(filepath, encoding="UTF-8", xml_declaration=True, pretty_print=True)

#--------------------
