from astropy.io import fits
import logging
import numpy
import os

#--------------------

def apply_check(this_file, template_standard):
    """
    Conducts the standard verification on the given file.

    :param this_file: The file to run standard verification on.

    :type this_file: str

    :param template_standard: The standard template to use for this file.

    :type standard: dict
    """

    # Check each extension.
    with fits.open(this_file, mode="readonly") as hdulist:
        for exten in template_standard.keys():
            if exten != 'PRODUCT' and exten != 'STANDARD':
                # Determine FITS header extension based on keyword in template.
                if exten == 'PHDU':
                    hdr_kws = list(hdulist[0].header.keys())
                # Check required keywords in the header.
                for rqkw in template_standard[exten]['required']:
                    if rqkw not in hdr_kws:
                        logging.error("File: " + this_file +
                                      ", Missing required keyword: " + rqkw)
                # Check recommended keywords in the header.
                for rckw in template_standard[exten]['recommended']:
                    if rckw not in hdr_kws:
                        logging.warning("File: " + this_file +
                                        ", Missing recommened keyword: " + rckw)

#--------------------

def apply_metadata_check(file_base_dir, endings_to_check, all_standards):
    """
    Main module that applies metadata standards to files.

    :param file_base_dir: The root directory containing HLSP files to check.

    :type file_base_dir: str

    :param endings_to_check: File endings, template types, and product types.

    :type endings_to_check: list

    :param all_standards: Set of standard templates to use.

    :type all_standards: numpy.ndarray
    """

    all_endings_to_check = numpy.asarray(
        [x['FileEnding'] for x in endings_to_check])

    # Loop over each file in the file_base_dir.
    for froot, _, file_list in os.walk(file_base_dir):
        if len(file_list) > 0:
            for this_file in file_list:
                this_ending = this_file.split('_')[-1]
                if this_ending in all_endings_to_check:
                    # Idetify the index in the list to pass template, product
                    # types to 'apply_check'.
                    where_this_ending = numpy.where(
                        all_endings_to_check == this_ending)[0]
                    if len(where_this_ending) == 1:
                        prodtype = endings_to_check[where_this_ending[0]]['FileParams']['ProductType']
                        standard = endings_to_check[where_this_ending[0]]['FileParams']['Standard']
                        # Identify which standard template to pass to.
                        all_standard_index = (
                            numpy.where(
                                (numpy.asarray(
                                    [x['PRODUCT'] == prodtype for x in all_standards]))
                                & (numpy.asarray(
                                    [x['STANDARD'] == standard for x in all_standards]))))[0]
                        if len(all_standard_index) == 1:
                            apply_check(os.path.join(froot, this_file),
                                        all_standards[all_standard_index[0]])
                        else:
                            raise ValueError("No template standard found "
                                             "for this combination of product "
                                             "type and standard: " + product +
                                             ", " + standard + ".")
                    else:
                        raise ValueError("No match or multiple match "
                                         "for this file ending inside "
                                         "'apply_metadata_check'.")

