"""
Code here is designed to keep track of multiple .fits header keywords in
neatly-packaged objects.

..class:: HeaderKeyword
    :synopsis: This class attaches a number of parameters to a single .fits
    header keyword.

..class:: HeaderKeywordList
    :synopsis: This list subclass assembles a group of HeaderKeyword objects,
    keeps a running list of the included keywords, and provides custom methods
    to add a new object, find an object, or sort the list.

..module:: read_header_keywords_table
    :synopsis: This module opens a given table of .fits header keywords,
    creates a HeaderKeyword object for each and a single HeaderKeywordList to
    keep track of them all.  Returns the sorted HeaderKeywordList.
"""

import csv

import util.check_paths as cp

#--------------------

class HeaderKeyword():
    """ Attach a number of parameters to a given .fits header keyword.
    """

    def __init__(self, keyword):
        self.keyword = keyword
        self.caom = None
        self.headerName = None
        self.section = "metadataList"
        self.default = "None"

    @property
    def keyword(self):
        return self._keyword

    @keyword.setter
    def keyword(self, keyword):
        self._keyword = keyword.upper()

    @property
    def caom(self):
        return self._caom

    @caom.setter
    def caom(self, caom):
        self._caom = caom

    @property
    def headerName(self):
        return self._headerName

    @headerName.setter
    def headerName(self, headerName):
        self._headerName = headerName

    @property
    def section(self):
        return self._section

    @section.setter
    def section(self, section):
        self._section = section

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, default):
        self._default = default
#--------------------

class HeaderKeywordList(list):
    """ Create a list of HeaderKeyword objects and provide methods for list
    manipulation.
    """

    def __init__(self, header_type):
        super().__init__()
        self.header_type = header_type
        self.keywords = []

    def add(self, hk):
        if isinstance(hk, HeaderKeyword):
            self.append(hk)
            self.keywords.append(hk.keyword)

    def find(self, target_keyword):
        for member in self:
            if member.keyword == target_keyword:
                return member
        return None

    def sort(self):
        sorted_list = HeaderKeywordList(self.header_type)
        for k in sorted(self.keywords):
            keyword_obj = self.find(k)
            sorted_list.add(keyword_obj)
        return sorted_list

#--------------------

def read_header_keywords_table(filepath):
    """ Read a table of .fits keywords from a .csv file into a
    HeaderKeywordList of HeaderKeyword objects.

    :param filepath:  The location of the .csv file containing the header
                      keyword table.
    :type filepath:  str
    """

    # Open the file at filepath and read it into a list.
    tablepath = cp.check_existing_file(filepath)
    if tablepath is None:
        return None
    keywords = []
    with open(tablepath) as csvfile:
        hlsp_keys = csv.reader(csvfile, delimiter=",")
        for row in hlsp_keys:
            keywords.append(row)
        csvfile.close()

    # Pull out the column names
    cols = keywords[0]

    # Turn the list of rows into a dictionary of columns
    full_table = {}
    for column in cols:
        n = cols.index(column)
        values = []
        for row in keywords[1:]:
            values.append(row[n])
        full_table[column] = values

    # Pull out some lists from the dictionary
    all_caom = full_table["caom"]
    all_headerName = full_table["headerName"]
    all_section = full_table["section"]

    # Get a list of just the different types of header keywords
    cols.remove("caom")
    cols.remove("section")
    cols.remove("headerName")
    header_types = cols

    # For each different type of header keywords, create a HeaderKeywordList
    # and add a HeaderKeyword object to that list for each listed keyword.
    # Store all HeaderKeywordList objects in a dictionary.
    header_keywords = {}
    for _type in header_types:

        # Create a new HeaderKeywordList for the current type of .fits headers
        keywords = full_table[_type]
        keyword_objects = HeaderKeywordList(header_type=_type)

        for key in keywords:

            # Skip empty or null keyword definition rows
            if key == "" or key.lower() == "null":
                continue

            # Create a new HeaderKeyword object for the current keyword and
            # assign the parameters
            n = keywords.index(key)
            hk = HeaderKeyword(key)
            hk.caom = all_caom[n]
            hk.headerName = all_headerName[n]
            hk.section = all_section[n]

            # Add the new HeaderKeyword object to the HeaderKeywordList
            keyword_objects.add(hk)

        # Add the sorted HeaderKeywordList to the dictionary
        header_keywords[_type] = keyword_objects.sort()

    return header_keywords
