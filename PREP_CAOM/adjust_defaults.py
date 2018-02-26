from CAOMxml import *

def adjust_defaults(caomlist, header_type):

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
        exptime = caomlist.findheader("EXPTIME")
        if isinstance(exptime, CAOMheader):
            exptime.headerDefaultValue = "1800"

    return caomlist
