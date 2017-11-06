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

from lxml import etree
import util.add_xml_entries as axe
import util.check_paths as cp
import csv
import logging
import os
import yaml

#--------------------

def open_xml_file(filepath, overwrite=True):
    """
    Will either overwrite or create a new xml file.

    :param filepath:  Desired filepath for xml file creation.
    :type filepath:  string

    :param overwrite:  Flag to overwrite an existing xml file at the filepath
    location.  Defaults to True.
    :type overwrite:  boolean
    """

    #Check if this is a new file or if 'overwrite' is on before proceeding
    print("Opening {0}...".format(filepath))
    if overwrite or not os.path.isfile(filepath):
        with open(filepath, 'w') as xmlfile:
            xmlfile.close()
    else:
        logging.error("{0} already exists. Set overwrite=True to proceed."
                      .format(filepath))
        print("Aborting, see log!")
        quit()

#--------------------

def get_header_keys(tablepath, header_type):
    """
    Parse a .csv file at tablepath, which contains the CAOM XML entry name and
    corresponding header keywords.  Create a dictionary for translating CAOM
    entry to a header keyword for a designated header type.

    :param tablepath:  The filepath containing a .csv file with CAOM elements
    and corresponding xml parents and fits keywords.
    :type tablepath:  string

    :param header_type:  The type of fits header keywords used by this HLSP.
    Must match a column header in the .csv file at tablepath.
    :type header_type:  string
    """

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
    section_index = keys[0].index("section")
    try:
        key_index = keys[0].index(header_type)
    except ValueError:
        logging.error("'{0}' is not a header type defined in {1}"
                      .format(header_type, tablepath))
        print("Aborting, see log!")
        quit()

    #Create the header_keys dictionary and add an entry for each csv row
    #[CAOM: (PARENT, KEYWORD)]
    header_keys = {}
    for row in keys[1:]:
        if row[key_index] == "null":
            continue
        elif row[caom_index] in header_keys.keys():
            header_keys[row[caom_index]].append((row[section_index],
                                                 row[key_index]))
        else:
            header_keys[row[caom_index]] = [(row[section_index],
                                             row[key_index])]

    return header_keys

#--------------------

def start_hlsp_xml(outpath, statics, tablepath, header_type, overwrite=True):
    """
    Create a new xml file for CAOM ingestion and add standard HLSP information.

    :param outpath:  Location and filename of new xml file to generate.
    :type outpath:  string

    :param tablepath:  Location of the .csv file with translations from CAOM
    elements to fits header keywords.
    :type tablepath:  string

    :param header_type:  The type of fits header used by the current HLSP.
    Must match a column header in the tablepath .csv file.
    :type header_type:  string

    :param overwrite:  Flag to prevent existing file destruction.
    :type overwrite:  boolean (=True by default)
    """

    #Check output path sent from wrapper
    outpath = cp.check_new_file(outpath)

    #Get the designated xml file and path ready
    open_xml_file(outpath, overwrite)

    #Get the appropriate keyword dictionary from the lookup table
    #header_keys dictionary formatted as CAOM: (PARENT, KEYWORD)
    header_keys = get_header_keys(tablepath, header_type)

    #Form the xml body
    print("Adding general HLSP information...")
    composite = etree.Element("CompositeObservation")
    as_tree = etree.ElementTree(composite)
    metadata = etree.SubElement(composite, "metadataList")
    provenance = etree.SubElement(composite, "provenance")
    products = etree.SubElement(composite, "productList")
    hlsp_entries = statics["hlsp"]
    metadata = hlsp_entries["metadataList"]
    provenance = hlsp_entries["provenance"]
    if header_type == "kepler":
        kepler_entries = statics["kepler"]
        kepler_metadata = kepler_entries["metadataList"]
        metadata.update(kepler_metadata)
    as_tree = axe.add_value_subelements(as_tree,
                                        metadata,
                                        "metadataList")
    as_tree = axe.add_value_subelements(as_tree,
                                        provenance,
                                        "provenance")
    as_tree = axe.add_header_subelements(as_tree, header_keys)

    print("...done!")
    return as_tree

#--------------------
