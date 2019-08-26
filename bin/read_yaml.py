"""
..module:: read_yaml
    :synopsis: Open a provided file path and load the yaml-formatted contents
    into a dictionary.
"""

import os
import yaml

# --------------------


def read_yaml(path, output=True):
    """ Open a provided file path and load the yaml-formatted contents
    into a dictionary.  Return an error string if there is a failure.

    :param path: File path of a .yaml file to pull contents from.
    :type path: string
    """

    path = os.path.abspath(path)

    # Try to open a yaml config file.
    try:
        stream = open(path, 'r')
    except FileNotFoundError:
        err = "{0} does not exist!".format(path)
        raise FileNotFoundError(err)
    else:
        if output:
            print("Opening {0}".format(path))

    # Use yaml.load to read the contents into a dictionary.
    try:
        contents = yaml.load(stream)
    except yaml.YAMLError:
        err = "{0} is not a YAML formatted file!".format(path)
        raise TypeError(err)

    stream.close()

    if isinstance(contents, dict):
        return contents
    else:
        err = "{0} did not produce a YAML dictionary!".format(path)
        raise TypeError(err)

# --------------------


if __name__ == "__main__":
    f = "../fake/k2sff_test.hlsp"
    d = read_yaml(f)
    print(d)
