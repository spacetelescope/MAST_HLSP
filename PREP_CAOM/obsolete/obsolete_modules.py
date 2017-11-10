
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

def add_header_entries(xmltree, tablepath, header_type):
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
    header_index = keys[0].index("headerName")
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
    print("Adding header keyword entries...")
    header_keys = {}
    for row in keys[1:]:
        keyword = row[key_index]
        parent = row[section_index]
        caom_parameter = row[caom_index]
        header_name = row[header_index]
        new_set = (parent, header_name, keyword)
        if keyword == "null":
            continue
        elif caom_parameter in header_keys.keys():
            header_keys[caom_parameter].append(new_set)
        else:
            header_keys[caom_parameter] = [new_set]


    xmltree = axe.add_header_subelements(xmltree, header_keys)

    print("...done!")
    return xmltree

#--------------------

def add_value_subelements(xmltree, subelements, parent):
    """
    Adds SubElements from a dictionary to xmltree under a designated parent in
    the CAOM VALUE formatting.

    :param xmltree:  The xml tree object this function will add subelements
    into.
    :type xmltree:  _ElementTree from lxml

    :param subelements:  All the subelements and corresponding keywords to be
    added to the xml tree.
    :type subelements:  dictionary

    :param parent:  The element or subelement to create new subelements for
    with this function.
    :type parent:  string
    """

    #Find the parent section
    section = xmltree.find(parent)

    #Create a SubElement for each entry in the subelements dictionary
    for key in sorted(subelements):
        new_subelement = etree.SubElement(section, key)
        source = etree.SubElement(new_subelement, "source")
        source.text = "VALUE"
        value = etree.SubElement(new_subelement, "value")
        value.text = subelements[key]

    return xmltree

#--------------------

def add_header_subelements(xmltree, subelements):
    """
    Adds SubElements from a dictionary to xmltree under a designated parent in
    the CAOM HEADER formatting.  Parents are expected to be defined within the
    subelements dictionary [CAOM: (PARENT, HEADER_NAME, KEYWORD)]

    :param xmltree:  The xml tree object this function will add subelements
    into.
    :type xmltree:  _ElementTree from lxml

    :param subelements:  All the subelements and corresponding keywords to be
    added to the xml tree.
    :type subelements:  dictionary
    """

    #Create a SubElement for each entry in the subelements dictionary
    for key in sorted(subelements):
        for entry in subelements[key]:
            #Extract elements from tuple
            parent = entry[0]
            header_name = entry[1]
            header_keyword = entry[2]

            #Some header schemes don't use certain keywords
            if header_keyword == "null":
                continue

            #Find parent and create new subelement
            section = xmltree.find(parent)
            new_subelement = etree.SubElement(section, key)
            source = etree.SubElement(new_subelement, "source")
            source.text = "HEADER"
            name = etree.SubElement(new_subelement, "headerName")
            name.text = header_name
            keyword = etree.SubElement(new_subelement, "headerKeyword")
            keyword.text = header_keyword

            #Handle different default value cases
            if key == "targetPosition_equinox":
                default = "2000.0"
            elif key == "targetPosition_coordsys":
                default = "ICRS"
            else:
                default = "None"
            default_value = etree.SubElement(new_subelement,
                                             "headerDefaultValue")
            default_value.text = default

    return xmltree

def update_xml_entry(xmltree, parent, parameter, new_value):
    section = xmltree.find(parent)
    if section:
        entry = section.find(parameter)
        entry.text = new_value
        return xmltree
    else:
        for child in xmltree.iter():
            if child.tag == parent:
                try:
                    entry = child.find(parameter)
                    entry.text = new_value
                    return xmltree
                except AttributeError:
                    logging.warning("{0} does not have a {1} parameter!"
                                    .format(child, parameter))
                    break
    logging.warning("Could not find {0} in {1}!".format(parent,
                                                        xmltree.getroot().tag))
    return xmltree

#--------------------

def add_productlist_xml(filepath, extensions_table, static_values, tree):
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

    #All products will be subelements of the productList subelement
    parent = tree.find("productList")
    print("Generating the product list...")

    #Make sure filepaths are full and valid
    filepath = cp.check_existing_dir(filepath)
    extensions_table = cp.check_existing_file(extensions_table)

    #Read the extensions_table into a dictionary, ASSUMES extension name in
    #column 0.
    #[file extension : (n parameters...)]
    extensions = {}
    found_extensions = []
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

    #Walk filepath and check files found against the list of defined
    #extensions.  If the extension matches, create a product subelement with
    #matching parameters.
    print("...scanning files from {0}...".format(filepath))
    for path, subdirs, files in os.walk(filepath):
        #print("...adding files from {0}...".format(path))
        for name in files:
            #Build static HLSP product information.
            product_properties = static_values["product_properties"]

            #Look for a match with an entry in extensions and fill in
            #parameters.  If parameters is not filled, generate a warning in
            #the log and skip the file.
            parameters = {}
            for ext in extensions.keys():
                if name.lower().endswith(ext):
                    parameters = dict(zip(extensions['extension'],
                                          extensions[ext]))
                    found_extensions.append(ext)
                    del extensions[ext]
                    break
            if len(parameters) == 0:
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

            #Add the newly-filled parameters dictionary to the static
            #properties defined previously.
            product_properties.update(parameters)

            #Define statusAction depending on what fileStatus is assigned
            try:
                status = product_properties["fileStatus"]
            except KeyError:
                logging.error("{0} does not define 'fileStatus'!"
                              .format(extensions_table))
                print("Aborting, see log!")
                quit()
            if status == "REQUIRED":
                product_properties["statusAction"] = "ERROR"
            else:
                product_properties["statusAction"] = "WARNING"

            #Get fileType and contentType by operating on the filename.
            #Assumes that the filename ends with '_abc' to denote file type.
            #Concatenates everything after the first '.' to get content type.
            get_ext = name.split(".")
            filename = get_ext[0]
            if "_" in filename:
                filename = filename.split("_")
            elif "-" in filename:
                filename = filename.split("-")
            fileType = filename[-1]
            contentType = ".".join(get_ext[1:])
            product_properties["fileType"] = fileType.upper()
            product_properties["contentType"] = contentType.upper()

            #product_properties is now a dictionary of all necessary
            #[CAOM: XML value] entries.
            product = etree.SubElement(parent, "product")
            for prop in sorted(product_properties):
                sub = etree.SubElement(product, prop)
                sub.text = str(product_properties[prop])

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
    return tree
