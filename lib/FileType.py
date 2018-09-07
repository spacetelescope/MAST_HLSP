import re


class FileType(object):

    valid_cpt = ["auxiliary", "preview", "science", "thumbnail"]
    valid_ft = ["fits", "graphic", "none", "text"]
    valid_pt = ["catalog", "image", "spectrum", "timeseries"]

    def __init__(self, ftype, param_dict=None):
        self.ftype = ftype.lower()
        self.caom_product_type = "science"
        self.file_type = "none"
        self.include = True
        self.mrp_check = True
        self.product_type = "image"
        self.run_check = (True if ftype.endswith(".fits") else False)
        self.standard = None

        self._graphics_ext = ["jpeg", "jpg", "png", "tiff", "pdf"]
        self._texts_ext = ["csv", "md", "txt"]
        self.ext = self._get_ext()
        if self.ext == "fits":
            self.file_type = "fits"
        elif self.ext in self._graphics_ext:
            self.file_type = "graphic"
        elif self.ext in self._texts_ext:
            self.file_type = "text"

        if param_dict and not self._empty_dict_check(param_dict):
            for key, val in param_dict.items():
                #print("<<<FileType using param_dict>>>{0}".format(param_dict))
                key = self._format_attr_name(key)
                setattr(self, key, val)

    def __repr__(self):
        public_dict = {k: v for k, v in self.__dict__.items()
                       if not k[0] == '_'}
        return "<FileType({0}: {1})>".format(self.ftype, public_dict)

    def __lt__(self, another):
        return (self.ftype < another.ftype)

    @staticmethod
    def _empty_dict_check(param_dict):
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

    def _get_ext(self):
        return ".".join(self.ftype.split(".")[1:])

    @property
    def caom_product_type(self):
        return self._caom_product_type

    @caom_product_type.setter
    def caom_product_type(self, caom_type):
        # ct = ["auxiliary", "preview", "science", "thumbnail"]
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

    def as_dict(self):
        key = self.ftype
        params = {}
        skip = ["ext", "ftype", "_graphics_ext", "_texts_ext"]
        for k in sorted(self.__dict__.keys()):
            if k in skip:
                continue
            name = self._format_dict_name(k)
            params[name] = getattr(self, k)
        return {key: params}


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


if __name__ == "__main__":
    __test__()
