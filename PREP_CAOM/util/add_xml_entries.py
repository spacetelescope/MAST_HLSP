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

from CAOMxml import CAOMxml
from lxml import etree
import logging

def add_value_caomxml(xmllist, dictionary):
    for section in dictionary.keys():
        section_dict = dictionary[section]
        for element in section_dict.keys():
            new_entry = CAOMxml(element)
            new_entry.parent = section
            new_entry.source = "VALUE"
            new_entry.value = section_dict[element]
            xmllist.append(new_entry)
    return xmllist
