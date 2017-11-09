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
import util.check_paths as cp
import csv
import logging

#--------------------

def add_header_entries(xmllist, tablepath, header_type):

    #Open the csv file and parse into a list
    tablepath = cp.check_existing_file(tablepath)
    print("Opening {0}...".format(tablepath))
    keys = []
    with open(tablepath) as csvfile:
        hlsp_keys = csv.reader(csvfile, delimiter=",")
        for row in hlsp_keys:
            keys.append(row)
        csvfile.close()

    #Get the indices for the section value, CAOM XML value, and designated
    #header type
    caom_index = keys[0].index("caom")
    header_index = keys[0].index("headerName")
    section_index = keys[0].index("section")
    try:
        key_index = keys[0].index(header_type)
    except ValueError:
        logging.error("'{0}' is not a header type defined in {1}"
                      .format(header_type, tablepath))
        print("Aborting, see log!")
        quit()

    for row in keys[1:]:
        if row[key_index] == "null":
            continue
        else:
            caom_parameter = row[caom_index]
            new_entry = CAOMxml(caom_parameter)
            new_entry.parent = row[section_index]
            new_entry.source = "HEADER"
            new_entry.headerName = row[header_index]
            new_entry.headerKeyword = row[key_index]
            if caom_parameter == "targetPosition_equinox":
                new_entry.headerDefaultValue = "2000.0"
            elif caom_parameter == "targetPosition_coordsys":
                new_entry.headerDefaultValue = "ICRS"
            else:
                new_entry.headerDefaultValue = "None"
            xmllist.append(new_entry)

    return xmllist
