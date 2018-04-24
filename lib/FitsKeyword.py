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

#--------------------

class FitsKeyword():
    """
    Attach a number of parameters to a given .fits header keyword.
    """

    def __init__(self, kw, keyword):
        self.fits_keyword = kw
        self.alternates = "null"
        if "alternates" in keyword:
            self.alternates = keyword["alternates"]
        self.caom_keyword = "null"
        if "caom_keyword" in keyword:
            self.caom_keyword = keyword["caom_keyword"]
        self.caom_status = "required"
        if "caom_status" in keyword:
            self.caom_status = keyword["caom_status"]
        self.default = "None"
        if "default" in keyword:
            self.default = keyword["default"]
        self.header = 0
        if "header" in keyword:
            self.header = keyword["header"]
        self.hlsp_status = "required"
        if "hlsp_status" in keyword:
            self.hlsp_status = keyword["hlsp_status"]
        self.multiple = False
        if "multiple" in keyword:
            self.multiple = keyword["multiple"]
        self.xml_parent = "metadataList"
        if "metadataList" in keyword:
            self.xml_parent = keyword["xml_parent"]

    def __repr__(self):
        return ("<FitsKeyword({0.fits_keyword}, "
                "CAOM={0.caom_keyword}, "
                "HEADER={0.header})>".format(self))

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
        assert (c_status == "omitted"
                or c_status == "recommended"
                or c_status == "required")
        self._caom_status = c_status

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
        assert type(head) is int
        self._header = head

    @property
    def hlsp_status(self):
        return self._hlsp_status

    @hlsp_status.setter
    def hlsp_status(self, h_status):
        h_status = str(h_status).lower()
        assert (h_status == "omitted"
                or h_status == "recommended"
                or h_status == "required")
        self._hlsp_status = h_status

    @property
    def multiple(self):
        return self._multiple

    @multiple.setter
    def multiple(self, flag):
        assert type(flag) is bool
        self._multiple = flag

    @property
    def xml_parent(self):
        return self._xml_parent

    @xml_parent.setter
    def xml_parent(self, parent):
        self._xml_parent = parent

#--------------------

class FitsKeywordList(object):
    """
    Create a list of FitsKeyword objects and provide methods for list
        manipulation.
    """

    def __init__(self, product_type, standard_type, keywords_dict):
        self.product_type = product_type
        self.standard_type = standard_type
        self.keywords = [FitsKeyword(x, keywords_dict[x]) for x in
                         keywords_dict]

    def add(self, hk):
        if isinstance(hk, FitsKeyword):
            self.append(hk)
            self.keywords.append(hk.keyword)

    def find_caom(self, target_keyword):
        for member in self:
            if member.caom_keyword == target_keyword:
                return member
        return None

    def find_fits(self, target_keyword):
        for member in self:
            if member.fits_keyword == target_keyword:
                return member
        return None

    # NOTE: This will have to be re-done given new constructor.
    def sort(self):
        sorted_list = FitsKeywordList(self.header_type)
        for k in sorted(self.keywords):
            keyword_obj = self.find_fits(k)
            sorted_list.add(keyword_obj)
        return sorted_list

#--------------------

if __name__ == "__main__":
    test = FitsKeyword("this")
    print(test)
