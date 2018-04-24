"""
..module:: add_header_entries
    :synopsis: This module opens a .csv file provided through tablepath, which
    contains a translation table of CAOM XML elements to various FITS header
    keyword standards.  The type of keywords used is determined by header_type.
    The module then creates a CAOMxml object for each appropriate table entry,
    and adds these objects to the xmllist.
"""

import csv
import logging

from lib.CAOMxml import *

import util.check_paths as cp

#--------------------

def add_header_entries(caomlist, tablepath, header_type):
    """ Read the .fits header keyword translation table and create CAOMheader
    objects for each matching header_type.

    :param caomlist:  The list of CAOMxml objects being aggregated to write
                      into XML.
    :type caomlist:  CAOMxmlList

    :param tablepath:  The file path to the .csv table linking CAOM parameters
                       to .fits header keywords.
    :type tablepath:  str

    :param header_type:  The type of headers expected for this HLSP, defined
                         in the config file.
    :type header_type:  str
    """

    # Open the csv file and parse into a list
    tablepath = cp.check_existing_file(tablepath)
    if tablepath is None:
        print("*** No header keywords added")
        return caomlist
    print("...opening {0}...".format(tablepath))
    keywords = []
    with open(tablepath) as csvfile:
        hlsp_keys = csv.reader(csvfile, delimiter=",")
        for row in hlsp_keys:
            keywords.append(row)
        csvfile.close()

    # Get the indices for the section value, CAOM XML value, the name of the
    # header containing this keyword, and the designated header type.
    caom_index = keywords[0].index("caom")
    header_index = keywords[0].index("headerName")
    section_index = keywords[0].index("section")
    try:
        key_index = keywords[0].index(header_type)
    except ValueError:
        err = "'{0}' is not a header type defined in {1}".format(header_type,
                                                                 tablepath)
        logging.error(err)
        print(err)
        return caomlist

    # Create a CAOMxml object for each entry in the table (skipping the head
    # row and 'null' entries).  Add each CAOMxml object to caomlist.
    for row in keywords[1:]:
        key = row[key_index]
        if key is None or key == "null":
            continue
        else:
            caom_parameter = row[caom_index]
            new_entry = CAOMheader(caom_parameter)
            new_entry.parent = row[section_index]
            new_entry.headerName = row[header_index]
            new_entry.headerKeyword = row[key_index]
            caomlist.add(new_entry)

    return caomlist
