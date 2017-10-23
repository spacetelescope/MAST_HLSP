from start_hlsp_xml import start_hlsp_xml
from add_lightcurve_xml import add_lightcurve_xml
from add_productlist_xml import add_productlist_xml

EXTENSIONS = "/Users/pforshay/Documents/1709_hlsp/MAST-HLSP/PREP_CAOM/fake_hlsp_extensions.csv"
HLSPPATH = "/Users/pforshay/Documents/1709_hlsp/hlsp_data"
OUTPUT = "/Users/pforshay/Documents/1709_hlsp/COOL/ididit.xml"
TABLE = "/Users/pforshay/Documents/1709_hlsp/MAST-HLSP/PREP_CAOM/hlsp_keywords_test.csv"
TYPE = "kepler"

if __name__ == "__main__":
    tree = start_hlsp_xml(OUTPUT, TABLE, TYPE)
    tree = add_lightcurve_xml(tree)
    tree = add_productlist_xml(HLSPPATH, EXTENSIONS, tree)
    tree.write(OUTPUT, encoding="UTF-8", xml_declaration=True,
               pretty_print=True)
