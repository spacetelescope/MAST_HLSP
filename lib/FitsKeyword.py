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

import pandas as pd

# --------------------


class FitsKeyword(object):
    """
    Attach a number of parameters to a given .fits header keyword.
    """

    _status_choices = ["omitted", "recommended", "required"]

    def __init__(self, kw, parameters=None):
        self.fits_keyword = kw
        self.alternates = "None"
        self.caom_keyword = "None"
        self.caom_status = "required"
        self.default = "None"
        self.header = 0
        self.hlsp_status = "required"
        self.multiple = False
        self.xml_parent = "metadataList"
        if parameters:
            [setattr(self, key, val) for key, val in parameters.items()]

    def __lt__(self, another):
        if isinstance(another, FitsKeyword):
            return (self.fits_keyword < another.fits_keyword)
        else:
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

    def as_dict(self):

        file_formatted_dict = {}
        for key, val in self.__dict__.items():
            if key[0] == "_":
                key = key[1:]
            key = key.split("_")
            key = "".join([k.capitalize() for k in key])
            file_formatted_dict[key] = val

        return file_formatted_dict

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
        if isinstance(hk, FitsKeyword):
            self.keywords.append(hk)

    def find_caom(self, target_keyword):
        for member in self.keywords:
            if member.caom_keyword == target_keyword:
                return member
        return None

    def find_fits(self, target_keyword):
        for member in self.keywords:
            if member.fits_keyword == target_keyword:
                return member
        return None

    def to_dataframe(self):
        row_list = []
        for member in self.keywords:
            keys = member.as_dict().keys()
            vals = member.as_dict().values()
            row = pd.DataFrame(data=[vals], columns=keys)
            row_list.append(row)

        pdframe = pd.concat(row_list)
        return pdframe

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

    kd = {"here2": dict1, "there2": dict2}
    mylist = FitsKeywordList("thing", "HST9000", kd)
    mylist.__display__()
    print(mylist.to_dataframe())

# --------------------


if __name__ == "__main__":
    __test__()
