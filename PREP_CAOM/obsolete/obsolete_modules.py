
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
