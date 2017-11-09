"""
..module:: open_xml_file
    :synopsis: Called from start_hlsp_xml.  Will either overwrite or create a
    new xml file.

..module:: get_header_keys
    :synopsis:  Called from start_hlsp_xml.  Given a filepath for a .csv
    keyword lookup table and a header type, will return a dictionary of CAOM
    entries with their associated header keywords.

..module:: start_hlsp_xml
    :synopsis: With a given filepath, create a new xml file for CAOM ingestion
    and add standard HLSP informaiton.

..moduleauthor:: Peter Forshay <pforshay@stsci.edu>
"""

from CAOMxml import *
import util.add_xml_entries as axe
import logging

#--------------------

def add_static_values(xmllist, statics, data_types, header_type):

    #print("all statics = {0}".format(statics))
    xmllist = axe.add_value_caomxml(xmllist, statics["hlsp"])
    if "lightcurve" in data_types:
        xmllist = axe.add_value_caomxml(xmllist, statics["lightcurve"])
    return xmllist
