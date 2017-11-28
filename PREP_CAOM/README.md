/MAST-HLSP/PREP_CAOM/README.md  
:Updated: 2017 Nov 28  
:Author: Peter Forshay  

The files in this directory are used to create an XML document that will  
allow data files from an HLSP to be ingested into CAOM.  The Python scripts  
attempt to automate as much of the process as possible, and we try to provide  
templates and guidance for necessary HLSP-specific coding.  The file  
structure is described below:  
___
### /PREP_CAOM/  
+ "launch_gui.py"  
This script launches a PyQt window that contains widgets from  
config_generator.py and ext_generator.py inside a tabs widget.  This wrapper  
widget allows the user to quit or to launch a popup help dialog.  

+ "hlsp_to_xml.py"  
This is the wrapper script intended to launch all necessary child scripts.  
The user must also provide a .yaml config file when launching this script,  
which is then parsed and checked for all necessary parameters and file  
paths.  

+ "CAOMxml.py"  
This defines a custom CAOMxml object class and subclasses for CAOMvalue  
entries, CAOMheader entries, and CAOMproduct entries.  These classes help  
carry multiple parameters for a given XML entry without resorting to  
dictionaries of dictionaries.  String modules also simplify output of XML  
entries for debugging purposes.  

+ "add_static_values.py"  
Read in all appropriate static values from hlsp_caom_staticvalues.yaml and  
create CAOMvalue objects.  Additions are made based on data types indicated  
in the user-provided yaml config file, as well as the indicated FITS header  
type.  

+ "add_header_entries.py"  
Read in the header keywords translation table based on which header type  
the user has designated.  Create a CAOMheader object for each header.  

+ "add_product_caomxml.py"  
This script crawls the provided HLSP file path and creates a CAOMproduct  
object for each file type matching a set of defined file extensions.  
___
### /PREP_CAOM/util/
+ "add_value_caomxml.py"  
This script recursively creates CAOMvalue objects for dictionaries of  
parameters.  This is used to create entries for the static values in  
add_static_values.py and any user-provided unique parameters defined in the  
yaml config file.  

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
___
### /PREP_CAOM/gui/
+ "ext_generator.py"  
This PyQt widget allows the user to construct a CSV table with descriptions  
of HLSP data files that hlsp_to_xml.py will scan for.  The user can add any  
number of file types or load an existing CSV file to modify.  

+ "config_generator.py"  
This PyQt widget allows the user to generate a YAML config file to send to  
hlsp_to_xml.py containing all necessary filepaths and setting information.  
The user can define any number of HLSP-specific parameters to insert or load  
an existing YAML file to modify.  There is also an option to immediately launch  
hlsp_to_xml.py after saving the YAML file.
