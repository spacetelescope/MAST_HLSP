"""
..class:: CAOMxml
    :synopsis: The CAOMxml class allows for more reliable transport of multiple
    variables associated with a CAOM XML entry by reducing the number of
    complex dictionary operations and indexing assumptions needed in
    hlsp_to_xml.py and its children.
"""

from lxml import etree

#--------------------

class CAOMxml:

    def __init__(self, label):
        """
        Create a new CAOMxml object with a few default parameters.
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

    def properties(self):
        """
        An easy way to print out all the current parameter values of a given CAOMxml object.
        """
        description = self.label + ":"
        description += " parent=" + self.parent
        if self.source:
            description += " source=" + self.source
        description += " headerName=" + self.headerName
        if self.headerKeyword:
            description += " headerKeyword=" + self.headerKeyword
        description += " headerDefaultValue=" + self.headerDefaultValue
        description += " value=" + self.value
        print(description)

#--------------------

class CAOMvalue(CAOMxml):

    def __init__(self, label):
        CAOMxml.__init__(self, label)
        self.source = "VALUE"
        self.value = "None"

#--------------------

class CAOMheader(CAOMxml):
    def __init__(self, label):
        CAOMxml.__init__(self, label)
        self.source = "HEADER"
        self.headerName = "PRIMARY"
        self.headerKeyword = None
        self.headerDefaultValue = "None"

#--------------------

class CAOMproduct(CAOMxml):
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

#--------------------

if __name__ == "__main__":
    x = CAOMproduct()
    print(x.label)
    print(x.parent)
    x.properties()
