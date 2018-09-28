"""
.. module:: apply_metadata_check
    :synopsis: Applies the check of header keywords and values given a standard.

().. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import logging
import os
from astropy.io import fits
import numpy

from get_filetypes_keys import get_filetypes_keys

# --------------------


def write_log(fname, logstring, logtype, log_message_counts):
    """
    Writes a logging string in a formatted way.

    :param fname: The name of the file.

    :type fname: str

    :param logstring: The string to log.

    :type logstring: str

    :param logtype: The type of message to log.

    :type logtype: str

    :param log_message_counts: Keeps track of the number of times a message is
        logged.

    :type log_message_counts: dict
    """

    if logtype == 'error':
        logging.error('File: {0}'.format(fname) +
                      '; ' + logstring)
    elif logtype == 'warning':
        logging.warning('File: {0}'.format(fname) +
                        '; ' + logstring)
    elif logtype == "info":
        logging.info('File: {0}'.format(fname) +
                     '; ' + logstring)
    else:
        raise ValueError("Type of log message not understood, passed a" +
                         " value of " + logtype + ".")

    # Update log message counts.
    if logstring not in log_message_counts.keys():
        log_message_counts[logstring] = {'count': 1, 'type': logtype}
    else:
        log_message_counts[logstring]['count'] = (
            log_message_counts[logstring]['count'] + 1)

# --------------------


def validate_date(datevals, this_file, log_message_counts):
    """
    Given an list of dates in [YYYY, MM, DD] order, checks to make sure they
        are valid date values.

    :param datevals: The list of date values.

    :type datevals: list

    :param this_file: Name of file being checked.

    :type this_file: str

    :param log_message_counts: Keeps track of the number of times a message is
        logged.

    :type log_message_counts: dict
    """

    if len(datevals[0]) != 4:
        logstring = ('first part of "DATE-OBS" does not look like a 4-digit' +
                     ' year.')
        write_log(this_file, logstring, 'error', log_message_counts)

    if len(datevals[1]) != 2 or int(datevals[1]) < 1 or int(datevals[1]) > 12:
        logstring = ('second part of "DATE-OBS" does not look like a' +
                     ' 2-digit month.')
        write_log(this_file, logstring, 'error', log_message_counts)
    if len(datevals[2]) != 2 or int(datevals[2]) < 1 or int(datevals[2]) > 31:
        logstring = ('third part of "DATE-OBS" does not look like a 2-digit' +
                     ' day.')
        write_log(this_file, logstring, 'error', log_message_counts)

# --------------------


def validate_time(timevals, this_file, log_message_counts):
    """
    Given an list of times in [hh, mm, ss.ss] order, checks to make sure they
        are valid time values.

    :param timevals: The list of date values.

    :type timevals: list

    :param this_file: Name of file being checked.

    :type this_file: str

    :param log_message_counts: Keeps track of the number of times a message is
        logged.

    :type log_message_counts: dict
    """

    if len(timevals) != 3:
        logstring = 'keyword "TIME-OBS" is not in a "hh:mm:ss.ss" format.'
        write_log(this_file, logstring, 'error', log_message_counts)
    else:
        if (len(timevals[0]) != 2 or int(timevals[0]) < 0 or
                int(timevals[0]) > 24):
            logstring = ('first part of "TIME-OBS" does not look like' +
                         ' a 2-digit hour.')
            write_log(this_file, logstring, 'error', log_message_counts)
        if (len(timevals[1]) != 2 or int(timevals[1]) < 0 or
                int(timevals[1]) > 60):
            logstring = ('second part of "TIME-OBS" does not look like' +
                         ' a 2-digit minute.')
            write_log(this_file, logstring, 'error', log_message_counts)
        # If there's a 'z' sticking around at the end of the string, strip it
        # before comparing values.
        seconds_val = timevals[2]
        if timevals[2][-1].lower() == 'z':
            seconds_val = timevals[2][0:-1]
        if (float(seconds_val) < 0. or float(seconds_val) > 60.):
            logstring = ('third part of "TIME-OBS" does not look like a valid' +
                         ' seconds field.')
            write_log(this_file, logstring, 'error', log_message_counts)

# --------------------


def check_date_obs(header, this_file, log_message_counts):
    """
    Checks that the DATE-OBS keyword is in the correct format, or if not
        that the TIME-OBS keyword is also supplied.

    :param header: The header with the DATE-OBS string to check.

    :type header: astropy.io.fits.header.Header

    :param this_file: Name of file being checked.

    :type this_file: str

    :param log_message_counts: Keeps track of the number of times a message is
        logged.

    :type log_message_counts: dict
    """
    date_obs_str = header['DATE-OBS'].strip()

    # Format should be YYYY-MM-DDThh:mm:ss.ss
    # Check first if the DATE-OBS is only the date,
    # (which would be YYYY-MM-DD).
    if len(date_obs_str.split('-')) == 3 and 'T' not in date_obs_str:
        # Then the first must be 4 digits, the next two 2 digits,
        # and the TIME-OBS keyword must be present in hh:mm:ss.ss format.
        dsplits = date_obs_str.split('-')
        validate_date(dsplits, this_file, log_message_counts)
        if 'TIME-OBS' not in header.keys():
            logstring = ('header contains the' +
                         ' "DATE-OBS" keyword with only the date information,' +
                         ' but does not include the "TIME-OBS keyword" with' +
                         'the time information.')
            write_log(this_file, logstring, 'error', log_message_counts)
        else:
            # No 'z' or 'Z' for "zulu" time zone allowed.
            if header['TIME-OBS'].strip()[-1].lower() == 'z':
                logstring = ('"z" or "Z" for "zulu" is not allowed in' +
                             ' time string.')
                write_log(this_file, logstring, 'error', log_message_counts)
            tsplits = header['TIME-OBS'].strip().split(':')
            validate_time(tsplits, this_file, log_message_counts)
    elif 'T' in date_obs_str and len(date_obs_str) >= 19:
        # No 'z' or 'Z' for "zulu" time zone allowed.
        if date_obs_str[-1].lower() == 'z':
            logstring = ('"z" or "Z" for "zulu" is not allowed in' +
                         ' "DATE-OBS" string.')
            write_log(this_file, logstring, 'error', log_message_counts)
        datetimesplits = date_obs_str.split('T')
        datesplits = datetimesplits[0].split('-')
        timesplits = datetimesplits[1].split(':')
        validate_date(datesplits, this_file, log_message_counts)
        validate_time(timesplits, this_file, log_message_counts)
    else:
        logstring = ('keyword "DATE-OBS" is in the header' +
                     ' but is not in either a "YYYY-MM-DD" or' +
                     ' "YYYY-MM-DDThh:mm:ss.ss" format.')
        write_log(this_file, logstring, 'error', log_message_counts)

# --------------------


def apply_check(this_file, template_standard, hdulist, log_message_counts):
    """
    Conducts the standard verification on the given file.

    :param this_file: The file to run standard verification on.

    :type this_file: str

    :param template_standard: The standard template to use for this file.

    :type standard: lib.FitsKeyword.FitsKeywordList

    :param hdulist: The HDUList of the file to check.

    :type hdulist: astropy.io.fits.hdu.hdulist.HDUList

    :param log_message_counts: Keeps track of the number of times a message is
        logged.

    :type log_message_counts: dict
    """
    # Check each extension.
    for kw in template_standard.keywords:
        if kw.header >= 0:
            kw_checked = kw.fits_keyword
            is_in_hdr = kw_checked.upper() in hdulist[kw.header].header.keys()
            # If this keyword is missing from the header, try the alternate
            # keyword(s) instead, if one exists.
            # The alternates are stored as a comma-separated string.
            if not is_in_hdr:
                if kw.alternates:
                    for kwa in kw.alternates:
                        kw_checked = kwa
                        is_in_hdr = kw_checked.upper() in (
                            hdulist[kw.header].header.keys())
                        if is_in_hdr:
                            break
        else:
            # ---------------------------------
            # If header is negative value need to make sure a default is
            # specified here if CAOM is required/recommended ....
            # ---------------------------------
            # Define the is_in_hdr variable to 'None' since we haven't checked.
            is_in_hdr = 'None'
            kw_checked = kw.fits_keyword
            if kw.default == 'None':
                kw_checked = 'None'
                if kw.caom_status == 'required':
                    logstring = ("Missing CAOM required" +
                                 " keyword: {0}".format(kw.fits_keyword) +
                                 ', and no default value is' +
                                 ' specififed.')
                    write_log(this_file, logstring, 'error',
                              log_message_counts)
                elif kw.caom_status == 'recommended':
                    logstring = ("Missing CAOM recommended" +
                                 " keyword: {0}".format(kw.fits_keyword) +
                                 ', and no default value is' +
                                 ' specififed.')
                    write_log(this_file, logstring, 'warning',
                              log_message_counts)
            # This scenario is an HLSP requirement error regardless, since
            # even if a default is provided, it's not in the file headers.
            if kw.hlsp_status == 'required':
                logstring = ("Missing HLSP required" +
                             " keyword: {0}".format(kw.fits_keyword) +
                             ', and no default value is' +
                             ' specififed.')
                write_log(this_file, logstring, 'error',
                          log_message_counts)
            elif kw.hlsp_status == 'recommended':
                logstring = ("Missing HLSP recommended" +
                             " keyword: {0}".format(kw.fits_keyword) +
                             ', and no default value is' +
                             ' specififed.')
                write_log(this_file, logstring, 'warning',
                          log_message_counts)
        if (not is_in_hdr and is_in_hdr != 'None') and kw_checked != 'None':
            # Check required/recommended HLSP keywords.
            if kw.hlsp_status == "required":
                logstring = ("Missing HLSP required keyword: " +
                             '"{0}".'.format(kw_checked))
                write_log(this_file, logstring, 'error', log_message_counts)
            elif kw.hlsp_status == "recommended":
                logstring = ("Missing HLSP recommened keyword: " +
                             '"{0}".'.format(kw_checked))
                write_log(this_file, logstring, 'warning',
                          log_message_counts)
            # Check required/recommended CAOM keywords.
            if kw.caom_status == "required":
                logstring = ("Missing CAOM required keyword: " +
                             '"{0}".'.format(kw_checked))
                write_log(this_file, logstring, 'error', log_message_counts)
                # If a required CAOM keyword is missing, but a default
                # value is present, inform the user a fallback default
                # is being used.
                if kw.default != 'None':
                    logstring = ("Using default" +
                                 ' value of "{0}"'.format(str(kw.default)) +
                                 " for CAOM required " +
                                 'keyword "{0}".'.format(kw_checked))
                    write_log(this_file, logstring, 'info',
                              log_message_counts)
            elif kw.caom_status == "recommended":
                logstring = ("Missing CAOM recommended keyword: " +
                             '"{0}".'.format(kw_checked))
                write_log(this_file, logstring, 'warning',
                          log_message_counts)
                # If a recommended CAOM keyword is missing, but a default
                # value is present, inform the user a fallback default
                # is being used.
                if kw.default != 'None':
                    logstring = ('Using default value' +
                                 ' of "{0}"'.format(str(kw.default)) +
                                 ' for CAOM recommended ' +
                                 'keyword "{0}".'.format(kw_checked))
                    write_log(this_file, logstring, 'info',
                              log_message_counts)
        # Now do some sanity checking of keywords if present.
        if is_in_hdr and kw_checked != 'None':
            if kw_checked == "DATE-OBS":
                # Check DATE-OBS keyword is correct format, if not,
                # try TIME-OBS.
                check_date_obs(hdulist[kw.header].header, this_file,
                               log_message_counts)
            if kw.multiple:
                # Check if this keyword is set to 'MULTI' properly.
                kw_value_checked = hdulist[kw.header].header[kw_checked]
                if kw_value_checked.lower() == "multi":
                    # Make sure there are other keywords of the format
                    # KW[0:6]nn.  There should be at least two of them.
                    if (kw_checked[0:6]+'01' not in
                            hdulist[kw.header].header.keys() or
                            kw_checked[0:6]+'02' not in
                            hdulist[kw.header].header.keys()):
                        logstring = ('Keyword "{0}"'.format(kw_checked) +
                                     ' is set to "MULTI" but does not' +
                                     ' have at least two of keyword' +
                                     ' {0}nn.'.format(kw_checked[0:6]))
                        write_log(this_file, logstring, 'error',
                                  log_message_counts)
                elif kw_value_checked.lower() == "multiple":
                    logstring = ('Keyword "{0}"'.format(kw_checked) +
                                 ' is set to "MULTIPLE" but should be' +
                                 ' set to "MULTI".')
                    write_log(this_file, logstring, 'error',
                              log_message_counts)

# --------------------


def apply_metadata_check(file_base_dir, endings_to_check, all_standards):
    """
    Main module that applies metadata standards to files.

    :param file_base_dir: The root directory containing HLSP files to check.

    :type file_base_dir: str

    :param endings_to_check: File endings, template types, and product types.

    :type endings_to_check: list

    :param all_standards: Set of standard templates to use.

    :type all_standards: numpy.ndarray

    :returns: dict -- A count of the messages being logged.
    """

    all_endings_to_check = numpy.asarray(get_filetypes_keys(endings_to_check))

    # This dict will store all the messages logged, and count how many times
    # that message is logged.
    log_message_counts = {}

    # Loop over each file in the file_base_dir.
    for froot, _, file_list in os.walk(file_base_dir):
        if file_list:
            for this_file in file_list:
                this_ending = this_file.split('_')[-1]
                if this_ending in all_endings_to_check:
                    # Idetify the index in the list to pass template, product
                    # types to 'apply_check'.
                    where_this_ending = numpy.where(
                        all_endings_to_check == this_ending)[0]
                    if len(where_this_ending) == 1:
                        ending_params = endings_to_check[where_this_ending[0]]
                        prodtype = ending_params[this_ending]['ProductType']
                        standard = ending_params[this_ending]['Standard']
                        # Identify which standard template to pass.
                        all_standard_index = [i for i, x in enumerate(
                            all_standards) if (
                                x.product_type == prodtype and
                                x.standard_type == standard)]
                        if len(all_standard_index) == 1:
                            fitsfile = os.path.join(froot, this_file)
                            with fits.open(fitsfile, mode="readonly") as hdulist:
                                apply_check(fitsfile,
                                            all_standards[all_standard_index[0]],
                                            hdulist, log_message_counts)
                        else:
                            raise ValueError("No template standard found "
                                             "for this combination of product "
                                             "type and standard: " + prodtype +
                                             ", " + standard + ".")
                    else:
                        raise ValueError("No match or multiple match "
                                         "for this file ending inside "
                                         "'apply_metadata_check'.")
    return log_message_counts
