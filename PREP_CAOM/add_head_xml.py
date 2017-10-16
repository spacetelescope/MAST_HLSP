"""
..module:: add_head_xml
    :synopsis: With a given filepath, create a new xml file for CAOM ingestion and add standard HLSP informaiton.

..moduleauthor:: Peter Forshay <pforshay@stsci.edu>
"""

from lxml import etree

#--------------------

def add_head_xml(filepath):
    """
    Create a new xml file for CAOM ingestion and add standard HLSP information.

    :param filepath: Location and filename of new xml file to generate.

    :type filepath: string
    """

#--------------------
