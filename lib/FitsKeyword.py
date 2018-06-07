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

# --------------------

class FitsKeyword(object):
    """
    Attach a number of parameters to a given .fits header keyword.
    """

    _status_choices = ["omitted", "recommended", "required"]

    def __init__(self, kw, parameters=None):
        self.fits_keyword = kw
        self.alternates = "null"
        self.caom_keyword = "null"
        self.caom_status = "required"
        self.default = "None"
        self.header = 0
        self.hlsp_status = "required"
        self.multiple = False
        self.xml_parent = "metadataList"

        if parameters:
            [setattr(self, key, val) for key, val in parameters.items()]

    def __lt__(self, another):
        return self.fits_keyword < another.fits_keyword

    def __repr__(self):
        return ("<FitsKeyword({0.fits_keyword}, "
                "CAOM={0.caom_keyword}, "
                "HEADER={0.header})>".format(self)
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

    def add(self, hk):
        # NOTE: self.append() may not work without defining that method...
        if isinstance(hk, FitsKeyword):
            self.append(hk)
            self.keywords.append(hk.keyword)

    def find_caom(self, target_keyword):
        # NOTE: may not be able to iterater directly over this...
        for member in self:
            if member.caom_keyword == target_keyword:
                return member
        return None

    def find_fits(self, target_keyword):
        # NOTE: may not be able to iterater directly over this...
        for member in self:
            if member.fits_keyword == target_keyword:
                return member
        return None

# --------------------


if __name__ == "__main__":
    p = {"default": "what?", "header": 1, "caom_keyword": "no"}
    test = FitsKeyword("this", parameters=p)
    print(test.__dict__)
