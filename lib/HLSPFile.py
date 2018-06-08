from .FileType import FileType
from .FitsKeyword import FitsKeyword
import yaml


class HLSPFile(object):

    def __init__(self):
        super().__init__()

        self._prep_level = 0

        self.file_paths = {"InputDir": "", "Output": ""}
        self.file_types = []
        self.hlsp_name = "Blank"
        self.keyword_updates = []
        self.unique_parameters = {}
        self.updated = False
        steps = ["filenames_checked", "metadata_checked", "files_selected"]
        self.ingest = {s: False for s in steps}

    def add_filetype(self, ftype):

        if isinstance(ftype, FileType):
            self.file_types.append(ftype)
        else:
            raise TypeError("Only FileType objects should be added.")

    def add_keyword_update(self, keyword):

        if isinstance(keyword, FitsKeyword):
            self.keyword_updates.append(keyword)
        else:
            raise TypeError("Only FitsKeyword objects should be added.")

    def as_dict(self):

        file_formatted_dict = {}
        for key, val in self.__dict__.items():
            if key[0] == "_":
                continue
            key = key.split("_")
            key = "".join([k.capitalize() for k in key])
            file_formatted_dict[key] = val

        return file_formatted_dict

    def save(self, filename):

        if not filename.endswith(".hlsp"):
            filename = ".".join([filename, "hlsp"])

        with open(filename, 'w') as yamlfile:
            yaml.dump(self.as_dict(), yamlfile)

    def update_filepaths(self, input=None, output=None):

        new_paths = {}

        if input:
            new_paths["InputDir"] = input
        if output:
            new_paths["Output"] = output

        self.file_paths.update(new_paths)
