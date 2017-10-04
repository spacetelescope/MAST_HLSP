"""
.. module:: check_in_known_filters
    :synopsis: Given a string, checks if it's in a list of known filter values.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------

def check_in_known_filters(istring, known_filters):
    """
    Checks if filter string is in list of known values.

    :param istring: The string to check.

    :type istring: str

    :param known_filters: The list of known values for the "filter" part of
        file names.

    :type known_filters: set

    :returns: bool - True if in set of known values, false otherwise.
    """

    # The input string can contain one or more filter values.  If multiple,
    # they are separated by a hyphen ("-").

    # Split into pieces.
    filter_splits = istring.split('-')

    # Check if this is a subset of the known filters.
    return set(filter_splits).issubset(known_filters)

#--------------------
