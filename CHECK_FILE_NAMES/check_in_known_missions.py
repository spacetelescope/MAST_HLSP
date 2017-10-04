"""
.. module:: check_in_known_missions
    :synopsis: Given a string, checks if it's in a list of known mission values.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------

def check_in_known_missions(istring, known_missions):
    """
    Checks if mission string is in list of known values.

    :param istring: The string to check.

    :type istring: str

    :param known_missions: The list of known values for the "mission" part of
        file names.

    :type known_missions: set

    :returns: bool - True if in set of known values, false otherwise.
    """

    # The input string can contain one or more mission values.  If multiple,
    # they are separated by a hyphen ("-").

    # Split into pieces.
    mission_splits = istring.split('-')

    # Check if this is a subset of the known missions.
    return set(mission_splits).issubset(known_missions)

#--------------------
