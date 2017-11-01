"""
..module::  check_log
    :synopsis:  Examines the log file at the end of processing to provide some
    feedback on how many errors and warnings were logged.
"""

import os

#--------------------

def check_log(filepath):
    fullpath = os.path.abspath(filepath)
    errors = 0
    warnings = 0
    with open(fullpath) as log:
        as_lines = log.readlines()
        for n in as_lines:
            if n.startswith("***WARNING"):
                warnings += 1
            elif n.startswith("***ERROR"):
                errors += 1
        log.close()
    print("Logged {0} errors and {1} warnings".format(errors, warnings))
