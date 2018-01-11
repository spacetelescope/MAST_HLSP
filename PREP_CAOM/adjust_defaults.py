from CAOMxml import *

def adjust_defaults(caomlist, header_type):
    
    #Adjust these defaults for all HSLPs

    equinox = caomlist.findlabel("targetPosition_equinox")
    if equinox is not None:
        equinox.headerDefaultValue = "2000.0"
    coordsys = caomlist.findlabel("targetPosition_coordsys")
    if coordsys is not None:
        coordsys.headerDefaultValue = "ICRS"

    #Adjust parameters for Kepler entries
    if header_type == "kepler":
        filt = caomlist.findheader("FILTER")
        if filt is not None:
            filt.headerDefaultValue = "Kepler"
        exptime = caomlist.findheader("EXPTIME")
        if exptime is not None:
            exptime.headerDefaultValue = "1800"

    return caomlist
