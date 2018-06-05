"""
..module::  check_log
    :synopsis:  Examines the log file at the end of processing to provide some
    feedback on how many errors and warnings were logged.
"""

import os

#--------------------

def check_log(filepath):
    """ Count errors and warnings in the log file and print the results.

    :param filepath: File path for the log file.
    :type filepath: string
    """

    fullpath = os.path.abspath(filepath)
    errors = warnings = 0
    info = False

    with open(fullpath) as log:

        # Reset error & warning tallies when a new session is found via
        # additional '***INFO' lines
        for line in log:
            if line.startswith("***INFO"):
                info = not info
                if info:
                    errors = warnings = 0
            elif line.startswith("***WARNING"):
                warnings += 1
            elif line.startswith("***ERROR"):
                errors += 1

    print("Logged {0} errors and {1} warnings in the last "
          "session".format(errors, warnings))
