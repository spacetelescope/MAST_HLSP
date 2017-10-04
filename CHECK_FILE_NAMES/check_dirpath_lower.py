"""
.. module:: check_dirpath_lower
    :synopsis: Given a list of files, checks that the directory paths are all
        lowercase.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import logging
import os

#--------------------

def check_dirpath_lower(file_list, root_dir):
    """
    Checks if directory paths are all lowercase.

    :param file_list: The list of HLSP files to check.

    :type file_list: list

    :param root_dir: Optional root directory to skip when checking compliance.

    :type root_dir: str
    """

    # Get a unique list of directory paths.  Removes the root directory if
    # present.
    if root_dir:
        unique_dirs = set([os.path.dirname(x).replace(root_dir, '')
                           for x in file_list])
    else:
        unique_dirs = set([os.path.dirname(x) for x in file_list])

    # Check for any subdirectories that are not lowercase.
    failed_dirs = list(filter(lambda x: not x.islower(), unique_dirs))

    # If there are any failed subdirectories, log them to the file.
    if failed_dirs:
        for failed_dir in failed_dirs:
            logging.warning("Subdirectory is not all lowercase: " + failed_dir)

#--------------------
