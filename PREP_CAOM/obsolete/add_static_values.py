"""
..module:: add_static_values
    :synopsis: Given the full dictionary of possible static value xml entries,
    this module decides which portions to actually add to the caomlist based
    on various conditions.  (This is expected to grow as the list of static
    values does as well)
"""

import logging

from lib.CAOMxml import *

from util.add_value_caomxml import add_value_caomxml

#--------------------

def add_static_values(caomlist, statics, data_type, header_type):
    """ Add entries from the statics dictionary to the caomlist by looking at
    properties of data_type and header_type.  The add_value_caomxml module is
    used to actually create the CAOMxml objects and add them to the caomlist.
    """

    caomlist = add_value_caomxml(caomlist, statics["hlsp"])
    if data_type == "timeseries":
        caomlist = add_value_caomxml(caomlist, statics["timeseries"])
    if header_type == "kepler":
        caomlist = add_value_caomxml(caomlist, statics["kepler"])
    return caomlist
