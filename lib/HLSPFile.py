from bin.read_yaml import read_yaml
from FileType import FileType
from FitsKeyword import FitsKeyword, FitsKeywordList
import re
import yaml

try:
    from PyQt5.QtCore import pyqtSignal
except ImportError:
    from PyQt4.QtCore import pyqtSignal


class HLSPFile(object):

    def __init__(self, path=None):
        super().__init__()

        steps = ["00_filenames_checked",
                 "01_metadata_prechecked",
                 "02_metadata_checked",
                 "03_files_selected",
                 ]
        self._prep_level = 0
        self._updated = False

        self.file_paths = {"InputDir": "", "Output": ""}
        self.file_types = []
        self.hlsp_name = "Blank"
        self.ingest = {s: False for s in steps}
        self.keyword_updates = []
        self.unique_parameters = {}

        if path:
            self.load_hlsp(path)

    def add_filetype(self, ftype):

        # print("<<<adding to HLSPFile obj>>>{0}".format(ftype.as_dict()))
        self.file_types.append(ftype)

    def add_keyword_update(self, keyword):

        try:
            k = keyword.fits_keyword
        except AttributeError:
            raise TypeError("Only FitsKeyword objects should be added.")

        if len(self.keyword_updates) == 0:
            print(
                "Adding {0} with len(self.keyword_updates)==0".format(keyword))
            self.keyword_updates.append(keyword)
            return

        for existing_update in self.keyword_updates:
            if existing_update.fits_keyword == k:
                updated_parameters = keyword.as_dict()[k]
                existing_update.update(updated_parameters)
                return
        else:
            print("Adding {0} after not finding a match".format(keyword))
            self.keyword_updates.append(keyword)

    def as_dict(self):

        file_formatted_dict = {}
        for key, val in self.__dict__.items():
            if key[0] == "_":
                continue
            key = key.split("_")
            key = "".join([k.capitalize() for k in key])
            if key == "FileTypes":
                val = list()
                for ft in self.file_types:
                    # print("<<<HLSPFile contains>>>{0}".format(ft.as_dict()))
                    val.append(ft.as_dict())
            elif key == "KeywordUpdates":
                val = list()
                for kw in self.keyword_updates:
                    val.append(kw.as_dict())
            file_formatted_dict[key] = val

        return file_formatted_dict

    def load_hlsp(self, filename):

        load_dict = read_yaml(filename)
        for key, val in load_dict.items():
            key = re.findall('[A-Z][^A-Z]*', key)
            attr = "_".join([k.lower() for k in key])
            setattr(self, attr, val)

    def member_fits_standards(self):

        if len(self.file_types) == 0:
            return None

        standards = []
        for ft in self.file_types:
            if not (ft.standard and ft.product_type and ft.run_check):
                continue
            std = "_".join([ft.product_type, ft.standard])
            if std not in standards:
                standards.append(std)

        if len(standards) > 0:
            return standards
        else:
            return None

    def save(self, filename=None):

        print("HLSPFile.keyword_updates={0}".format(self.keyword_updates))
        if filename:
            if not filename.endswith(".hlsp"):
                filename = ".".join([filename, "hlsp"])
        else:
            filename = ".".join([self.hlsp_name, "hlsp"])

        with open(filename, 'w') as yamlfile:
            yaml.dump(self.as_dict(), yamlfile, default_flow_style=False)
            print("...saving {0}...".format(filename))

    def toggle_updated(self, flag):
        self.updated = flag

    def update_filepaths(self, input=None, output=None):

        new_paths = {}

        if input:
            new_paths["InputDir"] = input
        if output:
            new_paths["Output"] = output

        self.file_paths.update(new_paths)


def __test__():
    h = HLSPFile()
    h.save("test_ouput")


if __name__ == "__main__":
    __test__()
