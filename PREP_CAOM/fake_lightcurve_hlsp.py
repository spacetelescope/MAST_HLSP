import start_hlsp_xml as shx
import add_lightcurve_xml as alx

OUTPUT = "/Users/pforshay/Documents/1709_hlsp/COOL/ididit.xml"
TABLE = "/Users/pforshay/Documents/1709_hlsp/MAST-HLSP/PREP-CAOM/hlsp_keywords_test.csv"
TYPE = "kepler"

if __name__ == "__main__":
    tree = shx.start_hlsp_xml(OUTPUT, TABLE, TYPE)
    tree = alx.add_lightcurve_xml(tree)
    tree.write(OUTPUT, encoding="UTF-8", xml_declaration=True,
               pretty_print=True)
