"""
..class:: MyError
    :synopsis: A very basic Exception subclass to pass errors with specific
    dialog between PyQt widgets.
"""

class MyError(Exception):

    def __init__(self, message):
        self.message = message
