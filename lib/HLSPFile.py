from FileType import FileType
from FitsKeyword import FitsKeyword


class HLSPFile(dict):

    def __init__(self):
        super().__init__()
        self["FilePaths"] = {"InputDir": "", "Output": ""}
        self["FileTypes"] = []
        self["KeywordUpdates"] = []
        self["UniqueParameters"] = {}
        self.prep_level = 0

    def update_filepaths(self, input=None, output=None):

        new_paths = {}

        if input:
            new_paths["InputDir"] = input
        if output:
            new_paths["Output"] = output

        self["FilePaths"].update(new_paths)

    def add_filetype(self, ftype):

        if isinstance(ftype, FileType):
            self["FileTypes"].append(ftype)
        else:
            raise TypeError("Only FileType objects should be added.")

    def add_keyword_update(self, keyword):

        if isinstance(keyword, FitsKeyword):
            self["KeywordUpdates"].append(keyword)
        else:
            raise TypeError("Only FitsKeyword objects should be added.")
