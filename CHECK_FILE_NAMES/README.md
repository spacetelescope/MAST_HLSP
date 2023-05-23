This folder contains Python software for 1) checking that file names follow MAST HLSP convention, 2) changing any file name from uppercase to lowercase, and changing the signs ('+/-') in file names to 'p/m'.

## Usage
```
  check_file_names.py [-h] [--root_dir ROOT_DIR] [--exclude_missions [EXCLUDE_MISSIONS ...]] [--exclude_filters [EXCLUDE_FILTERS ...]]
                           [--skip_sym] [--lowercase_dirname] [--lowercase_filename] [--update_sign]
                           idir hlsp_name
```

- positional arguments:

  idir                  [Required] Full path to the folder containing HLSP files to check.

  hlsp_name             [Required] Name of the HLSP.

- optional arguments:

  -h, --help            show this help message and exit

  --root_dir ROOT_DIR   Optional root path to HLSP directory. This part of the file path will not be subject to MAST HLSP requirements
                        (e.g., lowercase will not be checked).

  --exclude_missions [EXCLUDE_MISSIONS ...]
                        Optional list of mission values to temporarily accept as valid values.

  --exclude_filters [EXCLUDE_FILTERS ...]
                        Optional list of filter values to temporarily accept as valid values.

  --skip_sym            If set, will ignore symbolic links

  --lowercase_dirname   If set, will change the directory names to lowercase

  --update_dirname_sign
                        If set, it will change the sign of the dir names to 'p/m'. If your hlsp has a complex folder structure, use the --root-dir option to point directly to the target name-based directories.

  --lowercase_filename     If set, will change the file names to lowercase

  -- update_filename_sign
                        If set, will change the sign of the file names to 'p/m'.
 

## Command line example:

  - simply check directory and file names and see the log
    ```
    check_file_names.py /ifs/archive/test/mast/public/hlsp/lowlib/ lowib
    ```
  - Check directory and file names and make directory names to lowercase
    ```
    python check_file_names.py --lowercase_dirname  /ifs/archive/test/mast/public/hlsp/cos-gal/ cos-gal
    ```
  - Change '+', '-' in directory name to 'p', 'm' respectively, e.g., cos-gal has another subdirectory called 'spectra' so you need to specify --rootdir down to the directory just above the target name based directories 
    
    - Changing signs in directory names or filenames requires a list of catalogs whose name was constructed with RA/DEC coordinates called "radec_named_catalogs_\[hlspname\]_dat". Create a list of the prefixes before the coordinates in the file. For instance, if the target name is "macs1201+25", only add "macs" to the list. See more examples in radec_named_catalogs.dat. 

    ```
    python check_file_names.py --root_dir /ifs/archive/test/mast/public/hlsp/cos-gal/spectra/ --update_dirname_sign /ifs/archive/test/mast/public/hlsp/cos-gal/ cos-gal
    ```
  - Change '+', '-' in filename to 'p', 'm' respectively, e.g.,
     
    ```
    python check_file_names.py --update_filename_sign /ifs/archive/test/mast/public/hlsp/test_relics/ test_relics
    ```
    - If both names of the subdirectories and the filenames need to change the signs, you need to change the subdirectory names and then the filenames after that.