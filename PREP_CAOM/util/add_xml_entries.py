"""
..module:: add_value_subelements
    :synopsis:  With an XML tree, this module will create a SubElement under a
    given parent for each entry in a passed dictionary (subelements) with CAOM
    VALUE formatting.

..module:: add_header_subelements
    :synopsis:  With an XML tree, this module will create a SubElement under a
    given parent for each entry in a passed dictionary (subelements) with CAOM
    HEADER formatting.
"""

from lxml import etree
import logging

#--------------------

def new_add_value_subelements(xmltree, subelements):
    for parent in subelements:
        print("Finding {0}".format(parent))
        section = xmltree.find(parent)
        subset = subelements[parent]
        for value in sorted(subset):
            new_subelement = etree.SubElement(section, value)
            source = etree.SubElement(new_subelement, "source")
            source.text = "VALUE"
            value = etree.SubElement(new_subelement, "value")
            value.text = subset[value]
    return xmltree

def add_value_subelements(xmltree, subelements, parent):
    """
    Adds SubElements from a dictionary to xmltree under a designated parent in
    the CAOM VALUE formatting.

    :param xmltree:  The xml tree object this function will add subelements
    into.
    :type xmltree:  _ElementTree from lxml

    :param subelements:  All the subelements and corresponding keywords to be
    added to the xml tree.
    :type subelements:  dictionary

    :param parent:  The element or subelement to create new subelements for
    with this function.
    :type parent:  string
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
    Adds SubElements from a dictionary to xmltree under a designated parent in
    the CAOM HEADER formatting.  Parents are expected to be defined within the
    subelements dictionary [CAOM: (PARENT, KEYWORD)]

    :param xmltree:  The xml tree object this function will add subelements
    into.
    :type xmltree:  _ElementTree from lxml

    :param subelements:  All the subelements and corresponding keywords to be
    added to the xml tree.
    :type subelements:  dictionary
    """

    #Create a SubElement for each entry in the subelements dictionary
    for key in sorted(subelements):
        for entry in subelements[key]:
            #Extract elements from tuple
            parent = entry[0]
            header_keyword = entry[1]

            #Some header schemes don't use certain keywords
            if header_keyword == "null":
                continue

            #Find parent and create new subelement
            section = xmltree.find(parent)
            new_subelement = etree.SubElement(section, key)
            source = etree.SubElement(new_subelement, "source")
            source.text = "HEADER"
            header_name = etree.SubElement(new_subelement, "headerName")
            header_name.text = "PRIMARY"
            keyword = etree.SubElement(new_subelement, "headerKeyword")
            keyword.text = header_keyword

            #Handle different default value cases
            if key == "targetPosition_equinox":
                default = "2000.0"
            elif key == "targetPosition_coordsys":
                default = "ICRS"
            else:
                default = "None"
            default_value = etree.SubElement(new_subelement,
                                             "headerDefaultValue")
            default_value.text = default

    return xmltree
