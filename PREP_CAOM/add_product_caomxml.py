"""
..module:: add_productlist_xml
    :synopsis: Walk an HLSP directory (filepath) to identify all files.
    Compare the filenames found to a table of expected file extensions
    (extensions_table) and generate CAOM product entries with appropriate
    parameters.
"""

from CAOMxml import *
import util.check_paths as cp
import csv
import logging
import os

#--------------------

def add_product_caomxml(caomlist, filepath, extensions_table, data_types):
    """
    Walk filepath and create product entries for files by matching them with
    entries in extensions_table.

    :param filepath:  The path where all the files for the current HLSP are
    located.
    :type filepath:  string

    :param extensions_table:  The filepath for a .csv file specific to the
    current HLSP with file extensions expected to be found and corresponding
    CAOM product parameters to associate with them.
    :type extensions_table:  string

    :param tree:  The xml tree object to add product subelements to.
    :type tree:  _ElementTree from lxml
    """

    print("Generating the product list...")

    #Make sure filepaths are full and valid
    filepath = cp.check_existing_dir(filepath)
    extensions_table = cp.check_existing_file(extensions_table)

    #Read the extensions_table into a dictionary, ASSUMES extension name in
    #column 0.
    #[file extension : (n parameters...)]
    extensions = {}
    with open(extensions_table) as csvfile:
        csv_object = csv.reader(csvfile, delimiter=",")
        for row in csv_object:
            if len(row) <= 1:
                logging.error("Not enough columns in {0}"
                              .format(extensions_table))
                print("Aborting, see log!")
                quit()
            else:
                extensions[row[0]] = tuple(row[1:])
        csvfile.close()

    #Check that 'extension' is a valid key in the extensions dictionary,
    #otherwise it is not formatted correctly.
    try:
        ext_list = extensions['extension']
    except KeyError:
        logging.error("{0} needs 'extension' listed in column 0"
                      .format(extensions_table))
        print("Aborting, see log!")
        quit()

    try:
        pt_index = ext_list.index("productType")
        fs_index = ext_list.index("fileStatus")
    except KeyError:
        logging.error("{0} is missing a required parameter!"
                      .format(extensions_table))
        print("Aborting, see log!")
        quit()

    #Walk filepath and check files found against the list of defined
    #extensions.  If the extension matches, create a product subelement with
    #matching parameters.
    print("...scanning files from {0}...".format(filepath))
    found_extensions = []
    projects = []
    for path, subdirs, files in os.walk(filepath):
        #print("...adding files from {0}...".format(path))
        for name in files:
            #Look for a match with an entry in extensions and create a
            #CAOMproduct if found.  If the extension doesn't match one from
            #the .csv file, generate a warning in the log and skip the file.
            product = None
            for ext in extensions.keys():
                if name.lower().endswith(ext):
                    this_ext = extensions[ext]
                    product = CAOMproduct()
                    product.dataProductType = data_types.upper()
                    product.productType = this_ext[pt_index]
                    product.fileStatus = this_ext[fs_index]
                    found_extensions.append(ext)
                    del extensions[ext]
                    spl = str.split(name, "_")
                    if spl[0] == "hlsp" and spl[1] not in projects:
                        projects.append(spl[1])
                    break
            if product is None:
                found = False
                for e in found_extensions:
                    if name.lower().endswith(e):
                        found = True
                        break
                if not found:
                    logging.warning("Skipped {0}, extension not defined in {1}"
                                    .format(os.path.join(path, name),
                                    os.path.basename(extensions_table)))
                continue

            #Define statusAction depending on what fileStatus is assigned
            if product.fileStatus == "REQUIRED":
                product.statusAction = "ERROR"
            else:
                product.statusAction = "WARNING"

            #Get fileType and contentType by operating on the filename.
            #Assumes that the filename ends with '_abc' to denote file type.
            #Concatenates everything after the first '.' to get content type.
            full = name.split("_")
            end = full[-1]
            get_ext = end.split(".")
            fileType = get_ext[0]
            contentType = ".".join(get_ext[1:])
            product.fileType = fileType.upper()
            product.contentType = contentType.upper()
            print("...adding {0}...".format(product))
            caomlist.add(product)

            if len(extensions.keys()) == 0:
                print("...all defined extensions entered, still scanning...")

    if len(projects) == 1:
        name = CAOMvalue("name")
        name.parent = "provenance"
        name.value = projects[0].upper()
        caomlist.add(name)

    #Check for any remaining unused file extensions.  Dictionary will still
    #contain one 'extension' entry.
    if len(extensions) > 1:
        for ext in sorted(extensions):
            if ext == 'extension':
                continue
            else:
                logging.warning("{0} was defined in {1}, but none found in {2}"
                                .format(ext, extensions_table, filepath))

    print("...done!")
    return caomlist
