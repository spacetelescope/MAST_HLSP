"""
.. module:: get_all_files
    :synopsis: Given a directory, returns all files, including full paths,
        within it and all sub-directories.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import os
import sys

#--------------------

def get_all_files(idir, skip_sym = False):
    """
    Returns all files within the input directory, including sub-directories.

    :param idir: The directory containing HLSP files to check.

    :type idir: str

    :param skip_sym: If True, will ignore symbolic links.

    :type skip_sym: Boolean
    """

    # Initialize list that will contain all files.
    all_files = []

    # Walk through all files, making sure there aren't so many that a list can't
    # be created (based on 32- or 64-bit machine limits).
    for dirname, _, file_list in os.walk(idir):
        if len(all_files) + len(file_list) < sys.maxsize:
            if not skip_sym:
                found_files = [os.path.abspath(os.path.join(dirname, x))
                               for x in file_list]
            else:
                found_files =  [os.path.abspath(os.path.join(dirname, x))
                                for x in file_list if not os.path.islink(
                        os.path.join(dirname, x))]
            all_files.extend(found_files)
        else:
            raise IndexError("There are too many files to store in a single "
                             "array inside " + idir + ", run again on a subset "
                             "of the directories.")

    return all_files

#--------------------
