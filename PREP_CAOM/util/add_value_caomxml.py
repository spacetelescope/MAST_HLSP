"""
..module:: add_value_caomxml
    :synopsis: Recursively translate entries in a dictionary to CAOMxml
    objects.  Empty CAOMxml objects are made for dictionaries of dictionaries,
    so users can create new parameters with any xml depth.  All CAOMxml
    objects are then added to caomlist and returned.
"""

from CAOMxml import *
from lxml import etree
import logging

#--------------------

def add_value_caomxml(caomlist, dictionary, parent="CompositeObservation"):
    """
    Create CAOMvalue objects from entries in a dictionary.  Recursive
    operation allows nested parameters.
    """

    for element in dictionary.keys():
        if isinstance(dictionary[element], dict):
            if not element == "CompositeObservation":
                blank_entry = CAOMxml(element)
                blank_entry.parent = parent
                caomlist.add(blank_entry)
            caomlist = add_value_caomxml(caomlist,
                                         dictionary[element],
                                         element)
        else:
            existing = caomlist.findlabel(element)
            if existing is not None:
                existing.parent = parent
                existing.value = dictionary[element]
                #print("Updated existing: {0}".format(existing))
            else:
                new_entry = CAOMvalue(element)
                new_entry.parent = parent
                new_entry.value = dictionary[element]
                caomlist.add(new_entry)
                #print("Made a new entry: {0}".format(new_entry))
    return caomlist
