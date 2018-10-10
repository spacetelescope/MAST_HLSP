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

        xml_dict = {"source": "HEADER",
                    "headerName": self.header,
                    "headerKeyword": self.fits_keyword.upper(),
                    "headerDefaultValue": self.default,
                    }

        return xml_dict

    def add_to_xml(self, xmltree):

        xml_dict = self._get_xml_dict()

        parent = xmltree.find(self.xml_parent)
        new_entry = etree.SubElement(parent, self.caom_keyword)

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

    def update(self, new_dict):
        """
        Accepts a dictionary of {attribute: vlaue} pairs and attempts to update
        existing FitsKeyword obj attributes.  If the attribute does not exist,
        a new attribute is added.  Returns a boolean flag for whether any
        changes were made to self, which allows detection of any changes a
        user enters in a keyword-updating GUI.
        """

        # print("FitsKeyword.update({0})".format(new_dict))
        if not isinstance(new_dict, dict):
            raise TypeError("FitsKeyword.update() requires a dict obj arg!")

        # Initialize the boolean flag to False
        updated = False
        for key, val in new_dict.items():

            # If 'key' is not currently an attribute, add it as a new attribute
            # and set the 'updated' flag.
            try:
                current = getattr(self, key)
            except AttributeError:
                print("Adding new attribute: {0}={1}".format(key, val))
                setattr(self, key, val)
                updated = True
                continue

            # If the new value is equal to the current value, do nothing.
            # Otherwise, update the attribute and set the 'updated' flag.
            if str(current) == str(val):
                continue
            else:
                print("Updating {0}: old={1} new={2}".format(key,
                                                             str(current),
                                                             str(val)))
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
        try:
            key = hk.fits_keyword
        except AttributeError:
            err = "FitsKeywordList only accepts FitsKeyword objects."
            raise TypeError(err)

        existing = self.find_fits(key)
        if existing:
            self.keywords.remove(existing)

        self.keywords.append(hk)

    @classmethod
    def empty_list(cls):
        pt = None
        st = None
        kd = {}
        return cls(pt, st, kd)

    def find_caom(self, target_keyword):
        for member in self.keywords:
            if member.caom_keyword == target_keyword:
                return member
        return None

    def find_differences(self, another_list):
        new_list = FitsKeywordList.empty_list()

        for kw in self.keywords:
            existing = another_list.find_fits(kw.fits_keyword)
            if existing:
                d = dict(existing.as_dict())[existing.fits_keyword]
                copy = FitsKeyword(existing.fits_keyword, parameters=d)
                updated = copy.update(kw.as_dict()[kw.fits_keyword])
                if kw.as_dict() != existing.as_dict():
                    new_list.add(kw)
                else:
                    print("{0} is the same".format(kw.fits_keyword))
            else:
                new_list.add(kw)

        return new_list

    def find_fits(self, target_keyword):
        for member in self.keywords:
            if member.fits_keyword == target_keyword:
                return member
        return None

    def is_empty(self):
        if len(self.keywords) == 0:
            return True
        else:
            return False

    def remove(self, fits_kw):

        existing = self.find_fits(fits_kw)
        if existing:
            self.keywords.remove(existing)

    def to_dataframe(self):
        row_list = []
        for member in self.keywords:
            keys = member.as_dict().keys()
            vals = member.as_dict().values()
            row = pd.DataFrame(data=[vals], columns=keys)
            row_list.append(row)

        pdframe = pd.concat(row_list)
        return pdframe

    def update_list(self, another_list):

        if another_list.is_empty():
            return

        for kw in another_list:
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
