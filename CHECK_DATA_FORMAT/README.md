# Instructions To Run CHECK_DATA_FORMAT

## Running The Pre-Check Program
This step will look at every file underneath your input directory and create
a parameter file that you will modify manually, based on the different types
of extensions it finds.

### Example Usage
python precheck_data_format.py *some_dir*/*some_hlspname* *some_hlspname*

## Running The GUI To Select Templates
This step will use a GUI to fill in template and file type choices so the
software knows how to check for HLSP compliance.

### Example Usage
python select_data_templates.py *name_of_precheck_data_format_output_file*

## Running The Check Data Program
This step will use the template selections to check every file for HLSP
compliance.

### Example Usage
python check_data_format.py *name_of_precheck_data_format_output_file*
