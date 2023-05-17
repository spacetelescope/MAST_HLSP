"""
.. module:: check_dirpath_lower
    :synopsis: Given a list of files, checks that the directory paths are all
        lowercase.
 

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
.. moduleeditor:: Jinm Yoon <jyoon@stsci.edu>

"""

import logging
import os

#--------------------

def check_dirpath_lower(file_list, root_dir, hlsp_name, lowercase_dirname = False):
    """
    Checks if directory paths are all lowercase.

    :param file_list: The list of HLSP files to check.
    :type file_list: list

    :param root_dir: Optional root directory to skip when checking compliance.
    :type root_dir: str

    :param lowercase_dirname: If True, will make directory names lowercase.
    :type lowercase_dirname: Boolean

    """

    # Get a unique list of directory paths.  Removes the root directory if
    # present.
    if root_dir:
        unique_dirs = set([os.path.dirname(x).replace(root_dir, '')
                           for x in file_list])
    else:
        unique_dirs = set([os.path.dirname(x) for x in file_list])
        #print("check_dirpath_lower:", unique_dirs)

    # Check for any subdirectories that are not lowercase.
    failed_dirs = list(filter(lambda x: not x.islower(), unique_dirs))

    # If there are any failed subdirectories, log them to the file.
    if failed_dirs:
        for failed_dir in failed_dirs:
            logging.error("The subdirectory name is not all lowercase: " + failed_dir)

        if lowercase_dirname:
            os.rename(failed_dir, failed_dir.lower())
            logging.info( "Now CHANGE to LOWERCASE DIRNAME " + failed_dir +" changed to lowercase letters: " 
                    + failed_dir.lower() )

#--------------------
