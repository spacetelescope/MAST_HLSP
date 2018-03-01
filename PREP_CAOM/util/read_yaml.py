"""
..module:: read_yaml
    :synopsis: Open a provided file path and load the yaml-formatted contents
    into a dictionary.
"""

import os
import yaml

#--------------------

def read_yaml(path):
    """ Open a provided file path and load the yaml-formatted contents
    into a dictionary.  Return an error string if there is a failure.

    :param path: File path of a .yaml file to pull contents from.
    :type path: string
    """

    # Try to open a yaml config file.
    try:
        stream = open(path, 'r')
        print("Opening {0}".format(path))
    except FileNotFoundError:
        err = "{0} does not exist!".format(path)
        return err

    # Use yaml.load to read the contents into a dictionary.
    try:
        contents = yaml.load(stream)
    except yaml.YAMLError:
        err = "{0} is not a YAML formatted file!".format(path)
        return err

    if isinstance(contents, dict):
        return contents
    else:
        err = "{0} did not produce a YAML dictionary!".format(path)
        return err
