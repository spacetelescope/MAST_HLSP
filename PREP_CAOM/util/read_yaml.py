"""
..module:: read_yaml
    :synopsis: Open a provided file path and load the yaml-formatted contents
    into a dictionary.
"""

import os
import yaml

#--------------------

def read_yaml(path):
    """
    Open a provided file path and load the yaml-formatted contents
    into a dictionary.

    :param path: File path of a .yaml file to pull contents from.
    :type path: string
    """
    #Try to open a yaml config file.
    try:
        stream = open(path, 'r')
        print("Opening {0}...".format(path))
    except FileNotFoundError:
        print("{0} does not exist!".format(path))
        quit()

    #Use yaml.load to read the contents into a dictionary.
    try:
        contents = yaml.load(stream)
    except yaml.YAMLError:
        print("{0} is not a yaml formatted file!".format(path))
        quit()

    return contents
