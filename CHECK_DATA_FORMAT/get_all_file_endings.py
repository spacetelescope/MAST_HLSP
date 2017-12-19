"""
.. module:: get_all_file_endings
    :synopsis: Given a directory, returns all file endings,
        within it and all sub-directories.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import os
import sys

#--------------------

def get_all_file_endings(idir):
    """
    Returns all file endings within the input directory, including
        sub-directories.

    :param idir: The directory containing HLSP files to check.

    :type idir: str
    """

    # Initialize list that will contain all file endings.
    all_file_endings = []

    # Walk through all files, making sure there aren't so many that a list can't
    # be created (based on 32- or 64-bit machine limits).
    for _, _, file_list in os.walk(idir):
        if len(all_file_endings) + len(file_list) < sys.maxsize:
            all_file_endings.extend([x.split('_')[-1] for x in file_list])
        else:
            raise IndexError("There are too many files to store in a single "
                             "array inside " + idir + ", run again on a subset "
                             "of the directories.")

    return set(all_file_endings)

#--------------------
