"""
..module:: add_value_subelements
    :synopsis:  With an XML tree, this module will create a SubElement under a given parent for each entry in a passed dictionary (subelements) with CAOM VALUE formatting.

..module:: add_header_subelements
    :synopsis:  With an XML tree, this module will create a SubElement under a given parent for each entry in a passed dictionary (subelements) with CAOM HEADER formatting.
"""

from lxml import etree
import logging

#--------------------

def add_value_subelements(xmltree, subelements, parent):
    """
    Adds SubElements from a dictionary to xmltree under a designated parent in the CAOM VALUE formatting.
    """

    #Find the parent section
    section = xmltree.find(parent)

    #Create a SubElement for each entry in the subelements dictionary
    for key in sorted(subelements):
        new_subelement = etree.SubElement(section, key)
        source = etree.SubElement(new_subelement, "source")
        source.text = "VALUE"
        value = etree.SubElement(new_subelement, "value")
        value.text = subelements[key]

    return xmltree

#--------------------

def add_header_subelements(xmltree, subelements):
    """
    Adds SubElements from a dictionary to xmltree under a designated parent in the CAOM HEADER formatting.  Parents are expected to be defined within the subelements dictionary [CAOM: (PARENT, KEYWORD)]
    """

    try:
        assert len(list(subelements.values())[0]) == 2
    except AssertionError:
        logging.error("The 'subelements' dictionary passed to add_header_subelements is not constructed correctly- [CAOM: (PARENT, KEYWORD)]")
        print("Aborting, see log!")
        quit()

    #Create a SubElement for each entry in the subelements dictionary
    for key in sorted(subelements):
        parent = subelements[key][0]
        section = xmltree.find(parent)
        new_subelement = etree.SubElement(section, key)
        source = etree.SubElement(new_subelement, "source")
        source.text = "HEADER"
        header_name = etree.SubElement(new_subelement, "headerName")
        header_name.text = "PRIMARY"
        keyword = etree.SubElement(new_subelement, "headerKeyword")
        keyword.text = subelements[key][1]
        default_value = etree.SubElement(new_subelement, "headerDefaultValue")
        default_value.text = "None"

    return xmltree
