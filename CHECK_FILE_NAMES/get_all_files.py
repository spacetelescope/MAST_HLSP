"""
.. module:: get_all_files
    :synopsis: Given a directory, returns all files, including full paths,
        within it and all sub-directories.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import os

#--------------------

def get_all_files(idir):
    """
    Returns all files within the input directory, including sub-directories.

    :param idir: The directory containing HLSP files to check.

    :type idir: str
    """

    # Initialize list that will contain all files.
    all_files = []

    for dirname, _, file_list in os.walk(idir):
        all_files.extend([os.path.abspath(os.path.join(dirname, x))
                          for x in file_list])

    return all_files

#--------------------
