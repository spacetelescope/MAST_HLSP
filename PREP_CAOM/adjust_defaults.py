from CAOMxml import *

def adjust_defaults(caomlist, header_type, keyword_updates):

    #Adjust these defaults for all HLSPs

    equinox = caomlist.findlabel("targetPosition_equinox")
    if isinstance(equinox, CAOMheader):
        equinox.headerDefaultValue = "2000.0"
    coordsys = caomlist.findlabel("targetPosition_coordsys")
    if isinstance(coordsys, CAOMheader):
        coordsys.headerDefaultValue = "ICRS"

    #Adjust parameters for Kepler entries

    if header_type == "kepler":
        filt = caomlist.findheader("FILTER")
        if isinstance(filt, CAOMheader):
            filt.headerDefaultValue = "Kepler"
        """
        exptime = caomlist.findheader("EXPTIME")
        if isinstance(exptime, CAOMheader):
            exptime.headerDefaultValue = "1800"
        """

    for key in sorted(keyword_updates.keys()):
        values = keyword_updates[key]
        entry = caomlist.findheader(key)
        if isinstance(entry, CAOMheader):
            entry.label = values["caom"]
            entry.headerDefaultValue = values["headerDefaultValue"]
            entry.headerName = values["headerName"]
            entry.parent = values["section"]
        else:
            print("making new entry for {0}".format(key))
            new_entry = CAOMheader(values["caom"])
            new_entry.headerKeyword = key
            new_entry.headerDefaultValue = values["headerDefaultValue"]
            new_entry.headerName = values["headerName"]
            new_entry.parent = values["section"]
            caomlist.add(new_entry)

    return caomlist
