"""
..class::  CAOMxml
    :synopsis: The CAOMxml class allows for more reliable transport of multiple
    variables associated with a CAOM XML entry by reducing the number of
    complex dictionary operations and indexing assumptions needed in
    hlsp_to_xml.py and its children.

..class::  CAOMxmlList
    :synopsis:  This class maintains a list of CAOMxml objects, providing a
    ready-made list of labels contained in the list, modules for returning list
    members based on various search parameters, and a way to sort the list for
    final writing to file.
"""

from lxml import etree

# --------------------


class CAOMxml(object):
    """ A CAOMxml object pairs a CAOM parameter with various information
    depending on what type of parameter is being defined.
    """

    def __init__(self, label, parent="CompositeObservation", source=None):
        """
        Create a new CAOMxml object with a few default parameters.

        :param label:  This is the actual CAOM parameter being defined.
        :type label:  str
        """

        # Common properties
        self.label = label
        self.parent = parent
        self.source = source

    def __lt__(self, another):
        return (self.label < another.label)

    def __str__(self):
        return "{0.label}: parent={0.parent}".format(self)

    def attributes_dict(self):
        d = {key: val for key, val in self.__dict__.items() if "__" not in key}
        return d

    def fill_lxml_entry(self, entry):
        s = etree.SubElement(entry, "source")
        s.text = "None"

    def send_to_lxml(self, xmltree):
        """
        Create a new subelement within xmltree for a given CAOMxml object.
        Multiple parameters read from the CAOMxml object are used to organize,
        label, and otherwise fill out the XML entry.

        :param xmltree:  This is an lxml tree where CAOMxml objects are
                         described in order to ingest files into CAOM.
        :type xmltree:  lxml etree.ElementTree
        """
        # Search every element of the xmltree.
        for element in xmltree.iter():

            # Create a new subelement if an element matches the CAOMxml
            # object's 'parent' parameter.
            if element.tag == self.parent:
                entry = etree.SubElement(element, self.label)
                attributes = self.attributes_dict()
                for attr, val in attributes.items():
                    sub = etree.SubElement(entry, attr)
                    sub.text = val
                # self.fill_lxml_entry(entry)
                return xmltree

        # If the 'parent' parameter is not found in xmltree, create it as a new
        # subelement and try again.
        new_parent = etree.SubElement(xmltree.getroot(), self.parent)
        return self.send_to_lxml(xmltree)

# --------------------


class CAOMvalue(CAOMxml):
    """
    A CAOMvalue object sets source to VALUE and adds a value parameter.
    """

    source = "VALUE"

    def __init__(self, label):
        super().__init__(label, source=self.source)
        self.value = "None"

    def __str__(self):
        return "{0.label}: parent={0.parent}, value={0.value}".format(self)

    def fill_lxml_entry(self, entry):
        attributes = [k for k in self.__dict__.keys() if "__" not in k]
        for attr in attributes:
            subelement = etree.SubElement(entry, attr)
            subelement.text = getattr(self, attr)
        """
        s = etree.SubElement(entry, "source")
        s.text = self.source
        v = etree.SubElement(entry, "value")
        v.text = self.value
        """

# --------------------


class CAOMheader(CAOMxml):
    """
    A CAOMheader object sets source to HEADER, creates a few header
    parameters and sets a few default values.
    """

    source = "HEADER"

    def __init__(self, label):
        super().__init__(label, source=self.source)
        self.headerName = "PRIMARY"
        self.headerKeyword = None
        self.headerDefaultValue = "None"

    def __str__(self):
        return ("{0.label}: parent={0.parent}, headerName={0.headerName}, "
                "headerKeyword={0.headerKeyword}".format(self)
                )

    def fill_lxml_entry(self, entry):
        s = etree.SubElement(entry, "source")
        s.text = self.source
        hn = etree.SubElement(entry, "headerName")
        hn.text = self.headerName
        hk = etree.SubElement(entry, "headerKeyword")
        hk.text = self.headerKeyword
        hdv = etree.SubElement(entry, "headerDefaultValue")
        hdv.text = self.headerDefaultValue

# --------------------


class CAOMproduct(CAOMxml):
    """
    A CAOMproduct adds a number of new parameters and default values, even
    setting the label to default to "product".
    """

    label = "product"
    parent = "productList"

    def __init__(self):
        super().__init__(self.label, parent=self.parent)
        self.calibrationLevel = "HLSP"
        self.contentType = None
        self.dataProductType = None
        self.fileNameDescriptor = "FILEROOTSUFFIX"
        self.fileStatus = "OPTIONAL"
        self.fileType = None
        self.planeNumber = "1"
        self.productType = None
        self.releaseType = "DATA"
        self.statusAction = "WARNING"

    def __str__(self):
        return ("{0.label}: contentType={0.contentType}, "
                "fileType={0.fileType}, productType={0.productType}"
                .format(self)
                )

    def fill_lxml_entry(self, entry):
        attributes = [k for k in self.__dict__.keys() if "__" not in k]
        for attr in attributes:
            subelement = etree.SubElement(entry, attr)
            subelement.text = getattr(self, attr)
        """
        cl = etree.SubElement(entry, "calibrationLevel")
        cl.text = self.calibrationLevel
        ct = etree.SubElement(entry, "contentType")
        ct.text = self.contentType
        dpt = etree.SubElement(entry, "dataProductType")
        dpt.text = self.dataProductType
        fnd = etree.SubElement(entry, "fileNameDescriptor")
        fnd.text = self.fileNameDescriptor
        fs = etree.SubElement(entry, "fileStatus")
        fs.text = self.fileStatus
        ft = etree.SubElement(entry, "fileType")
        ft.text = self.fileType
        pn = etree.SubElement(entry, "planeNumber")
        pn.text = self.planeNumber
        pt = etree.SubElement(entry, "productType")
        pt.text = self.productType
        rt = etree.SubElement(entry, "releaseType")
        rt.text = self.releaseType
        sa = etree.SubElement(entry, "statusAction")
        sa.text = self.statusAction
        """

# --------------------


class CAOMxmlList(list):
    """
    A CAOMxmlList object maintains a list of CAOMxml (and subtypes)
    objects, and provides modules to manipulate the list.
    """

    def __init__(self):
        super().__init__
        self.labels = []

    def add(self, caom_obj):
        if isinstance(caom_obj, CAOMxml):
            self.append(caom_obj)
            self.labels.append(caom_obj.label)
        else:
            err = "CAOMxmlList cannot accept members other than CAOMxml!"
            raise TypeError(err)

    def findlabel(self, target):
        target = str(target)
        if target in self.labels:
            for member in self:
                if member.label == target:
                    return member
        else:
            return None

    def findheader(self, target):
        target = str(target)
        for member in self:
            if isinstance(member, CAOMheader):
                if member.headerKeyword == target:
                    return member
        else:
            return None

# --------------------


if __name__ == "__main__":
    x = CAOMproduct()
    print(x.__dict__)
