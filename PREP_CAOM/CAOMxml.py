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
        self.label = label
        self.parent = "CompositeObservation"
        self.source = None
        self.headerName = "PRIMARY"
        self.headerKeyword = None
        self.headerDefaultValue = "None"
        self.value = "None"

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

if __name__ == "__main__":
    x = CAOMxml("test")
    print(x.parent)
    x.parent = "Echo"
    x.properties()
