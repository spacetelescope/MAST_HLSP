"""
.. module:: check_in_known_missions
    :synopsis: Given a string, checks if it's in a list of known mission values.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------

def check_in_known_missions(istring, known_missions, exclude_missions):
    """
    Checks if mission string is in list of known values.

    :param istring: The string to check.

    :type istring: str

    :param known_missions: The list of known values for the "mission" part of
        file names.

    :type known_missions: set

    :param exclude_missions: Optional list of values for the "mission" part of
        the file names that will be temporarily accepted (for this run only).

    :type exclude_missions: list

    :returns: bool - True if in set of known values, false otherwise.
    """

    # The input string can contain one or more mission values.  If multiple,
    # they are separated by a hyphen ("-").

    # Split into pieces.
    mission_splits = istring.split('-')

    # If provided, add the list of mission values to exclude temporarily to the
    # list to check against.
    if exclude_missions:
        all_known_missions = known_missions.union(exclude_missions)
    else:
        all_known_missions = known_missions

    # Check if this is a subset of the known missions.
    return set(mission_splits).issubset(all_known_missions)

#--------------------
