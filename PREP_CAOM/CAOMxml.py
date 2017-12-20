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

#--------------------

class CAOMxml:
    """
    A CAOMxml object pairs a CAOM parameter with various information depending
    on what type of parameter is being defined.
    """

    def __init__(self, label):
        """
        Create a new CAOMxml object with a few default parameters.

        :param label:  This is the actual CAOM parameter being defined.
        :type label:  str
        """
        #Common properties
        self.label = label
        self.parent = "CompositeObservation"
        self.source = None

    def send_to_lxml(self, xmltree):
        """
        Create a new subelement within xmltree for a given CAOMxml object.
        Multiple parameters read from the CAOMxml object are used to organize,
        label, and otherwise fill out the XML entry.

        :param xmltree:  This is an lxml tree where CAOMxml objects are
        described in order to ingest files into CAOM.
        :type xmltree:  lxml etree.ElementTree
        """
        #Search every element of the xmltree.
        for element in xmltree.iter():

            #Create a new subelement if an element matches the CAOMxml object's
            #'parent' parameter.
            if element.tag == self.parent:
                entry = etree.SubElement(element, self.label)
                if self.source == "VALUE":
                    s = etree.SubElement(entry, "source")
                    s.text = self.source
                    v = etree.SubElement(entry, "value")
                    v.text = self.value
                elif self.source == "HEADER":
                    s = etree.SubElement(entry, "source")
                    s.text = self.source
                    hn = etree.SubElement(entry, "headerName")
                    hn.text = self.headerName
                    hk = etree.SubElement(entry, "headerKeyword")
                    hk.text = self.headerKeyword
                    hdv = etree.SubElement(entry, "headerDefaultValue")
                    hdv.text = self.headerDefaultValue
                elif self.label == "product":
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
                return xmltree

        #If the 'parent' parameter is not found in xmltree, create it as a new
        #subelement and try again.
        new_parent = etree.SubElement(xmltree.getroot(), self.parent)
        return self.send_to_lxml(xmltree)

    def __str__(self):
        return "{0}: parent={1}".format(self.label,
                                        self.parent)

#--------------------

class CAOMvalue(CAOMxml):
    """
    A CAOMvalue object sets source to VALUE and adds a value parameter.
    """

    def __init__(self, label):
        CAOMxml.__init__(self, label)
        self.source = "VALUE"
        self.value = "None"

    def __str__(self):
        return "{0}: parent={1}, value={2}".format(self.label,
                                                   self.parent,
                                                   self.value)

#--------------------

class CAOMheader(CAOMxml):
    """
    A CAOMheader object sets source to HEADER, creates a few header parameters
    and sets a few default values.
    """

    def __init__(self, label):
        CAOMxml.__init__(self, label)
        self.source = "HEADER"
        self.headerName = "PRIMARY"
        self.headerKeyword = None
        self.headerDefaultValue = "None"

    def __str__(self):
        return ("{0}: parent={1}, headerName={2}, headerKeyword={3}"
                .format(self.label,
                        self.parent,
                        self.headerName,
                        self.headerKeyword))

#--------------------

class CAOMproduct(CAOMxml):
    """
    A CAOMproduct adds a number of new parameters and default values, even
    setting the label to default to "product".
    """

    def __init__(self):
        CAOMxml.__init__(self, label="product")
        self.parent = "productList"
        self.calibrationLevel = "HLSP"
        self.contentType = None
        self.dataProductType = None
        self.fileNameDescriptor = "FILEROOT"
        self.fileStatus = None
        self.fileType = None
        self.planeNumber = "1"
        self.productType = None
        self.releaseType = "DATA"
        self.statusAction = None

    def __str__(self):
        return ("{0}: contentType={1}, fileType={2}, productType={3}"
                .format(self.label,
                        self.contentType,
                        self.fileType,
                        self.productType))

#--------------------

class CAOMxmlList(list):
    """
    A CAOMxmlList object maintains a list of CAOMxml (and subtypes) objects.
    """

    def __init__(self):
        super().__init__
        self.labels = []

    def add(self, caom_obj):
        if not isinstance(caom_obj, CAOMxml):
            print("CAOMxmlList cannot accept members other than CAOMxml!")
            return self
        self.append(caom_obj)
        self.labels.append(caom_obj.label)

    def findlabel(self, target):
        assert isinstance(target, str)
        if target in self.labels:
            for member in self:
                if member.label == target:
                    return member
        else:
            return None

    def findheader(self, target):
        assert isinstance(target, str)
        for member in self:
            if isinstance(member, CAOMheader):
                if member.headerKeyword == target:
                    return member
        else:
            return None

    def sort(self):
        sorted_labels = sorted(self.labels)
        sorted_objs = CAOMxmlList()
        for label in sorted_labels:
            obj = self.findlabel(label)
            sorted_objs.add(obj)
            self.remove(obj)
        return sorted_objs

#--------------------

if __name__ == "__main__":
    x = CAOMproduct()
    print(x.label)
    print(x.parent)
