"""
..module:: add_productlist_xml
    :synopsis: Walk an HLSP directory (filepath) to create a list of all files.  Compare the filenames to a table of expected file extensions (extensions_table) and generate CAOM product entries with appropriate parameters.
"""

from lxml import etree
import csv
import logging
import os

#--------------------

def add_productlist_xml(filepath, extensions_table, tree):
    """
    Walk filepath and create product entries for files by matching them with entries in extensions_table.
    """

    parent = tree.find("productList")
    products = []
    filepath = os.path.abspath(filepath)
    extensions_table = os.path.abspath(extensions_table)

    extensions = {}
    with open(extensions_table) as csvfile:
        csv_object = csv.reader(csvfile, delimiter=",")
        for row in csv_object:
            extensions[row[0]] = tuple(row[1:])

    for path, subdirs, files in os.walk(filepath):
        for name in files:
            products.append(os.path.join(path, name))

    for filename in products:
        parameters = ["n/a"]*4
        for ext in extensions.keys():
            if filename.lower().endswith(ext):
                parameters = extensions[ext]
        if "n/a" in parameters:
            logging.warning("Skipped {}".format(filename))
            logging.warning("Extension not defined in {}".format(extensions_table))
            continue
        product = etree.SubElement(parent, "product")
        pn = etree.SubElement(product, "planeNumber")
        pn.text = parameters[0]
        cl = etree.SubElement(product, "calibrationLevel")
        cl.text = "HLSP"
        dpt = etree.SubElement(product, "dataProductType")
        dpt.text = parameters[1]
        pt = etree.SubElement(product, "productType")
        pt.text = parameters[2]
        rt = etree.SubElement(product, "releaseType")
        rt.text = "DATA"
        fnd = etree.SubElement(product, "fileNameDescriptor")
        fnd.text = "FILEROOT"
        ft = etree.SubElement(product, "fileType")
        ct = etree.SubElement(product, "contentType")
        ct.text = parameters[3]
        fs = etree.SubElement(product, "fileStatus")
        if parameters[0] == '1':
            fs.text = "REQUIRED"
        else:
            fs.text = "OPTIONAL"
        sa = etree.SubElement(product, "statusAction")
        if parameters[0] == '1':
            sa.text = "WARNING"
        else:
            sa.text = "IGNORE"
        pproj = etree.SubElement(product, "provenanceProject")
        pprod = etree.SubElement(product, "provenanceProducer")

    return tree
