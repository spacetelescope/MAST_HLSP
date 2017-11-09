from lxml import etree

class CAOMxml:

    def __init__(self, label):
        self.label = label
        self.source = None
        self.headerName = "PRIMARY"
        self.headerKeyword = None
        self.headerDefaultValue = "None"
        self.parent = "CompositeObservation"
        self.value = "None"

    def send_to_lxml(self, xmltree):
        for element in xmltree.iter():
            if element.tag == self.parent:
                entry = etree.SubElement(element, self.label)
                s = etree.SubElement(entry, "source")
                s.text = self.source
                if self.source == "VALUE":
                    v = etree.SubElement(entry, "value")
                    v.text = self.value
                elif self.source == "HEADER":
                    hn = etree.SubElement(entry, "headerName")
                    hn.text = self.headerName
                    hk = etree.SubElement(entry, "headerKeyword")
                    hk.text = self.headerKeyword
                    hdv = etree.SubElement(entry, "headerDefaultValue")
                    hdv.text = self.headerDefaultValue
                return xmltree
        new_parent = etree.SubElement(xmltree.getroot(), self.parent)
        return self.send_to_lxml(xmltree)

if __name__ == "__main__":
    x = CAOMxml()
    print(x.parent)
    x.parent = "Echo"
    print(x.parent)
