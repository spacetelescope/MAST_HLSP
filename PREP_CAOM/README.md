/MAST-HLSP/PREP_CAOM/README.md
:Updated: 2017 Oct 27
:Author: Peter Forshay
___
The files in this directory are used to create an XML document that will allow  
data files from an HLSP to be ingested into CAOM.  The Python scripts attempt  
to automate as much of the process as possible, and we try to provide  
templates and guidance for necessary HLSP-specific coding.  The file structure  
is described below:  
___
"fake_lightcurve_hlsp.py"  
This is the wrapper script intended to launch all necessary child scripts  
and contain any operations required specifically for a single HLSP.  This  
script will need to be generated for each HLSP, using this version as a  
template.  
|
--->"start_hlsp_xml.py"  
|This script will begin creation of the output XML file and check  
|provided filepaths.  It also writes as much generic HLSP information  
|as possible to xml.  
||  
|--->"hlsp_keywords_test.csv"  
||This table contains CAOM parameter keywords, and a  
||translation table for multiple sets of accepted fits header  
||keywords.  Parent xml elements are also listed for each  
||keyword.  
|  
--->"add_lightcurve_xml.py"  
|This script adds as much generic light curve information as possible  
|to the xml.  Similar scripts will be added for additional data types  
|(spectra, catalogs, etc.).  
|  
--->"add_productlist_xml.py"  
|This script crawls the provided HLSP filepath and creates a product  
|entry for all files matching a defined file extension.  
||  
|--->"fake_hlsp_extensions.csv"  
||This file contains a list of data file extensions to search  
||for in the HLSP filepath and corresponding CAOM product  
||properties to define for each.  
V          
"add_xml_entries.py"  
This script is called from several others to generate xml subelements with  
proper CAOM formatting.  Modules are available for creating both VALUE  
    subelements and HEADER subelements.  
