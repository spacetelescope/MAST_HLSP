"""
..module:: check_existing_dir
    :synopsis: Check a user-provided directory that should already exist (such
    as an HLSP directory).  Quit if the directory is not found.

..module:: check_existing_file
    :synopsis: Check a file that should already exist (such as the header
    keyword translation table) and quit if it is not found.

..module:: check_new_file
    :synopsis: Check a new file path that is being created.  Get the full path
    and create any directories along the way that don't already exist.
"""

import logging
import os

#--------------------

def check_existing_dir(path):
    """
    Check a user-provided directory that should already exist (such
    as an HLSP directory).  Quit if the directory is not found.

    :param path: File path to be checked.
    :type path: string
    """
    try:
        fullpath = os.path.abspath(path)
    except TypeError:
        logging.error("check_existing_dir was passed an empty path!")
        print("Aborting, see log!")
        quit()
    if not os.path.exists(fullpath):
        logging.error("{0} does not exist!".format(fullpath))
        print("Aborting, see log!")
        quit()
    else:
        return fullpath

#--------------------

def check_existing_file(path):
    """
    Check a file that should already exist (such as the header keyword
    translation table) and quit if it is not found.

    :param path: File path to be checked.
    :type path: string
    """
    try:
        fullpath = os.path.abspath(path)
    except TypeError:
        logging.error("check_existing_file was passed an empty path!")
        print("Aborting, see log!")
        quit()
    if not os.path.isfile(fullpath):
        logging.error("{0} does not exist!".format(fullpath))
        print("Aborting, see log!")
        quit()
    else:
        return fullpath

#--------------------

def check_new_file(path):
    """
    Check a new file path that is being created.  Get the full path and create
    any directories along the way that don't already exist.

    :param path: File path to be checked.
    :type path: string
    """
    try:
        fullpath = os.path.abspath(path)
    except TypeError:
        logging.error("check_new_file was passed an empty path!")
        print("Aborting, see log!")
        quit()
    directory = os.path.dirname(fullpath)
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print("Creating new directories for {0}...".format(directory))
        except FileExistsError:
            pass
    return fullpath
