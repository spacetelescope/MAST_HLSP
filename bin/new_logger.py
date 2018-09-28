import logging


def new_logger(filename, lvl=logging.DEBUG):
    """
    This module establishes Python logging to a new user-provided log file at
    a specified message level.  By operating on the root logger, parent modules
    can set up a new log file and allow child modules to simply use 'logging'
    commands.  This enables multiple log file creation while running through a
    GUI.

    :param filename:  The desired file to write logging messages to.
    :type filename:  str

    :param lvl:  The lowest level of messages to capture in the log.  (Defaults
                 to logging.DEBUG)
    :type lvl:  int
    """

    # An empty getLogger call returns the root log.
    logger = logging.getLogger()

    # Setting the handlers attribute to an empty list removes any existing
    # file handlers.
    logger.handlers = []

    # Format the message strings to log.
    format = logging.Formatter('%(levelname)s from %(module)s: %(message)s')

    # Create a new file handler with the requested file name.
    handler = logging.FileHandler(filename, mode='w')
    handler.setFormatter(format)

    # Update the new properties of the root logger.
    logger.setLevel(lvl)
    logger.addHandler(handler)

    return logger
