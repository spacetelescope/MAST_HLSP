usage: check_file_names.py [-h] [--root_dir ROOT_DIR] [--exclude_missions [EXCLUDE_MISSIONS ...]] [--exclude_filters [EXCLUDE_FILTERS ...]]
                           [--skip_sym] [--lowercase_dirname] [--lowercase_filename] [--update_sign]
                           idir hlsp_name

Check that file names follow MAST HLSP convention.

positional arguments:
  idir                  [Required] Full path to the folder containing HLSP files to check.
  hlsp_name             [Required] Name of the HLSP.

optional arguments:
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
                        If set, will change the sign of the dir names to '-p/-m'If your hlsp has a complex folder structure, use --root-dir option to point directly to the targetname-based directories.
  --lowercase_filename     If set, will change the file names to lowercase
  --update_dirname_sign         If set, will change the sign of the dirnames to '-p/-m'.



command line example:

- simply checking directory and file names and see the log

check_file_names.py /ifs/archive/test/mast/public/hlsp/lowlib/ lowib

- Checking directory and file names and make directory names to lowercase

python check_file_names.py --lowercase_dirname  /ifs/archive/test/mast/public/hlsp/<hlspname>/ <hlspname>

- changing dirname '+', '-' to '-p', '-m' respectively, e.g., cos-gal has another subdirectory called 'spectra' so you need to specify --rootdir down to the directory just above the targetname directories 

python check_file_names.py --root_dir /ifs/archive/test/mast/public/hlsp/cos-gal/spectra/ --update_dirname_sign /ifs/archive/test/mast/public/hlsp/cos-gal/ cos-gal