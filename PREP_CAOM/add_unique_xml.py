import add_xml_entries as axe

def add_unique_xml(unique_parameters, tree):
    """
    Add CAOM parameters that are unique to this HLSP and not contained in
    headers.

    :param tree:  The xml tree object that these subelements will be added to.
    :type tree:  _ElementTree from lxml
    """

    print("Adding unique HLSP information...")

    #Define the parents to add subelements to
    metadata = "metadataList"
    provenance = "provenance"
    products = "productList"

    hlsp_provenance = unique_parameters[provenance]

    tree = axe.add_value_subelements(tree, hlsp_provenance, provenance)

    print("...done!")
    return tree
