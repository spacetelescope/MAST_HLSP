"""
..module:: add_value_caomxml
    :synopsis: Recursively translate entries in a dictionary to CAOMxml
    objects.  Empty CAOMxml objects are made for dictionaries of dictionaries,
    so users can create new parameters with any xml depth.  All CAOMxml
    objects are then added to xmllist and returned.
"""

from CAOMxml import *
from lxml import etree
import logging

#--------------------

def add_value_caomxml(xmllist, dictionary, parent="CompositeObservation"):
    """
    Create CAOMvalue objects from entries in a dictionary.  Recursive
    operation allows nested parameters.
    """
    for element in dictionary.keys():
        if isinstance(dictionary[element], dict):
            blank_entry = CAOMxml(element)
            blank_entry.parent = parent
            xmllist.append(blank_entry)
            xmllist = add_value_caomxml(xmllist, dictionary[element], element)
        else:
            new_entry = CAOMvalue(element)
            new_entry.parent = parent
            new_entry.value = dictionary[element]
            xmllist.append(new_entry)
    return xmllist
