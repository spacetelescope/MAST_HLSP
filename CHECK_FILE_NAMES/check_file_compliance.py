"""
.. module:: check_file_compliance
    :synopsis: Given a list of files, checks that they satisfy MAST HLSP
        requirements.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
.. moduleeditor:: Jinm Yoon <jyoon@stsci.edu>
"""

import logging
import os

from check_in_known_missions import check_in_known_missions
from check_in_known_filters import check_in_known_filters
from check_is_version_string import check_is_version_string
from check_has_plus_sign import check_has_plus_sign
from create_new_name import create_new_name

# --------------------


def check_file_compliance(file_list, hlsp_name, known_missions, known_filters, radec_named_catalogs,
                          exclude_missions, exclude_filters, lowercase_filename = False, 
                          update_filename_sign =False):
    """
    Checks if file names satisfy MAST HLSP requirements.

    :param file_list: The list of HLSP files to check.
    :type file_list: list

    :param hlsp_name: The name of the HLSP.
    :type hlsp_name: str

    :param known_missions: The list of known values for the "mission" part of
        file names.
    :type known_missions: set

    :param known_filters: The list of known values for the "filter" part of
        file names.
    :type known_filters: set

    :param radec_named_catalogs: The list of radec named catalogs for checking the "targetname" 
        part of filenames
    :type radec_named_catalogs: set

    :param exclude_missions: Optional list of values for the "mission" part of
        the file names that will be temporarily accepted (for this run only).
    :type exclude_missions: list

    :param exclude_filters: Optional list of values for the "filter" part of
        the file names that will be temporarily accepted (for this run only).
    :type exclude_filters: list

    :param lowercase_filename: If True, will make the file names lowercase.
    :type lowercase_filename: Boolean

    :param update_filename_sign : if True, will change the sign '+' or '-' 
                         in coordinated filenames to '-p' or '-m' respectively.
    :type update_filename_sign : Boolean


   """

    # Creating a function to check if a string has unallowed characters. 
    

    # This controls how many "fields" (strings separated by an underscore) are
    # expected.
    n_fields_expected = 8

    for ifile in file_list:
        ifile_base = os.path.basename(ifile)
        # # print("\n filename: ", ifile_base)

        # Check that the file name is all lowercase. 
        # If lowercase_filename = True, it will change to lowercases.
        if not ifile_base.islower():
            logging.error("File is not all lowercase: " + ifile)
            if lowercase_filename:
                os.rename(ifile, ifile.lower())
                logging.info( "Now CHANGE to LOWERCASE FILENAME: " + ifile +" changed to lowercase letters: " 
                        + ifile.lower() )


        # Check that this file has the corret number of fields.
        splits = ifile_base.split('_')

        if len(splits) != n_fields_expected:
            logging.error("File does not have " + str(n_fields_expected) +
                            " parts: " + ifile)
        else:
            # Check the first field is "hlsp"
            if splits[0] != "hlsp":
                logging.warning('Field 1 is not "hlsp": ' + ifile)

            # Check that the second field matches the HLSP name.
            if splits[1] != hlsp_name:
                logging.warning('Field 2 is not "' + hlsp_name + '": ' + ifile)

            # Check that the third field is in the list of known missions.
            # Field 3 is "observatory", which is mission names or telescope names
            if not check_in_known_missions(splits[2], known_missions,
                                           exclude_missions):
                logging.warning('Field 3 ("' + splits[2] + '") is not in list '
                                'of known missions: ' + ifile)

            # The fourth field is the instrument part, but can also include other
            # data like "resolution", etc.  No specific checks for this.

            # The fifth field is the target name part, and is by definition very
            # free-form.  However, '+' sign is not allowed. if any coordinate based 
            # targetname includes '+/-' signs, we need to change it to'-p/-m'.

            if check_has_plus_sign(splits[4]):
                logging.error('Field 5 does not appear to be a valid filename'
                                ' string: "+" sign ' + ifile) 
            if update_filename_sign:
                new_targetname = create_new_name(splits[4], radec_named_catalogs)

                if new_targetname !=None:
                    new_filename = ifile.replace(splits[4], new_targetname[1])    
                    os.rename(ifile, new_filename)
                    logging.info( "Now SIGNS in FILENAME " + ifile +" SWAPED"
                                    " to '-p' or '-m' : " + new_filename )
                     
            # Check that the sixth field is in the list of known filters.
            if not check_in_known_filters(splits[5], known_filters,
                                          exclude_filters):
                logging.warning('Field 6 ("' + splits[5] + '") is not in list '
                                'of known filters: ' + ifile)

            # Check that the seventh field looks like a version number.
            if not check_is_version_string(splits[6]):
                logging.warning('Field 7 does not appear to be a valid version'
                                ' string: ' + ifile)

            # The eighth field is a product and extension piece.  This is fairly
            # free-form, but generally must be <x>.<y>.  An exception is if a
            # file is gzipped, in which case the format is <x>.<y>.gz.
            prod_ext_str = splits[7]
            if splits[7][-3:] == '.gz':
                prod_ext_str = prod_ext_str.strip('.gz')
            product_extension_splits = prod_ext_str.split('.')
            if len(product_extension_splits) < 2:
                logging.warning('Field 8 does not have <product>.<extension> '
                                'format: ' + ifile)

# --------------------
