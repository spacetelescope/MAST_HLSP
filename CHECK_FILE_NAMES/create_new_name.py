"""
.. module:: create_new_name
    :synopsis: checks that a given name (either dirname or filename) is one of 
                the catalogs which use RA/Dec coordinates on their target name.
                So '+' or '-'sign is detected. 
                If then, return the current name (input) and the suggested new name as a tuple.
 

.. moduleauthor:: Jinm Yoon <jyoon@stsci.edu>

"""

import logging
import re
    
    
def create_new_name(current_name, radec_named_catalogs):
    """
    you will check current_name (either directory name or filename) has a substring 
    from radec_named_catalogs list and return the name of directory and the new suggested name.
    
    : param current_name : current dirname or filename
    : type current_name : string

    : param radec_named_catalogs : list of catalogs whose names have ra/dec coordinates
    : type radec_named_catalogs : list

    """
    #print("current_name = ", current_name)
    for substring in radec_named_catalogs:
            if re.match(substring, current_name):
                newstring = re.split(substring, current_name)[1]
                #print(newstring)

                #suggest new name for either dirname or filename
                if re.search('\+', newstring) :
                    new_name = substring+newstring.replace('+','p',1) 
                    failed_name = current_name
                    logging.error("Subdirectory or file name has the positive sign, '+' : " + failed_name)
                    return failed_name, new_name
                elif re.search('-',newstring) : 
                    new_name = substring+newstring.replace('-','m',1)
                    failed_name = current_name
                    logging.error("Subdirectory or file name has the negative sign, '-' in " + failed_name)                        
                    return failed_name, new_name
                else : 
                    logging.info(current_name + "doesn't contain '-' or '+' signs! ")
