from lxml import etree
import re

# --------------------


class FileType(object):
    """
    This class constructs an object to manage attributes of a file type for
    use during HLSP ingestion.  These are described at a per-observation level
    for CAOM, and are included in the XML template file passed to CAOM for
    inclusion in the MAST Portal.

    ..method::  _empty_dict_check
    ..synopsis::  Examine a dictionary of file type parameters for a single
                  'none' entry.

    ..method::  _format_attr_name
    ..synopsis::  Change a capitalized ExampleKey used by the YAML format into
                  a lower-case example_key used by the class attributes.

    ..method::  _format_dict_name
    ..synopsis::  Change a lower-case example_key used by the class attributes
                  into a capitalized ExampleKey used by the YAML format.

    ..method::  _get_caom_filetype
    ..synopsis::  Modify the ftype attribute to return information for CAOM.

    ..method::  _get_ext
    ..synopsis::  Modify the ftype attribute to return information for CAOM.

    ..method::  _get_xml_dict
    ..synopsis::  Format certain attributes in a dictionary for inclusion in
                  a CAOM template XML file.

    ..method::  add_to_xml
    ..synopsis::  Add self to an XML tree formatted for a CAOM template file.

    ..method::  as_dict
    ..synopsis::  Return certain attributes of self in a dictionary.

    ..property::  caom_product_type
    ..synopsis::  This property checks a list of acceptable values.

    ..property::  file_type
    ..synopsis::  This property checks a list of acceptable values.

    ..property::  mrp_check
    ..synopsis::  This property must be a boolean type.

    ..property::  product_type
    ..synopsis::  This property checks a list of acceptable values.

    ..property::  run_check
    ..synopsis::  This property must be a boolean type.
    """

    # These values are standard and will be added to every file type before
    # adding to a CAOM template XML file.
    every_filetype = {"calibrationLevel": "HLSP",
                      "fileNameDescriptor": "FILEROOTSUFFIX",
                      "planeNumber": 1,
                      "releaseType": "DATA"}

    # Set up lists for acceptable attribute values.
    valid_cpt = ["auxiliary", "preview", "science", "thumbnail"]
    valid_ft = ["fits", "graphic", "none", "text"]
    valid_pt = ["catalog", "image", "spectrum", "timeseries"]

    def __init__(self, ftype, param_dict=None):
        """
        Initialize a FileType object.

        :param ftype:  A file type string for reference.  Expect a
                       'fileend.extension' format.
        :type ftype:  str

        :param param_dict:  An optional of dictionary of parameters to load
                            into a new FileType object.
        :type param_dict:  dict
        """

        # Initialize main attributes.
        self.ftype = ftype.lower()
        self.caom_product_type = "science"
        self.file_type = "none"
        self.include = True
        self.mrp_check = True
        self.product_type = "image"
        self.run_check = (True if ftype.endswith(".fits") else False)
        self.standard = None

        # Set up private lists to categorize certain file extensions.
        self._graphics_ext = ["jpeg", "jpg", "png", "tiff", "pdf"]
        self._texts_ext = ["csv", "md", "txt"]

        # Update the file_type attribute based on the given file extension.
        self.ext = self._get_ext()
        if self.ext == "fits":
            self.file_type = "fits"
        elif self.ext in self._graphics_ext:
            self.file_type = "graphic"
        elif self.ext in self._texts_ext:
            self.file_type = "text"

        # Load param_dict values into self if provided.
        if param_dict and not self._empty_dict_check(param_dict):
            for key, val in param_dict.items():
                key = self._format_attr_name(key)
                setattr(self, key, val)

    def __repr__(self):
        """
        Format attributes of self for string representations.
        """

        # Skip private attributes beginning with '_'.
        public_dict = {k: v for k, v in self.__dict__.items()
                       if not k[0] == '_'}

        return "<FileType({0}: {1})>".format(self.ftype, public_dict)

    def __lt__(self, another):
        """
        Compare two FileType objects for sorting purposes.

        :param another:  A comparison object.
        :type another:  FileType
        """

        # Check another for a FileType attribute.
        try:
            x = another.ftype
        except AttributeError:
            err = "{0} must be a <FileType> class obj for comparison.".format(
                another)
            raise TypeError(err)

        return (self.ftype < another.ftype)

    @staticmethod
    def _empty_dict_check(param_dict):
        """
        Examine a dictionary of file type parameters for a single 'none' entry.

        :param param_dict:  A possible dictionary of parameters to add to self.
        :type param_dict:  dict
        """

        vals = list(set(param_dict.values()))
        if (len(vals) == 1) and (str(vals[0]).lower() == "none"):
            return True
        else:
            return False

    @staticmethod
    def _format_attr_name(var):
        """
        Change a capitalized ExampleKey used by the YAML format into a lower-
        case example_key used by the class attributes.
        """

        # Split the string along captial letters into a list.
        var = re.findall('[A-Z][^A-Z]*', var)

        # Detect series of capital letters from an acronym and group those
        # into a single word (ex: ['C', 'A', 'O', 'M', 'Product'] ->
        # ['CAOM', 'Product'])
        acronym = -1
        tmp = ""
        for n in range(len(var)):
            v = var[n]
            if len(v) == 1 and acronym < 0:
                acronym = n
                tmp = str(v)
                var[n] = ""
            elif len(v) == 1 and acronym >= 0:
                tmp = "".join([tmp, v])
                var[n] = ""
            elif len(v) > 1 and acronym >= 0:
                var[acronym] = str(tmp)
                acronym = -1
                tmp = ""

        var = "_".join([v.lower() for v in var if not v == ""])
        return var

    @staticmethod
    def _format_dict_name(var):
        """
        Change a lower-case example_key used by the class attributes into a
        capitalized ExampleKey used by the YAML format.
        """

        var = var.split("_")
        var = "".join([v.capitalize() for v in var])
        return var

    def _get_caom_filetype(self):
        """
        Modify the ftype attribute to return information for CAOM.
        """
        return self.ftype.split(".")[0]

    def _get_ext(self):
        """
        Modify the ftype attribute to return information for CAOM.
        """
        return ".".join(self.ftype.split(".")[1:])

    def _get_xml_dict(self):
        """
        Format certain attributes in a dictionary for inclusion in a CAOM
        template XML file.
        """

        # Add attributes from self.
        xml_dict = {"contentType": self.ext.upper(),
                    "dataProductType": self.product_type.upper(),
                    "fileType": self._get_caom_filetype().upper(),
                    "productType": self.caom_product_type.upper(),
                    }

        # Add standard parameters for every file type.
        xml_dict.update(self.every_filetype)

        return xml_dict

    def add_to_xml(self, xmltree):
        """
        Add self to an XML tree formatted for a CAOM template file.

        :param xmltree:  The XML tree must already be under construction before
                         adding FileType objects.
        :type xmltree:  lxml.etree.ElementTree
        """

        # Prepare the needed information in a dictionary.
        xml_dict = self._get_xml_dict()

        # Update 'fileStatus' and 'statusAction' depending on whether self is
        # a FITS file.
        if self.ext.upper() == "FITS":
            xml_dict["fileStatus"] = "REQUIRED"
            xml_dict["statusAction"] = "ERROR"
        else:
            xml_dict["fileStatus"] = "OPTIONAL"
            xml_dict["statusAction"] = "WARNING"

        # All FileType objects will be added to the 'productList' section of
        # the XML tree.
        pl = xmltree.find("productList")
        product = etree.SubElement(pl, "product")

        # Add the information to the new subelement.
        for key in sorted(xml_dict.keys()):
            parameter = etree.SubElement(product, key)
            parameter.text = str(xml_dict[key])

        return xmltree

    def as_dict(self):
        """
        Return certain attributes of self in a dictionary.
        """

        key = self.ftype
        params = {}

        # Create a list of attributes to omit.
        skip = ["ext", "ftype", "_graphics_ext", "_texts_ext"]

        # Populate the dictionary.
        for k in sorted(self.__dict__.keys()):
            if k in skip:
                continue
            name = self._format_dict_name(k)
            params[name] = getattr(self, k)

        return {key: params}

    @property
    def caom_product_type(self):
        return self._caom_product_type

    @caom_product_type.setter
    def caom_product_type(self, caom_type):
        if caom_type is None:
            return
        else:
            new_type = str(caom_type).lower()

        if new_type in self.valid_cpt:
            self._caom_product_type = new_type
        else:
            raise ValueError("'{0}' is not a valid FileType.caom_product_type!"
                             " (valid={1})".format(caom_type, ct))

    @property
    def file_type(self):
        return self._file_type

    @file_type.setter
    def file_type(self, ftype):
        # ft = ["fits", "graphic", "none", "text"]
        new_type = str(ftype).lower()
        if new_type in self.valid_ft:
            self._file_type = new_type
        else:
            raise ValueError("'{0}' is not a valid FileType.file_type! "
                             "(valid={1})".format(ftype, self.valid_ft))

    @property
    def mrp_check(self):
        return self._mrp_check

    @mrp_check.setter
    def mrp_check(self, status):
        if isinstance(status, bool):
            self._mrp_check = status
        elif str(status).lower() == "none":
            self._mrp_check = False
        else:
            err = "FileType.mrp_check given a non-boolean value."
            raise ValueError(err)

    @property
    def product_type(self):
        return self._product_type

    @product_type.setter
    def product_type(self, ptype):
        # pt = ["catalog", "image", "spectrum", "timeseries"]
        new_type = str(ptype).lower()
        if new_type in self.valid_pt:
            self._product_type = new_type
        else:
            raise ValueError("'{0}' is not a valid FileType.product_type! "
                             "(valid={1})".format(ptype, self.valid_pt))

    @property
    def run_check(self):
        return self._run_check

    @run_check.setter
    def run_check(self, status):
        if isinstance(status, bool):
            self._run_check = status
        elif str(status).lower() == "none":
            self._run_check = False
        else:
            err = "FileType.run_check given a non-boolean value."
            raise ValueError(err)

    @property
    def standard(self):
        return self._standard

    @standard.setter
    def standard(self, std):
        self._standard = std

# --------------------


def __test__():
    f = FileType("this")
    f.caom_product_type = "auxiliary"
    f.file_type = "text"
    f.mrp_check = False
    f.product_type = "Spectrum"
    f.run_check = True
    f.standard = "derp"
    k = FileType("zzz")
    l = sorted([k, f])
    print(f.as_dict())

# --------------------


if __name__ == "__main__":
    __test__()
