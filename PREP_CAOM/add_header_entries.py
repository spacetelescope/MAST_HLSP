"""
..module:: add_header_entries
    :synopsis: This module opens a .csv file provided through tablepath, which
    contains a translation table of CAOM XML elements to various FITS header
    keyword standards.  The type of keywords used is determined by header_type.
    The module then creates a CAOMxml object for each appropriate table entry,
    and adds these objects to the xmllist.
"""

from CAOMxml import *
import util.check_paths as cp
import csv
import logging

#--------------------

def add_header_entries(caomlist, tablepath, header_type):

    #Open the csv file and parse into a list
    tablepath = cp.check_existing_file(tablepath)
    print("...opening {0}...".format(tablepath))
    keywords = []
    with open(tablepath) as csvfile:
        hlsp_keys = csv.reader(csvfile, delimiter=",")
        for row in hlsp_keys:
            keywords.append(row)
        csvfile.close()

    #Get the indices for the section value, CAOM XML value, the name of the
    #header containing this keyword, and the designated header type.
    caom_index = keywords[0].index("caom")
    header_index = keywords[0].index("headerName")
    section_index = keywords[0].index("section")
    try:
        key_index = keywords[0].index(header_type)
    except ValueError:
        logging.error("'{0}' is not a header type defined in {1}"
                      .format(header_type, tablepath))
        print("Aborting, see log!")
        quit()

    #Create a CAOMxml object for each entry in the table (skipping the head
    #row and 'null' entries).  Add each CAOMxml object to caomlist.
    for row in keywords[1:]:
        if row[key_index] == "null":
            continue
        else:
            caom_parameter = row[caom_index]
            new_entry = CAOMheader(caom_parameter)
            new_entry.parent = row[section_index]
            new_entry.headerName = row[header_index]
            new_entry.headerKeyword = row[key_index]

            #Adjust default values as needed.  CAOMheader defaults to 'None'.
            if caom_parameter == "targetPosition_equinox":
                new_entry.headerDefaultValue = "2000.0"
            elif caom_parameter == "targetPosition_coordsys":
                new_entry.headerDefaultValue = "ICRS"

            if header_type == "kepler":
                if new_entry.headerKeyword == "FILTER":
                    new_entry.headerDefaultValue = "Kepler"
                elif new_entry.headerKeyword == "EXPTIME":
                    new_entry.headerDefaultValue = "1800"

            caomlist.add(new_entry)

    return caomlist
