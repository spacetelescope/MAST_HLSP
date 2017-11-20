"""
..module:: add_static_values
    :synopsis: Given the full dictionary of possible static value xml entries,
    this module decides which portions to actually add to the xmllist based
    on various conditions.  (This is expected to grow as the list of static
    values does as well)
"""

from CAOMxml import *
from util.add_value_caomxml import add_value_caomxml
import logging

#--------------------

def add_static_values(xmllist, statics, data_types, header_type):
    """
    Add entries from the statics dictionary to the xmllist by looking at
    properties of data_types and header_type.  The add_value_caomxml module is
    used to actually create the CAOMxml objects and add them to the xmllist.
    """

    xmllist = add_value_caomxml(xmllist, statics["hlsp"])
    if "lightcurve" in data_types:
        xmllist = add_value_caomxml(xmllist, statics["lightcurve"])
    if header_type == "kepler":
        xmllist = add_value_caomxml(xmllist, statics["kepler"])
    return xmllist
