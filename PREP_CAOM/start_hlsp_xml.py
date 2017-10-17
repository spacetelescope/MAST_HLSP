"""
..module:: open_xml_file
    :synopsis: Called from start_hlsp_xml.  Will either overwrite or create a new xml file.

..module:: start_hlsp_xml
    :synopsis: With a given filepath, create a new xml file for CAOM ingestion and add standard HLSP informaiton.

..moduleauthor:: Peter Forshay <pforshay@stsci.edu>
"""

from lxml import etree
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

def start_hlsp_xml(filepath, overwrite=True):
    """
    Create a new xml file for CAOM ingestion and add standard HLSP information.

    :param filepath: Location and filename of new xml file to generate.

    :param overwrite: Flag to prevent existing file destruction.

    :type filepath: string

    :type overwrite: boolean (default = True)
    """

    #Get the designated xml file and path ready
    print("Opening {}...".format(filepath))
    open_xml_file(filepath, overwrite)

    #Create the head string to write to doctype
    head_strings = []
    head_strings.append("<!-- Process HLSP for CAOM ingestion -->")
    head_strings.append("")
    head = "\n".join(head_strings)

    #Form the xml body
    co = etree.Element("CompositeObservation")
    metadata = etree.SubElement(co, "metadataList")
    collection = etree.SubElement(metadata, "Collection")
    obsid = etree.SubElement(metadata, "observationID")
    mrelease = etree.SubElement(metadata, "metaRelease")

    #Write the xml body and doctype to file
    print("Writing document info to the new file...")
    as_tree = etree.ElementTree(co)
    as_tree.write(filepath, encoding="UTF-8", xml_declaration=True, doctype=head, pretty_print=True)

#--------------------
