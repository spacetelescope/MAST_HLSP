"""
..module:: adjust_defaults
    :synopsis: Make some final headerDefaultValue adjustments to some header
    keyword entries.  Includes some standard adjustments and ability to
    incorporate new updates from the config file.
"""

from lib.CAOMxml import *

#--------------------

def adjust_defaults(caomlist, header_type, keyword_updates):
    """ Make final headerDefaultValue adjustments based on header_type and
    any provided in the config file.

    :param caomlist:  The list of CAOMxml objects being aggregated to write
                      into XML.
    :type caomlist:  CAOMxmlList

    :param header_type:  The type of header keywords specified in the config
                         file.
    :type header_type:  str

    :param keyword_updates:  Any additional changes to be made defined in the
                             config file.
    :type keyword_updates:  dict
    """

    # Adjust these defaults for all HLSPs
    equinox = caomlist.findlabel("targetPosition_equinox")
    if isinstance(equinox, CAOMheader):
        equinox.headerDefaultValue = "2000.0"
    coordsys = caomlist.findlabel("targetPosition_coordsys")
    if isinstance(coordsys, CAOMheader):
        coordsys.headerDefaultValue = "ICRS"

    # Adjust parameters for Kepler entries
    if header_type == "kepler":
        filt = caomlist.findheader("FILTER")
        if isinstance(filt, CAOMheader):
            filt.headerDefaultValue = "Kepler"

    # Read the dictionary defined in the config file and make any changes
    for key in sorted(keyword_updates.keys()):
        values = keyword_updates[key]
        entry = caomlist.findheader(key)

        # If the listed keyword already exists, update the parameters
        if isinstance(entry, CAOMheader):
            entry.label = values["caom"]
            entry.headerDefaultValue = values["headerDefaultValue"]
            entry.headerName = values["headerName"]
            entry.parent = values["section"]

        # If the listed keyword does not already exist, make a new CAOMheader
        # object, set parameters, and add it to caomlist
        else:
            print("...making new entry for {0}...".format(key))
            new_entry = CAOMheader(values["caom"])
            new_entry.headerKeyword = key
            new_entry.headerDefaultValue = values["headerDefaultValue"]
            new_entry.headerName = values["headerName"]
            new_entry.parent = values["section"]
            caomlist.add(new_entry)

    return caomlist
