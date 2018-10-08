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

# --------------------


class HLSPFile(object):
    """
    This file constructs an object to organize information needed for HLSP data
    file ingestion to MAST and CAOM.  The class provides methods to access and
    modify that information, as well as read or write that information from/to
    YAML-formatted files.

    ..module::  _add_fits_keyword
    ..synopsis::  Add a new FitsKeyword object to the private _fits_keywords
                  list.  Skip if the keyword is already present.

    ..module::  _add_xml_value_pairs
    ..synopsis::  Add a dictionary of keyword / value pairs to an lxml etree.

    ..module::  _get_standard_fits_keywords
    ..synopsis::  Read a FITS template file based on the file types present,
                  create FitsKeyword objects based on the template and try to
                  add them to _fits_keywords.

    ..module::  _implement_keyword_updates
    ..synopsis::  Add FITS keyword updates defined in the keyword_updates list
                  to _fits_keywords.

    ..module::  _make_value_xml_dict
    ..synopsis::  Format a provided value into a dictionary for lxml ingest.

    ..module::  _split_name_from_params
    ..synopsis::  Given a single key dictionary, return the lone key and
                  corresponding dictionary.

    ..module::  add_filetype
    ..synopsis::  Add a FileType object to the file_types list.

    ..module::  add_keyword_update
    ..synopsis::  Add an updated FitsKeyword object to the keyword_updates
                  list.

    ..module::  add_unique_parameter
    ..synopsis::  Add a new entry in the unique_parameters list.

    ..module::  as_dict
    ..synopsis::  Return the current contents of self as a formatted
                  dictionary.  This is useful for entering the contents into
                  an XML tree or writing to YAML.

    ..module::  find_file_type
    ..synopsis::  Find a given file ending in the file_types list.

    ..module::  fits_keywords
    ..synopsis::  Combine the contents of the designated FITS template and
                  any keyword updates and return a list of all FitsKeyword
                  objects used by this HLSPFile.

    ..module::  in_hlsp_format
    ..synopsis::  Checks for a number of HLSPFile attributes, returns False if
                  not found.  Have not put this to any use yet.

    ..module::  load_hlsp
    ..synopsis::  Read information from a YAML-formatted .hlsp file and load
                  those contents into self.

    ..module::  member_fits_standards
    ..synopsis::  Get a list of all FITS standards being used by file types
                  present in the file_types list.

    ..module::  remove_filetype
    ..synopsis::  Remove a FileType object from the file_types list.

    ..module::  save
    ..synopsis::  Write the current contents of self to a YAML-formatted .hlsp
                  file.

    ..module::  update_filepaths
    ..synopsis::  Update the file_paths dictionary with provided input / output
                  settings.

    ..module::  write_xml_template
    ..synopsis::  Write the current contents of self into an XML-formatted
                  template file for ingestion into CAOM.
    """

    def __init__(self, path=None):
        """
        Initialize a new HLSPFile object.

        :param path:  Provided a path to a valid .hlsp-formatted file,
                      initialization will immediately load the contents into
                      the new object.
        :type path:  str
        """

        super().__init__()

        # Set the list of ingestion steps.
        steps = ["00_filenames_checked",
                 "01_metadata_prechecked",
                 "02_metadata_checked",
                 "03_fits_keywords_set",
                 "04_value_parameters_added"
                 ]

        # Set private internal-use attributes.
        self._fits_keywords = []
        self._updated = False

        # Initialize primary attributes.
        self.file_paths = {"InputDir": "", "Output": ""}
        self.file_types = []
        self.hlsp_name = "Blank"
        self.ingest = {s: False for s in steps}
        self.keyword_updates = []
        self.unique_parameters = {}

        # If path is provided, try to load the file contents into self.
        if path:
            self.load_hlsp(path)

    def _add_fits_keyword(self, keyword_obj):
        """
        Add a new FitsKeyword object to the private _fits_keywords list.  Skip
        if the keyword is already present.

        :param keyword_obj:  The potentially new fits keyword to add.
        :type keyword_obj:  FitsKeyword
        """

        # Check keyword_obj for a FitsKeyword attribute.
        try:
            caom = keyword_obj.caom_keyword
        except AttributeError:
            err = "HLSPFile expected a <FitsKeyword> type object"
            raise TypeError(err)

        # Assume the given FitsKeyword is already in self._fits_keywords.
        found = False
        updated = False

        # Search for the given FitsKeyword in self._fits_keywords.
        for kw in self._fits_keywords:

            # If found, try updating the existing FitsKeyword object with
            # values from the target object.
            if kw.fits_keyword == keyword_obj.fits_keyword:
                found = True
                new_vals = keyword_obj.as_dict()
                updated = kw.update(new_vals[keyword_obj.fits_keyword])

        # If keyword_obj updates an existing FitsKeyword or is a new
        # FitsKeyword, add it to self._fits_keywords.
        if updated or not found:
            self._fits_keywords.append(keyword_obj)

    @staticmethod
    def _add_xml_value_pairs(parent, parameters):
        """
        Add a dictionary of keyword / value pairs to an lxml etree.

        :param parameters:  A dictionary of keyword / value pairs to be added.
        :type parameters:  dict
        """

        # Iterate through all key / val pairs in parameters.
        for key, val in parameters.items():
            new_entry = etree.SubElement(parent, key)

            # Format the dictionary to go in a CAOM template XML file.
            value_dict = self._make_value_xml_dict(val)

            # Add the formatted dictionary to the lxml etree.
            for line, txt in value_dict.items():
                new_line = etree.SubElement(new_entry, line)
                new_line.text = txt

        return parent

    def _get_standard_fits_keywords(self):
        """
        Read a FITS template file based on the file types present, create
        FitsKeyword objects based on the template and try to add them to
        _fits_keywords.
        """

        # Get all the FITS standards currently used by file types in self.
        all_standards = self.member_fits_standards()

        # Iterate through all the standards if any are found.
        if all_standards:
            for std in all_standards:

                # Look up the FITS template file for the current standard.
                filename = ".".join([std, "yml"])
                filename = "/".join([FITS_TEMPLATES_DIR, filename])
                standard_fits = read_yaml(filename)["KEYWORDS"]

                # Create a FitsKeyword for each entry in the template and try
                # to add it to self._fits_keywords.
                for kw, info in standard_fits.items():
                    kw_obj = FitsKeyword(kw, parameters=info)
                    self._add_fits_keyword(kw_obj)

    def _implement_keyword_updates(self):
        """
        Add FITS keyword updates defined in the keyword_updates list to
        _fits_keywords.
        """

        # Iterate through each entry in self.keyword_updates and try to add it
        # to self._fits_keywords.
        for kw_obj in self.keyword_updates:
            self._add_fits_keyword(kw_obj)

    @staticmethod
    def _make_value_xml_dict(val):
        """
        Format a provided value into a dictionary for lxml ingest.

        :param val:  A value to add to a formatted dictionary.
        :type val:  obj
        """

        # This is the format expected in a CAOM template XML file.
        value_dict = {"source": "VALUE",
                      "value": val}

        return value_dict

    @staticmethod
    def _split_name_from_params(entry):
        """
        Given a single key dictionary, return the lone key and corresponding
        dictionary.

        :param entry:  Expecting a single-key dictionary such as {key:
                       {param1: val1, param2: val2, ...}}.
        :type entry:  dict
        """

        # Verify entry only has one top-level key before returning the split
        # data.
        name = list(entry.keys())
        if len(name) > 1:
            return None
        else:
            return name[0], entry[name[0]]

    def add_filetype(self, new_filetype):
        """
        Add a FileType object to the file_types list.

        :param new_filetype:  A new file type to be added to self.file_types.
        :type new_filetype:  FileType
        """

        # Check new_filetype for a FileType attribute.
        try:
            ft = new_filetype.ftype
        except AttributeError:
            err = ("Only FileType objects should be added to "
                   "HLSPFile.file_types!"
                   )
            raise TypeError(err)

        self.file_types.append(new_filetype)

    def add_keyword_update(self, keyword):
        """
        Add an updated FitsKeyword object to the keyword_updates list.

        :param keyword:  A potentially new FitsKeyword object to be added to
                         self.keyword_updates.
        :type keyword:  FitsKeyword
        """

        # Check keyword for a FitsKeyword attribute.
        try:
            k = keyword.fits_keyword
        except AttributeError:
            raise TypeError("Only FitsKeyword objects should be added.")

        # If self.keyword_updates is empty, just add the new entry.
        if len(self.keyword_updates) == 0:
            self.keyword_updates.append(keyword)
            return

        # Check if keyword is already in self.keyword_updates.
        for existing_update in self.keyword_updates:

            # If found, try to update the existing FitsKeyword with values
            # from the new one.
            if existing_update.fits_keyword == k:
                updated_parameters = keyword.as_dict()[k]
                existing_update.update(updated_parameters)
                return

        # If not found, add the new FitsKeyword.
        else:
            self.keyword_updates.append(keyword)

    def add_unique_parameter(self, caom, parent, value):
        """
        Add a new entry in the unique_parameters list.

        :param caom:  The CAOM keyword we want to add to the XML template file.
        :type caom:  str

        :param parent:  The XML parent section to add the new keyword / value.
        :type parent:  str

        :param value:  The value to associate with the new CAOM keyword.
        :type value:  obj
        """

        # Get the current XML parents from the self.unique_parameters
        # dictionary.
        current_parents = self.unique_parameters.keys()

        # If parent is not an existing XML parent, make a new entry in the
        # self.unique_parameters dictionary.
        if parent not in current_parents:
            self.unique_parameters[parent] = {}

        # Add the keyword / value pair to the parent section.
        self.unique_parameters[parent].update({caom: value})

    def as_dict(self):
        """
        Return the current contents of self as a formatted dictionary.  This
        is useful for entering the contents into an XML tree or writing to
        YAML.
        """

        file_formatted_dict = {}

        # Iterate through all current attributes.
        for key, val in self.__dict__.items():

            # Skip any private attributes.
            if key[0] == "_":
                continue

            # Format the keys for writing to YAML.
            key = key.split("_")
            key = "".join([k.capitalize() for k in key])

            # If operating with self.file_types or self.keyword_updates, use
            # the class methods to return the object information in dicts.
            if key == "FileTypes":
                val = list()
                for ft in self.file_types:
                    val.append(ft.as_dict())
            elif key == "KeywordUpdates":
                val = list()
                for kw in self.keyword_updates:
                    val.append(kw.as_dict())

            file_formatted_dict[key] = val

        return file_formatted_dict

    def find_file_type(self, target_ending):
        """
        Find a given file ending in the file_types list.

        :param target_ending:  A file ending such as "type.extension" to look
                               for in self.file_types.
        :type target_ending:  str
        """

        # Search self._file_types and return any matching FileType object.
        for ft in self.file_types:
            if ft.ftype.lower() == target_ending.lower():
                return ft

        return None

    def fits_keywords(self):
        """
        Combine the contents of the designated FITS template and any keyword
        updates and return a list of all FitsKeyword objects used by this
        HLSPFile.
        """

        self._get_standard_fits_keywords()
        self._implement_keyword_updates()

        return self._fits_keywords

    def in_hlsp_format(self):
        """
        Checks for a number of HLSPFile attributes, returns False if not
        found.  Have not put this to any use yet.
        """

        # Access HLSPFile attributes.
        try:
            test_fp = self.file_paths
            test_ft = self.file_types
            test_hn = self.hlsp_name
            test_in = self.ingest
            test_ku = self.keyword_updates
            test_up = self.unique_parameters
        except AttributeError:
            return False

    def load_hlsp(self, filename):
        """
        Read information from a YAML-formatted .hlsp file and load those
        contents into self.

        :param filename:  Should be a filepath to a properly-formatted .hlsp
                          file written in YAML.
        :type filename:  str
        """

        # Access the given file.
        load_dict = read_yaml(filename)

        # Read the contents of the resulting dictionary.
        for key, val in load_dict.items():

            # Turn keys in 'KeywordUpdates' format to 'keyword_updates' format.
            key = re.findall('[A-Z][^A-Z]*', key)
            attr = "_".join([k.lower() for k in key])

            # All attributes in an .hlsp file should have already been
            # initialized by self.__init__().
            try:
                getattr(self, attr)
            except AttributeError:
                err = "{0} is not a properly formatted .hlsp file!".format(
                    filename)
                self = HLSPFile()
                raise IOError(err)

            # If reading in file_types or keyword_updates sections, use the
            # class methods to add the appropriate objects to self.
            if attr == "file_types":
                for ftype in val:
                    name, parameters = self._split_name_from_params(ftype)
                    as_obj = FileType(name, param_dict=parameters)
                    self.add_filetype(as_obj)
            elif attr == "keyword_updates":
                for kw in val:
                    keyword, parameters = self._split_name_from_params(kw)
                    as_obj = FitsKeyword(keyword, parameters=parameters)
                    self.add_keyword_update(as_obj)

            # Otherwise just set the attribute.
            else:
                setattr(self, attr, val)

        print("Loaded information for {0}".format(self.hlsp_name))

    def member_fits_standards(self):
        """
        Get a list of all FITS standards being used by file types present in
        the file_types list.
        """

        # Return immediately if there are no file types to examine.
        if len(self.file_types) == 0:
            return None

        standards = []
        for ft in self.file_types:

            # If the current FileType object is not being checked for HLSP
            # FITS metadata, skip it.
            if not (ft.standard and ft.product_type and ft.run_check):
                continue

            # Format the FITS standard name and add it to the list.
            std = "_".join([ft.product_type, ft.standard])
            if std not in standards:
                standards.append(std)

        # Return the results.
        if len(standards) > 0:
            return standards
        else:
            return None

    def remove_filetype(self, filetype_obj):
        """
        Remove a FileType object from the file_types list.

        :param filetype_obj:  The target file type to remove.
        :type filetype_obj:  FileType
        """

        # Search for a matching FileType object and remove it from
        # self.file_types.
        type_to_remove = filetype_obj.ftype
        for ft in self.file_types:
            if ft.ftype == type_to_remove:
                self.file_types.remove(ft)
                break

    def save(self, filename=None):
        """
        Write the current contents of self to a YAML-formatted .hlsp file.

        :param filename:  Designate a file name to use for saving (optional).
        :type filename:  str
        """

        # Make sure a provided file name has an .hlsp extension.
        if filename:
            if not filename.endswith(".hlsp"):
                filename = ".".join([filename, "hlsp"])

        # Construct a file name if none provided.
        else:
            filename = ".".join([self.hlsp_name, "hlsp"])

        # Format self as a dictionary and write it to YAML.
        with open(filename, 'w') as yamlfile:
            yaml.dump(self.as_dict(), yamlfile, default_flow_style=False)
            print("...saving {0}...".format(filename))

        return filename

    def toggle_updated(self, flag):
        #self.updated = flag
        pass

    def update_filepaths(self, input=None, output=None):
        """
        Update the file_paths dictionary with provided input / output settings.

        :param input:  A file path to find HLSP data files.
        :type input:  str

        :param output:  A file path to write a CAOM template XML file to.
        :type output:  str
        """

        new_paths = {}

        if input:
            new_paths["InputDir"] = input
        if output:
            new_paths["Output"] = output

        self.file_paths.update(new_paths)

    def write_xml_template(self, output=None):
        """
        Write the current contents of self into an XML-formatted template file
        for ingestion into CAOM.

        :param output:  A file name for the resulting XML file (optional).
        :type output:  str
        """

        # If output is not provided, get the default file name from the
        # self.file_paths dictionary.
        if not output:
            output = self.file_paths["Output"]

        # Check that output is a valid file path & name.
        output = cp.check_new_file(output)

        # Create a 'CompositeObservation' XML tree and add the three primary
        # subtrees.
        composite = etree.Element("CompositeObservation")
        xmltree = etree.ElementTree(composite)
        metadata = etree.SubElement(composite, "metadataList")
        provenance = etree.SubElement(composite, "provenance")
        products = etree.SubElement(composite, "productList")

        # Add all file types to the XML tree using the FileType class method.
        for ft in sorted(self.file_types):
            xmltree = ft.add_to_xml(xmltree)

        # Add all FITS keyword updates to the XML tree using the FitsKeyword
        # class method.
        for kw in sorted(self.fits_keywords()):
            xmltree = kw.add_to_xml(xmltree)

        # Add all unique parameters to the XML tree.
        for parent, parameters in self.unique_parameters.items():
            parent = xmltree.find(parent)
            parent = self._add_xml_value_pairs(parent, parameters)

        # Write the XML tree out to file.
        xmltree.write(output,
                      encoding="utf-8",
                      xml_declaration=True,
                      pretty_print=True,
                      )

# --------------------


def __test__():
    h = HLSPFile()
    h.save("test_ouput")

# --------------------


if __name__ == "__main__":
    __test__()
