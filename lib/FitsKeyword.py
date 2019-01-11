"""
Code here is designed to keep track of multiple .fits header keywords in
neatly-packaged objects.

..class:: FitsKeyword
    :synopsis: This class attaches a number of parameters to a single .fits
    header keyword.

..class:: FitsKeywordList
    :synopsis: This list subclass assembles a group of FitsKeyword objects,
    keeps a running list of the included keywords, and provides custom methods
    to add a new object, find an object, or sort the list.
"""

from copy import deepcopy
from lxml import etree
import pandas as pd

# --------------------


class FitsKeyword(object):
    """
    Attach a number of parameters to a given .fits header keyword.
    """

    _status_choices = ["omitted", "recommended", "required"]

    def __init__(self, kw, parameters=None):
        self.fits_keyword = kw
        self.alternates = []
        self.caom_keyword = "None"
        self.caom_status = "recommended"
        self.default = "None"
        self.header = 0
        self.hlsp_status = "required"
        self.multiple = False
        self.updated = False
        self.xml_parent = "metadataList"
        if parameters:
            [setattr(self, key, val) for key, val in parameters.items()]

    def __lt__(self, another):
        try:
            test = another.caom_keyword
            return (self.caom_keyword < another.caom_keyword)
        except AttributeError:
            raise TypeError("FitsKeyword object comparison attempted with "
                            "<{0}> ".format(type(another)))

    def __repr__(self):
        return ("<FitsKeyword ({0.fits_keyword})>: "
                "CAOM={0.caom_keyword}, "
                "HEADER={0.header}".format(self)
                )

    @property
    def alternates(self):
        return self._alternates

    @alternates.setter
    def alternates(self, alts):
        self._alternates = alts

    @property
    def caom_keyword(self):
        return self._caom_keyword

    @caom_keyword.setter
    def caom_keyword(self, c_keyword):
        self._caom_keyword = str(c_keyword).lower()

    @property
    def caom_status(self):
        return self._caom_status

    @caom_status.setter
    def caom_status(self, c_status):
        c_status = str(c_status).lower()
        if c_status in self._status_choices:
            self._caom_status = c_status
        else:
            err = "'{0}' is not an allowed value for caom_status".format(
                c_status)
            raise ValueError(err)

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = value

    @property
    def fits_keyword(self):
        return self._fits_keyword

    @fits_keyword.setter
    def fits_keyword(self, f_keyword):
        self._fits_keyword = str(f_keyword).upper()

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, head):
        if isinstance(head, int):
            self._header = head
        else:
            try:
                head = int(head)
                self._header = head
            except ValueError:
                err = "'header' must be of type <int>"
                raise TypeError(err)

    @property
    def hlsp_status(self):
        return self._hlsp_status

    @hlsp_status.setter
    def hlsp_status(self, h_status):
        h_status = str(h_status).lower()
        if h_status in self._status_choices:
            self._hlsp_status = h_status
        else:
            err = "{0} is not an allowed value for hlsp_status".format(
                h_status)
            raise ValueError(err)

    @property
    def multiple(self):
        return self._multiple

    @multiple.setter
    def multiple(self, flag):
        if isinstance(flag, bool):
            self._multiple = flag
        else:
            err = "'multiple' must be of type <bool>"
            raise TypeError(err)

    @property
    def xml_parent(self):
        return self._xml_parent

    @xml_parent.setter
    def xml_parent(self, parent):
        self._xml_parent = parent

    def _get_xml_dict(self):
        """
        Format a dictionary with information from self to be used in a CAOM XML
        template file.
        """

        xml_dict = {"source": "HEADER",
                    "headerName": self.header,
                    "headerKeyword": self.fits_keyword.upper(),
                    "headerDefaultValue": self.default,
                    }

        return xml_dict

    def add_to_xml(self, xmltree):
        """
        Add self to an lxml element tree object that defines a CAOM XML
        template file.

        :param xmltree:  The current XML structure being created for CAOM.
        :type xmltree:  lxml.etree
        """

        # Prepare the formatted dictionary containing current information from
        # self.
        xml_dict = self._get_xml_dict()

        # Find the designated XML parent and create a new subelement under it.
        parent = xmltree.find(self.xml_parent)
        new_entry = etree.SubElement(parent, self.caom_keyword)

        # Add each item in the formatted dictionary to the subelement.
        for key, val in xml_dict.items():
            parameter = etree.SubElement(new_entry, key)
            parameter.text = str(val)

        return xmltree

    def as_dict(self):
        """
        Convert the attributes of a FitsKeyword object into a dictionary for
        writing to YAML.
        """

        file_formatted_dict = {}
        for key, val in self.__dict__.items():

            # Remove any prepending underscores.  These are left over from the
            # setter functions.
            if key[0] == "_":
                key = key[1:]

            # Skip the 'fits_keyword' attribute, since that will be the
            # key for the final dict product.
            if key == "fits_keyword" or key == "updated":
                continue

            # Add the key / val pair to the dict product.
            file_formatted_dict[key] = val

        return {self.fits_keyword: file_formatted_dict}

    def compare(self, another):
        """
        Compares the attributes of two FitsKeyword objects, but the intended
        functionality is taken over by "self.update()".  Not currently used
        anywhere.
        """

        if not isinstance(another, FitsKeyword):
            raise TypeError("FitsKeyword.compare() given a non-FitsKeyword "
                            "object!")

        another_dict = another.as_dict()
        for key, val in self.as_dict().items():
            if another_dict[key] != val:
                return False
        else:
            return True

    def copy(self):
        """
        Return a separate copy of self.  Using this method can help to avoid
        problems when trying to maintain multiple FitsKeywordLists.
        """

        name = str(self.fits_keyword)
        new_dict = {}

        for key, val in self.__dict__.items():
            if key == "fits_keyword":
                continue
            else:
                new_dict[key] = deepcopy(val)

        return FitsKeyword(name, parameters=new_dict)

    @classmethod
    def from_list_item(cls, dict_from_list):
        """
        Before it is translated to a FitsKeywordList, the 'KeywordUpdates'
        section in an .hlsp file is populated by dictionaries with a single
        key and a dictionary of parameters as the corresponding value.  We want
        to natively create a FitsKeyword using this structure and take the
        burden off GUI or other supporting code.

        :param dict_from_list:  A dictionary describing a single FITS keyword.
                                {kw:{'header':0, 'default':None, ...}}
        :type dict_from_list:  dict
        """

        # Should only be a single keyword:values pair.
        kw, info = dict_from_list.popitem()

        # Expecting kw to be a string (keyword name) and info to be a
        # dictionary containing parameters.
        if (isinstance(kw, str) and isinstance(info, dict)):
            return cls(kw, parameters=info)
        else:
            return None

    def update(self, new_dict):
        """
        Accepts a dictionary of {attribute: vlaue} pairs and attempts to update
        existing FitsKeyword obj attributes.  If the attribute does not exist,
        a new attribute is added.  Returns a boolean flag for whether any
        changes were made to self, which allows detection of any changes a
        user enters in a keyword-updating GUI.

        :param new_dict:  A dictionary of new or updated attribute/value pairs.
        :type new_dict:  dict
        """

        # new_dict must be a dictionary.
        if not isinstance(new_dict, dict):
            raise TypeError("FitsKeyword.update() requires a dict obj arg!")

        # Initialize the boolean flag to False.
        updated = False

        for key, val in new_dict.items():

            # If key is not currently an attribute, add it as a new attribute
            # and set the 'updated' flag.
            try:
                current = getattr(self, key)
            except AttributeError:
                setattr(self, key, val)
                updated = True
                continue

            # If the new value is equal to the current value, do nothing.
            # Otherwise, update the attribute and set the 'updated' flag.
            if str(current) == str(val):
                continue
            else:
                setattr(self, key, val)
                updated = True

        self.updated = updated
        return updated

# --------------------


class FitsKeywordList(object):
    """
    Create a list of FitsKeyword objects and provide methods for list
    manipulation.
    """

    def __init__(self, product_type, standard_type, keywords_dict):
        self.product_type = product_type
        self.standard_type = standard_type
        self.keywords = [FitsKeyword(x, parameters=keywords_dict[x])
                         for x in keywords_dict
                         ]

    def __display__(self):
        """Only used for testing."""
        print("<FitsKeywordList>")
        print("product_type: {0}".format(self.product_type))
        print("standard_type: {0}".format(self.standard_type))
        print(".keywords: ")
        [print(member) for member in self.keywords]

    def __str__(self):
        return ("<FitsKeywordList>: product_type={0.product_type}, "
                "standard_type={0.standard_type}, "
                "num_keywords={1}".format(self, len(self.keywords))
                )

    def add(self, hk):
        """
        Add a FitsKeyword object to the self.keywords list.  If the list
        already contains an object with the same FITS keyword remove the
        existing one before adding.

        :param hk:  The FitsKeyword object to add to self.keywords.
        :type hk:  FitsKeyword
        """

        # Make sure hk is a FitsKeyword object.
        try:
            key = hk.fits_keyword
        except AttributeError:
            err = "FitsKeywordList only accepts FitsKeyword objects."
            raise TypeError(err)

        # Look for an existing FitsKeyword and remove it.
        existing = self.find_fits(key)
        if existing:
            self.keywords.remove(existing)

        self.keywords.append(hk)

    def diff(self, another_list):
        """
        Compare the contents of self to another FitsKeywordList and return
        a new FitsKeywordList of the differences.

        :param another_list:  The other list of keywords to compare to.
        :type another_list:  FitsKeywordList
        """

        # Begin a new FitsKeywordList.
        new_list = FitsKeywordList.empty_list()

        # Iterate through self.keywords and compare to another_list.  If it
        # does not match content from another_list, add it to the new_list.
        for kw in self.keywords:
            existing = another_list.find_fits(kw.fits_keyword)
            if existing:
                if kw.as_dict() != existing.as_dict():
                    new_list.add(kw)
            else:
                new_list.add(kw)

        return new_list

    @classmethod
    def empty_list(cls):
        """
        This offers an alternate constructor method for creating an empty
        FitsKeywordList.  This is mostly used for GUI operations.
        """

        pt = None
        st = None
        kd = {}
        return cls(pt, st, kd)

    def find_caom(self, target_keyword):
        """
        Search the list for a given CAOM keyword and return a matching
        FitsKeyword object.

        :param target_keyword:  The CAOM keyword to search for.
        :type target_keyword:  str
        """

        for member in self.keywords:
            if member.caom_keyword == target_keyword:
                return member
        return None

    def find_fits(self, target_keyword):
        """
        Search the list for a given FITS keyword and return the matching
        FitsKeyword object.

        :param target_keyword:  The FITS keyword to search for.
        :type target_keyword:  str
        """

        for member in self.keywords:
            if member.fits_keyword == target_keyword:
                return member
        return None

    def fill_from_list(self, list_of_kw):
        """
        Populate self with newly-made FitsKeyword objects coming from an
        unformatted list of dictionaries.  This is especially useful for
        translating the 'KeywordUpdates' section of an .hlsp file into
        a FitsKeywordList.

        :param list_of_kw:  A list of dictionaries, each describing a new or
                            updated FITS keyword.
                            [{kw1:{'header':0, ...}}, {kw2:{'header':1, ...}}]
        :type list_of_kw:  list
        """

        for kw in list_of_kw:

            # Use the from_list_item constructor and add the new object to
            # self.
            as_obj = FitsKeyword.from_list_item(kw)
            self.add(as_obj)

    def is_empty(self):
        """
        Return a boolean checking the length of the self.keywords list.
        """

        if len(self.keywords) == 0:
            return True
        else:
            return False

    def remove(self, fits_kw):
        """
        Remove a FitsKeyword object from self.keywords if a match to fits_kw
        is found.

        :param fits_kw:  The FITS keyword to search for and remove if found.
        :type fits_kw:  str
        """

        # find_fits will return the FitsKeyword object if a match is found.
        existing = self.find_fits(fits_kw)

        if existing:
            self.keywords.remove(existing)

    def to_dataframe(self):
        """
        Return a Pandas DataFrame containing the current contents of self.
        """

        # Collect individual DataFrames for each keyword.
        row_list = []
        for member in self.keywords:
            keys = member.as_dict().keys()
            vals = member.as_dict().values()
            row = pd.DataFrame(data=[vals], columns=keys)
            row_list.append(row)

        # Concat all individual DataFrames into one large frame.
        pdframe = pd.concat(row_list)

        return pdframe

    def update_list(self, another_list):
        """
        Update members of self.keywords using another FitsKeywordList.

        :param another_list:  Additions or updates to incorporate into
                              self.keywords.
        :type another_list:  FitsKeywordList
        """

        # Make sure another_list has FitsKeywordList attributes.
        try:
            x = another_list.keywords
        except AttributeError:
            err = ("FitsKeywordList.update_list() requires another "
                   "FitsKeywordList object (given {0})".format(
                       type(another_list))
                   )
            raise TypeError(err)

        # If an empty list was provided, do nothing.
        if another_list.is_empty():
            return

        # Look for each keyword in self.  If found, update the current
        # FitsKeyword with the new one.  If not found, add the new
        # FitsKeyword to self.
        for kw in another_list.keywords:
            existing = self.find_fits(kw.fits_keyword)
            if existing:
                new_params = kw.as_dict()[kw.fits_keyword]
                existing.update(new_params)
            else:
                self.add(kw)

# --------------------


def __test__():
    """
    Run some test cases for both FitsKeyword and FitsKeywordList classes.
    """

    dict1 = {"alternates": ["pink", "purple"],
             "caom_keyword": "colors",
             "default": "black",
             "header": 9}

    dict2 = {"caom_keyword": "stars",
             "default": "Sun",
             "hlsp_status": "recommended"}

    kw1 = FitsKeyword("here", parameters=dict1)
    print("--- kw1 ---")
    [print("{0}: {1}".format(key, val)) for key, val in kw1.__dict__.items()]

    kw2 = FitsKeyword("there", parameters=dict2)
    print("--- kw2 ---")
    [print("{0}: {1}".format(key, val)) for key, val in kw2.__dict__.items()]

    print(kw1.as_dict())

    kd = {"here2": dict1, "there2": dict2}
    mylist = FitsKeywordList("thing", "HST9000", kd)
    mylist.__display__()
    print(mylist.to_dataframe())

# --------------------


if __name__ == "__main__":
    __test__()
