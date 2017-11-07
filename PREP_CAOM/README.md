/MAST-HLSP/PREP_CAOM/README.md  
:Updated: 2017 Nov 7  
:Author: Peter Forshay  

The files in this directory are used to create an XML document that will  
allow data files from an HLSP to be ingested into CAOM.  The Python scripts  
attempt to automate as much of the process as possible, and we try to provide  
templates and guidance for necessary HLSP-specific coding.  The file  
structure is described below:  
___
### /PREP_CAOM/  
+ "hlsp_to_xml.py"  
This is the wrapper script intended to launch all necessary child scripts.  
The user must also provide a .yaml config file when launching this script,  
which is then parsed and checked for all necessary parameters and file  
paths.  

+ "add_static_values.py"  
Read in all appropriate static values from hlsp_caom_staticvalues.yaml and  
add these to the xml tree.

+ "add_header_entries.py"  
Read in the header keywords translation table based on which header type  
the user has designated.  Add these to the xml tree.

+ "add_productlist_xml.py"  
This script crawls the provided HLSP file path and creates a product  
entry for each file type matching a set of defined file extensions.  

+ "add_unique_xml.py"  
This script adds CAOM parameters unique to a certain HLSP provided in the  
.yaml config file.  
___
### /PREP_CAOM/util/
+ "add_xml_entries.py"  
This script is called from several others to generate xml subelements with  
proper CAOM formatting.  Modules are available for creating both VALUE  
subelements and HEADER subelements.  

+ "check_log.py"  
This script scans the resulting log file at the end of the script to display  
stats on errors and warnings logged.  

+ "check_paths.py"  
This script contains a number of modules to check user-provided file paths  
and potentially create new directories if they don't already exist.  

+ "read_yaml.py"  
Read in a .yaml file and return the contents as a dictionary.  
___
### /PREP_CAOM/resources/
+ "hlsp_caom_staticvalues.yaml"
This file contains CAOM parameters and static values to fill them with for  
certain types of HLSPs.  

+ "hlsp_keywords.csv"  
This table contains CAOM parameter keywords, and a translation table for  
multiple sets of accepted fits header keywords.  Parent xml elements are  
also listed for each keyword.  
