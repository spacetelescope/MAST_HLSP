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
import logging
import os

#--------------------

def merge_dictionaries(current_dict, new_dict):
    if "metadataList" in current_dict:
        current_metadata = current_dict["metadataList"]
    else:
        current_metadata = {}
    if "provenance" in current_dict:
        current_provenance = current_dict["provenance"]
    else:
        current_provenance = {}
    if "metadataList" in new_dict:
        new_metadata = new_dict["metadataList"]
    else:
        new_metadata = {}
    if "provenance" in new_dict:
        new_provenance = new_dict["provenance"]
    else:
        new_provenance = {}
    current_metadata.update(new_metadata)
    current_provenance.update(new_provenance)
    merged = {"metadataList": current_metadata,
              "provenance": current_provenance}
    return merged

#--------------------

def add_static_values(xmltree, statics, data_types, header_type):
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

    #Form the xml body
    print("Adding static HLSP information...")
    static_entries = statics["hlsp"]

    if header_type == "kepler":
        try:
            kepler_entries = statics["kepler"]
            static_entries = merge_dictionaries(static_entries, kepler_entries)
        except KeyError:
            logging.info("No Kepler static information found.")

    for dt in data_types:
        if dt == "lightcurve":
            lightcurve_entries = statics["lightcurve"]
            static_entries = merge_dictionaries(static_entries,
                                                lightcurve_entries)
        elif dt == "spectrum" or dt == "sepctra" or dt == "spectral":
            pass
        elif dt == "catalog":
            pass
        elif dt == "simulation":
            pass
        elif dt == "model":
            pass
        else:
            logging.warning("Skipping '{0}' from 'data_types', not valid type."
                            .format(dt))

    xmltree = axe.add_value_subelements(xmltree,
                                        static_entries["metadataList"],
                                        "metadataList")
    xmltree = axe.add_value_subelements(xmltree,
                                        static_entries["provenance"],
                                        "provenance")

    print("...done!")
    return xmltree

#--------------------
