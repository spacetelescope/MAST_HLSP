import util.add_xml_entries as axe
import logging

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
    hlsp_metadata = None
    hlsp_provenance = None
    hlsp_products = None

    try:
        hlsp_metadata = unique_parameters[metadata]
    except KeyError:
        logging.info("No unique metadataList parameters defined.")
    try:
        hlsp_provenance = unique_parameters[provenance]
    except KeyError:
        logging.info("No unique provenance parameters defined.")
    try:
        hlsp_products = unique_parameters[products]
    except KeyError:
        logging.info("No unique productList parameters defined.")

    if hlsp_metadata:
        tree = axe.add_value_subelements(tree, hlsp_metadata, metadata)
    if hlsp_provenance:
        tree = axe.add_value_subelements(tree, hlsp_provenance, provenance)
    if hlsp_products:
        tree = axe.add_value_subelements(tree, hlsp_products, products)

    print("...done!")
    return tree
