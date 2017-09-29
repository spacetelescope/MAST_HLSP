"""
.. module:: check_is_version_string
    :synopsis: Given a string, checks if it looks like a version string.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------

def check_is_version_string(istring):
    """
    Checks if the string looks like a version.

    :param istring: The string to check.

    :type istring: str

    :returns: bool - True if string looks like a version, false otherwise.
    """
    return istring[0] == 'v'

#--------------------
