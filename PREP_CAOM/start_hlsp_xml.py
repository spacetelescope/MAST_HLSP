"""
..module:: open_xml_file
    :synopsis: Called from start_hlsp_xml.  Will either overwrite or create a new xml file.

..module:: get_header_keys
    :synopsis:  Called from start_hlsp_xml.  Given a filepath for a .csv keyword lookup table and a header type, will return a dictionary of CAOM entries with their associated header keywords.

..module:: start_hlsp_xml
    :synopsis: With a given filepath, create a new xml file for CAOM ingestion and add standard HLSP informaiton.

..moduleauthor:: Peter Forshay <pforshay@stsci.edu>
"""

from keywords import Keyword
from lxml import etree
import add_xml_entries as axe
import csv
import os

#--------------------

def open_xml_file(filepath, overwrite=True):
    """
    Will either overwrite or create a new xml file.
    """

    #Make sure the filepath is whole and create any necessary directories
    path = os.path.abspath(filepath)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print("Creating new directories...")
        except FileExistsError:
            pass

    #Check if this is a new file or if 'overwrite' is on before proceeding
    if overwrite or not os.path.isfile(path):
        with open(path, 'w') as xmlfile:
            xmlfile.close()
    else:
        print("The file you are trying to create already exists. Set overwrite=True if you wish to proceed.")

#--------------------

def get_header_keys(tablepath, header_type):
    """
    Parse a .csv file at tablepath, which contains the CAOM XML entry name and corresponding header keywords.  Create a dictionary for translating CAOM entry to a header keyword for a designated header type.
    """

    #Open the csv file and parse into a list
    print("Opening {}".format(tablepath))
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
        print("get_header_keys was passed an invalid header_type!")
        quit()

    #Create the header_keys dictionary and add an entry for each csv row
    header_keys = {}
    for row in keys[1:]:
        header_keys[row[caom_index]] = (row[section_index], row[key_index])

    return header_keys

#--------------------

def start_hlsp_xml(outpath, tablepath, header_type, overwrite=True):
    """
    Create a new xml file for CAOM ingestion and add standard HLSP information.

    :param outpath: Location and filename of new xml file to generate.

    :param overwrite: Flag to prevent existing file destruction.

    :type outpath: string

    :type overwrite: boolean (default = True)
    """

    #Get the designated xml file and path ready
    print("Opening {}...".format(outpath))
    open_xml_file(outpath, overwrite)

    #Get the appropriate keyword dictionary from the lookup table
    header_keys = get_header_keys(tablepath, header_type)

    #Create the head string to write to doctype
    head_strings = []
    head_strings.append("<!-- Process HLSP for CAOM ingestion -->")
    head_strings.append("")
    head = "\n".join(head_strings)

    #Form the xml body
    co = etree.Element("CompositeObservation")
    as_tree = etree.ElementTree(co)

    metadata = etree.SubElement(co, "metadataList")
    provenance = etree.SubElement(co, "provenance")
    products = etree.SubElement(co, "productList")
    statics_metadata = {"collection": "HLSP",
                        "observationID": "FILENAME",
                        "proposal_id": "FILEROOT",
                        "intent": "SCIENCE"}
    statics_provenance = {"project": "FILEROOT"}
    as_tree = axe.add_value_subelements(as_tree, statics_metadata, "metadataList")
    as_tree = axe.add_value_subelements(as_tree, statics_provenance, "provenance")
    as_tree = axe.add_header_subelements(as_tree, header_keys)

    #Write the xml body and doctype to file
    print("Writing document info to the new file...")
    return as_tree
    #as_tree.write(outpath, encoding="UTF-8", xml_declaration=True, doctype=head, pretty_print=True)

#--------------------
