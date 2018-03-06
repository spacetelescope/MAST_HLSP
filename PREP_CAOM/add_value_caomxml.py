"""
..module:: add_value_caomxml
    :synopsis: Recursively translate entries in a dictionary to CAOMxml
    objects.  Empty CAOMxml objects are made for dictionaries of dictionaries,
    so users can create new parameters with any xml depth.  All CAOMxml
    objects are then added to caomlist and returned.
"""

from lib.CAOMxml import *
from lxml import etree
import logging

#--------------------

def add_value_caomxml(caomlist, dictionary, parent="CompositeObservation"):
    """ Create CAOMvalue objects from entries in a dictionary.  Recursive
    operation allows nested parameters.

    :param caomlist:  The list of CAOMxml objects being aggregated to write
                      into XML.
    :type caomlist:  CAOMxmlList

    :param dictionary:  The dictionary to create CAOMvalue objects for.
    :type dictionary:  dict

    :param parent:  The parent to assign to created CAOMvalue objects.
                    Defaults to 'CompositeObservation'.
    :type parent:  str
    """

    for element in dictionary.keys():

        # If the current element is another dictionary, get a new parent and
        # send back to add_value_caomxml
        if isinstance(dictionary[element], dict):
            if not element == "CompositeObservation":
                blank_entry = CAOMxml(element)
                blank_entry.parent = parent
                caomlist.add(blank_entry)
            caomlist = add_value_caomxml(caomlist,
                                         dictionary[element],
                                         element)

        # If the current element is not a dictionary, use it to make a
        # CAOMvalue object
        else:
            existing = caomlist.findlabel(element)

            # If the current element is not already in caomlist, make a new
            # CAOMvalue object, set the parameters, and add it to caomlist.
            if existing is None:
                new_entry = CAOMvalue(element)
                new_entry.parent = parent
                new_entry.value = dictionary[element]
                caomlist.add(new_entry)

            # If the current element already exists, just update the parent
            # and value parameters.
            else:
                existing.parent = parent
                existing.value = dictionary[element]

    return caomlist
