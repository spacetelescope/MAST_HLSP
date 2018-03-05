import csv
import util.check_paths as cp

class HeaderKeyword():
    def __init__(self, keyword):
        self.keyword = keyword
        self.caom = None
        self.headerName = None
        self.section = "metadataList"
        self.default = "None"

class HeaderKeywordList(list):
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

def read_header_keywords_table(filepath):
    tablepath = cp.check_existing_file(filepath)
    keywords = []
    with open(tablepath) as csvfile:
        hlsp_keys = csv.reader(csvfile, delimiter=",")
        for row in hlsp_keys:
            keywords.append(row)
        csvfile.close()

    cols = keywords[0]
    full_table = {}
    for column in cols:
        n = cols.index(column)
        values = []
        for row in keywords[1:]:
            values.append(row[n])
        full_table[column] = values

    all_caom = full_table["caom"]
    all_headerName = full_table["headerName"]
    all_section = full_table["section"]

    cols.remove("caom")
    cols.remove("section")
    cols.remove("headerName")
    header_types = cols

    header_keywords = {}
    for _type in header_types:
        keywords = full_table[_type]
        keyword_objects = HeaderKeywordList(header_type=_type)
        for key in keywords:
            if key == "" or key.lower() == "null":
                continue
            n = keywords.index(key)
            hk = HeaderKeyword(key)
            hk.caom = all_caom[n]
            hk.headerName = all_headerName[n]
            hk.section = all_section[n]
            keyword_objects.add(hk)
        header_keywords[_type] = keyword_objects.sort()

    return header_keywords
