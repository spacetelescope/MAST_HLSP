"""
..module:: add_product_caomxml
    :synopsis: Walk an HLSP directory (filepath) to identify all files.
    Compare the filenames found to a table of expected file extensions
    (extensions) and generate CAOM product entries with appropriate parameters.
"""

import csv
import logging
import os

from lib.CAOMxml import *

import util.check_paths as cp

#--------------------

def add_product_caomxml(caomlist, filepath, extensions, data_type):
    """ Walk filepath and create product entries for files by matching them
    with entries in extensions.

    :param caomlist:  The list of CAOMxml objects being aggregated to write
                      into XML.
    :type caomlist:  CAOMxmlList

    :param filepath:  The path where all the files for the current HLSP are
                      located.
    :type filepath:  str

    :param extensions:  A dictionary of file type suffixes with corresponding
                        productType values.
    :type extensions:  dict

    :param data_type:  The dataProductType to apply to all products created.
    :type data_type:  str
    """

    # Make sure filepaths are full and valid
    filepath = cp.check_existing_dir(filepath)

    # Walk filepath and check files found against the list of defined
    # extensions.  If the extension matches, create a product subelement with
    # matching parameters.
    print("...scanning files from {0}...".format(filepath))
    found_extensions = []
    projects = []
    for path, subdirs, files in os.walk(filepath):
        for name in files:

            # Look for a match with an entry in extensions and create a
            # CAOMproduct if found.  If the extension doesn't match one from
            # the .csv file, generate a warning in the log and skip the file.
            product = None
            for ext in extensions.keys():
                if name.lower().endswith(ext):
                    product = CAOMproduct()
                    product.dataProductType = data_type.upper()
                    product.productType = extensions[ext]
                    ext_split = ext.split(".")
                    product.fileType = ext_split[0].upper()
                    product.contentType = ".".join(ext_split[1:]).upper()
                    if product.contentType == "FITS":
                        product.fileStatus = "REQUIRED"
                        product.statusAction = "ERROR"
                    print("...adding {0}...".format(product))
                    found_extensions.append(ext)
                    caomlist.add(product)
                    del extensions[ext]

                    # Expect that the filename follows standard HLSP
                    # formatting: "hlsp_project_..."
                    spl = str.split(name, "_")
                    if spl[0] == "hlsp" and spl[1] not in projects:
                        projects.append(spl[1])
                    break

            # If the product is not found, check if it's because it's already
            # been found.  Otherwise, enter a warning in the log.
            if product is None:
                found = False
                for e in found_extensions:
                    if name.lower().endswith(e):
                        found = True
                        break
                if not found:
                    logging.warning("Skipped {0}, extension not defined."
                                    .format(os.path.join(path, name)))
                continue

            remaining = list(extensions.keys())
            if len(remaining) == 0:
                print("...all defined extensions entered, still scanning...")

    # If only one project name is found, set the "name" CAOM parameter to this
    # value.
    if len(projects) == 1:
        name = CAOMvalue("name")
        name.parent = "provenance"
        name.value = projects[0].upper()
        caomlist.add(name)

    # Check for any remaining unused file extensions.
    if len(extensions) > 0:
        for ext in sorted(extensions):
            logging.warning("{0} was defined, but none found in {1}"
                            .format(ext, filepath))

    return caomlist
