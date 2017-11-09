from lxml import etree

def fudge_for_kepler(xmltree):
    print("fudging...")
    root = xmltree.getroot()
    metadata = xmltree.find("metadataList")
    instrumentKeywords = metadata.findall("instrument_keywords")
    for instance in instrumentKeywords:
        headerKeyword = instance.find("headerKeyword")
        headerName = instance.find("headerName")
        headerDefaultValue = instance.find("headerDefaultValue")
        hk_text = headerKeyword.text
        if hk_text == "FILTER":
            headerDefaultValue.text = "KEPLER"
    #    if instance["headerKeyword"] == "FILTER":
    #        instance["headerDefaultValue"] = "Kepler"

    return xmltree
