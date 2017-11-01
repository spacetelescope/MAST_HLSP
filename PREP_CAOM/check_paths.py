import logging
import os

def check_existing_dir(path):
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

def check_existing_file(path):
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

def check_new_file(path):
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
