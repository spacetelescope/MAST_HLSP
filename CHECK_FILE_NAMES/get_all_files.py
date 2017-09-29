"""
.. module:: get_all_files
    :synopsis: Given a directory, returns all files, including full paths,
        within it and all sub-directories.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import os
import sys

#--------------------

def get_all_files(idir):
    """
    Returns all files within the input directory, including sub-directories.

    :param idir: The directory containing HLSP files to check.

    :type idir: str
    """

    # Initialize list that will contain all files.
    all_files = []

    # Walk through all files, making sure there aren't so many that a list can't
    # be created (based on 32- or 64-bit machine limits).
    for dirname, _, file_list in os.walk(idir):
        if len(all_files) + len(file_list) < sys.maxsize:
            all_files.extend([os.path.abspath(os.path.join(dirname, x))
                              for x in file_list])
        else:
            raise IndexError("There are too many files to store in a single "
                             "array inside " + idir + ", run again on a subset "
                             "of the directories.")

    return all_files

#--------------------
