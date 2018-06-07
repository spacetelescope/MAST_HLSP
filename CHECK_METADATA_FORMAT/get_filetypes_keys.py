"""
.. module:: get_filetypes_keys
    :synopsis: Extracts keys as a list of strings from an input list of dicts.
        This is used when a list of dicts is passed from parsing a .hlsp file.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------

import numpy

#--------------------

def get_filetypes_keys(ilist):
    """
    Extracts keys as a list of strings given a list of dicts from parsing a
        .hlsp file.

    :param ilist: The input list of dicts.

    :type ilist: list

    :returns: list - a list of keys as strings.
    """

    return [[*x][0] for x in ilist]

#--------------------
