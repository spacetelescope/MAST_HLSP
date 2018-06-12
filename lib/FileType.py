

class FileType(object):

    def __init__(self, ftype, param_dict=None):
        self.ftype = ftype
        self.caom_product_type = "science"
        self.file_type = "none"
        self.mrp_check = True
        self.product_type = "image"
        self.run_check = False
        self.standard = None

        if param_dict:
            [setattr(self, key, val) for key, val in param_dict.items()]

    def __repr__(self):
        return "<FileType({0.ftype}: {0.__dict__})>".format(self)

    def __lt__(self, another):
        return (self.ftype < another.ftype)

    @property
    def caom_product_type(self):
        return self._caom_product_type

    @caom_product_type.setter
    def caom_product_type(self, caom_type):
        ct = ["auxiliary", "preview", "science", "thumbnail"]
        new_type = caom_type.lower()
        assert new_type in ct
        self._caom_product_type = new_type

    @property
    def file_type(self):
        return self._file_type

    @file_type.setter
    def file_type(self, ftype):
        ft = ["fits", "graphic", "none", "text"]
        new_type = ftype.lower()
        assert new_type in ft
        self._file_type = new_type

    @property
    def mrp_check(self):
        return self._mrp_check

    @mrp_check.setter
    def mrp_check(self, status):
        if isinstance(status, bool):
            self._mrp_check = status
        else:
            err = "FileType.mrp_check given a non-boolean value."
            raise ValueError(err)

    @property
    def product_type(self):
        return self._product_type

    @product_type.setter
    def product_type(self, ptype):
        pt = ["catalog", "image", "spectrum", "timeseries"]
        new_type = ptype.lower()
        if new_type in pt:
            self._product_type = new_type
        else:
            err = "{0} is not a valid value for FileType.product_type.".format(
                ptype)
            raise ValueError(err)

    @property
    def run_check(self):
        return self._run_check

    @run_check.setter
    def run_check(self, status):
        if isinstance(status, bool):
            self._run_check = status
        else:
            err = "FileType.run_check given a non-boolean value."
            raise ValueError(err)

    @property
    def standard(self):
        return self._standard

    @standard.setter
    def standard(self, std):
        self._standard = std


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
    print(l)


if __name__ == "__main__":
    __test__()
