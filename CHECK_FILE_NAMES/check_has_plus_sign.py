"""
.. module:: check_has_plus_sign
    :synopsis: Given a string, checks if it has a plus sign.

.. moduleauthor:: Jinmi Yoon <jyoon@stsci.edu>
"""
import re

#--------------------

def check_has_plus_sign(istring):
    """
    Checks if the string has a plus sign.

    :param istring: The string to check.

    :type istring: str

    :returns: bool - True if string has a plus sign, false otherwise.
    """
    return re.search('\+', istring)
