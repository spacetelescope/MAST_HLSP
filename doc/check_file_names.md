Checking File Names
===================

Software for checking file name and subdirectory compliance is located within the "CHECK_FILE_NAMES/" folder within the repository.

## How To Run ##
### From The Command Line ###
    python check_file_names.py <folder> <hlsp_name> [--root_dir, --exclude_missions, --exclude_filters]

where
* <folder> = Required string containing the full path to the directory containing all the HLSP files you want to check.
* <hlsp_name> = Required string containing the name of the HLSP project, e.g., "relics", "everest", etc.
* --root_dir = Optional string containing the root path to the directory.  If provided, this part of the directory path will not be subject to HLSP requirement testing.
* --exclude_missions = Optional sequence of one or more strings to accept **for this run only** as the mission part of HLSP file names.
* --exclude_filters = Optional sequence of one or more strings to accept **for this run only** as the filter part of HLSP file names.

## Examples ##
    python check_file_names.py /Work/HLSP/k2gap k2gap --root_dir="/Work/HLSP/" --exclude_missions none any all multi --exclude_filters none multi

In the above example, the direcotry "/Work/HLSP/k2gap/" will be checked for HLSP requirement compliance.  Because the --root_dir option is provided, the "/Work/HLSP/" part of directory paths will not be subject to these requirements (e.g., this part of the full path does not need to be all lowercase).  Everything below the --root_dir **is** subject to HLSP requirements, however.  Because the --exclude_missions option is provided, the strings "none", "any", "all", and "multi" will be allowed to be part of the "mission" component of the HLSP file name for this run only.  Because the --exclude_filters option is provided, the strings "none" and "multi" will be allowed to be part of the "filter" component of the HLSP file name for this run only.

## What Requirements Are Tested By check_file_names.py? ##

* All sub-directories must be completely lower-case.  The only exception is the beginning path to the HLSP directory, which can be ignored by specifying it in the --root_dir option.
* All files must be completely lower-case.
* All files within the HLSP directory must contain exactly eight components, separated by a single underscore character.  These fields are:
    1. The string "hlsp"
    1. The HLSP name, which must match the HLSP name provided as an input variable to check_file_names.py
    1. The mission component, which must consist of one or more known mission strings or temporarily allowed mission strings if provided via the "--exclude_missions" option.  If this component has more than one value, they must be separated by a hyphen.
    1. The instrument component, for which there is no specific check done at this time.
    1. The target component, for which there is no specific check done at this time.
    1. The filter component, which must consist of one ore more known filter strings or temporarily allowed filter strings if provided via the "--exclude_filters" option.  If this component has more than one value, they must be separated by a hyphen.
    1. The version component, which must begin with the letter "v", e.g., "v1" or "v1.0".
    1. The product and extension component, which must be in the format <x>.<y>.  In this case, <x> is a string or composite string describing the product, e.g., "img" or "spec-list".  It can use hyphens to separate multiple strings.  The extension part <y> is the extension of the file type, e.g., "fits" or "txt" or "csv".

### Known Mission and Filter Values ###
A table of known, acceptable string values for the mission and filter components are stored in the repository in the "known_missions.dat" and "known_filters.dat" files, respectively.  If a string needs to be added to these known values, please create an Issue on the GitHub repository with your request.
