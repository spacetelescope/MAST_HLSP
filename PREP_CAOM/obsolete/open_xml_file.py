import logging
import os

def open_xml_file(filepath, overwrite=True):
    """
    Will either overwrite or create a new xml file.

    :param filepath:  Desired filepath for xml file creation.
    :type filepath:  string

    :param overwrite:  Flag to overwrite an existing xml file at the filepath
    location.  Defaults to True.
    :type overwrite:  boolean
    """

    #Check if this is a new file or if 'overwrite' is on before proceeding
    print("Opening {0}...".format(filepath))
    if overwrite or not os.path.isfile(filepath):
        with open(filepath, 'w') as xmlfile:
            xmlfile.close()
    else:
        logging.error("{0} already exists. Set overwrite=True to proceed."
                      .format(filepath))
        print("Aborting, see log!")
        quit()
