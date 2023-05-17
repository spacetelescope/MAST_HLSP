"""
.. module:: change_dirpath_sign
    :synopsis: Given a list of files, checks that the directory paths has '+' or '-'signs.
               If change_name = True, change the dirname to '-p', or  '-m'.
 

.. moduleauthor:: Jinm Yoon <jyoon@stsci.edu>

"""

import logging
import os
import re
import itertools
from create_new_name import create_new_name

#--------------

def change_dirpath_sign(idir, file_list, root_dir, hlsp_name, radec_named_catalogs, update_dirname_sign = False):   
    """
    Convert '+' and '-' signs in target-named directories (i.e., RA/Dec coordinates)
    to '-p', and '-m' respectively. 
    
    *** Note that there directories should lie just below the main hlsp folder. 
    *** If there are other subfolders between the main hlsp folder 
    *** and these targetnamed directories, use root_dir option to avoid errors since
    *** this task cannot be fully automated due to the complex nature of 
    *** each hlsp folder structure 

    :param file_list: The list of HLSP files to check.
    :type file_list: list

    :param root_dir: Optional root directory to skip when checking compliance.
    :type root_dir: str

    :param radec_named_catalogs: The list of radec_named catalogs
    :type radec_named_catalogs: list

    :param update_dirname_sign: If True, will make directory names lowercase.
    :type update_dirname_sign: Boolean

    """

    if root_dir:
        # when root_dir was offered
        unique_dirs = set([os.path.dirname(x).replace(root_dir, '').split('/')[0]
                           for x in file_list])
    else:
        unique_dirs = set([os.path.dirname(x).replace(idir, '').split('/')[0] for x in file_list])
        #print("check_dirpath_sign: ", unique_dirs)

    
    # compling dirname list to update 
    compiled_dirlist= [create_new_name(current_dir, radec_named_catalogs) for current_dir in unique_dirs]

    # list of only dirs which need updating; remove None or [] values from the list
    dirname_change_list = list(itertools.filterfalse(lambda item: not item , compiled_dirlist))

    def log(dirname, failed_dir, new_Dir):
        logging.info( "Now SIGNS in DIRNAME " + dirname+failed_dir +" SWAPED"
                        " to 'p' or 'm' : " + dirname+new_dir )
    # finally rename dirs 
    if update_dirname_sign:
        if dirname_change_list:
            for failed_dir, new_dir in dirname_change_list:
                if root_dir:
                    os.rename(root_dir+failed_dir, root_dir+new_dir)
                    log(root_dir, failed_dir, new_dir)
                else:
                    os.rename(idir+failed_dir, idir+new_dir)
                    log(idir, failed_dir, new_dir)

            
#----------------