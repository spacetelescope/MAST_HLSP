


class FileType():

    param_names = ["CAOMProductType",
                   "FileType",
                   "MRPCheck",
                   "ProductType",
                   "RunCheck",
                   "Standard",
                  ]

    def __init__(self, ftype, param_dict=None):
        self.ftype = ftype

        if param_dict:
            self.params = {x: param_dict[x] for x in self.param_names}
        else:
            self.params = {x: None for x in self.param_names}

    def __repr__(self):
        return "<FileType({0.ftype}: {0.params})>".format(self)

    def __lt__(self, another):
        return (self.ftype < another.ftype)

    @property
    def CAOMProductType(self):
        return self.params["CAOMProductType"]

    @CAOMProductType.setter
    def CAOMProductType(self, caom_type):
        ct = ["auxiliary", "preview", "science", "thumbnail"]
        new_type = caom_type.lower()
        assert new_type in ct
        self.params["CAOMProductType"] = new_type

    @property
    def FileType(self):
        return self.params["FileType"]

    @FileType.setter
    def FileType(self, file_type):
        ft = ["fits", "graphic", "none", "text"]
        new_type = file_type.lower()
        assert new_type in ft
        self.params["FileType"] = new_type

    @property
    def MRPCheck(self):
        return self.params["MRPCheck"]

    @MRPCheck.setter
    def MRPCheck(self, status):
        assert type(status) is bool
        self.params["MRPCheck"] = status

    @property
    def ProductType(self):
        return self.params["ProductType"]

    @ProductType.setter
    def ProductType(self, product_type):
        pt = ["catalog", "image", "spectrum", "timeseries"]
        new_type = product_type.lower()
        assert new_type in pt
        self.params["ProductType"] = new_type

    @property
    def RunCheck(self):
        return self.params["RunCheck"]

    @RunCheck.setter
    def RunCheck(self, status):
        assert type(status) is bool
        self.params["RunCheck"] = status

    @property
    def Standard(self):
        return self.params["Standard"]

    @Standard.setter
    def Standard(self, std):
        self.params["Standard"] = std


if __name__ == "__main__":
    f = FileType("this")
    f.CAOMProductType = "auxiliary"
    f.FileType = "text"
    f.MRPCheck = False
    f.ProductType = "Spectrum"
    f.RunCheck = True
    f.Standard = "derp"
    k = FileType("zzz")
    l = sorted([k, f])
    print(l)
