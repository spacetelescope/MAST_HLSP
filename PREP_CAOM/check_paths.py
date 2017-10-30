import os

def check_existing_dir(path):
    fullpath = os.path.abspath(path)
    if not os.path.exists(fullpath):
        logging.error("{0} does not exist!".format(fullpath))
        print("Aborting, see log!")
        quit()
    else:
        return fullpath

def check_existing_file(path):
    fullpath = os.path.abspath(path)
    if not os.path.isfile(fullpath):
        logging.error("{0} does not exist!".format(fullpath))
        print("Aborting, see log!")
        quit()
    else:
        return fullpath

def check_new_file(path):
    fullpath = os.path.abspath(path)
    directory = os.path.dirname(fullpath)
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print("Creating new directories for {0}...".format(directory))
        except FileExistsError:
            pass
    return fullpath
