import bin.check_paths as cp
from bin.read_yaml import read_yaml
from FileType import FileType
from FitsKeyword import FitsKeyword, FitsKeywordList
from lxml import etree
import re
import yaml

try:
    from PyQt5.QtCore import pyqtSignal
except ImportError:
    from PyQt4.QtCore import pyqtSignal

FITS_TEMPLATES_DIR = "CHECK_METADATA_FORMAT/TEMPLATES"


class HLSPFile(object):

    def __init__(self, path=None):
        super().__init__()

        steps = ["00_filenames_checked",
                 "01_metadata_prechecked",
                 "02_metadata_checked",
                 "03_files_selected",
                 ]
        self._fits_keywords = []
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

    def _add_fits_keyword(self, keyword_obj):

        try:
            caom = keyword_obj.caom_keyword
        except AttributeError:
            err = "HLSPFile expected a <FitsKeyword> type object"
            raise TypeError(err)

        found = False
        for kw in self._fits_keywords:
            if kw.fits_keyword == keyword_obj.fits_keyword:
                found = True
                new_vals = keyword_obj.as_dict()
                kw.update(new_vals[keyword_obj.fits_keyword])

        if not found:
            self._fits_keywords.append(keyword_obj)

    @staticmethod
    def _add_xml_value_pairs(parent, parameters):

        for key, val in parameters.items():
            new_entry = etree.SubElement(parent, key)
            value_dict = {"source": "VALUE",
                          "value": val}
            for line, txt in value_dict.items():
                new_line = etree.SubElement(new_entry, line)
                new_line.text = txt

        return parent

    def _implement_keyword_updates(self):

        for kw_obj in self.keyword_updates:
            self._add_fits_keyword(kw_obj)

    def _get_standard_fits_keywords(self):

        all_standards = self.member_fits_standards()
        if all_standards:
            for std in all_standards:
                filename = ".".join([std, "yml"])
                filename = "/".join([FITS_TEMPLATES_DIR, filename])
                standard_fits = read_yaml(filename)["KEYWORDS"]
                for kw, info in standard_fits.items():
                    kw_obj = FitsKeyword(kw, parameters=info)
                    self._add_fits_keyword(kw_obj)

    @staticmethod
    def _make_value_xml_dict(val):

        value_dict = {"source": "VALUE",
                      "value": val}

        return value_dict

    def add_filetype(self, new_filetype):

        # print("<<<adding to HLSPFile obj>>>{0}".format(ftype.as_dict()))
        try:
            ft = new_filetype.ftype
        except AttributeError:
            err = ("Only FileType objects should be added to "
                   "HLSPFile.file_types!"
                   )
            raise TypeError(err)

        self.file_types.append(new_filetype)

    def add_keyword_update(self, keyword):

        try:
            k = keyword.fits_keyword
        except AttributeError:
            raise TypeError("Only FitsKeyword objects should be added.")

        if len(self.keyword_updates) == 0:
            self.keyword_updates.append(keyword)
            return

        for existing_update in self.keyword_updates:
            if existing_update.fits_keyword == k:
                updated_parameters = keyword.as_dict()[k]
                existing_update.update(updated_parameters)
                return
        else:
            self.keyword_updates.append(keyword)

    def add_unique_parameter(self, caom, parent, value):

        current_parents = self.unique_parameters.keys()
        if parent not in current_parents:
            self.unique_parameters[parent] = {}

        self.unique_parameters[parent].update({caom: value})

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

    def fits_keywords(self):

        self._get_standard_fits_keywords()
        self._implement_keyword_updates()

        return self._fits_keywords

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

    def remove_filetype(self, filetype_obj):

        type_to_remove = filetype_obj.ftype
        for ft in self.file_types:
            if ft.ftype == type_to_remove:
                self.file_types.remove(ft)
                break

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

    def write_xml_template(self, output=None):

        if not output:
            output = self.file_paths["Output"]

        output = cp.check_new_file(output)

        composite = etree.Element("CompositeObservation")
        xmltree = etree.ElementTree(composite)
        metadata = etree.SubElement(composite, "metadataList")
        provenance = etree.SubElement(composite, "provenance")
        products = etree.SubElement(composite, "productList")

        for ft in sorted(self.file_types):
            xmltree = ft.add_to_xml(xmltree)

        for kw in sorted(self.fits_keywords()):
            xmltree = kw.add_to_xml(xmltree)

        for parent, parameters in self.unique_parameters.items():
            parent = xmltree.find(parent)
            parent = self._add_xml_value_pairs(parent, parameters)

        xmltree.write(output,
                      encoding="utf-8",
                      xml_declaration=True,
                      pretty_print=True,
                      )


def __test__():
    h = HLSPFile()
    h.save("test_ouput")


if __name__ == "__main__":
    __test__()
