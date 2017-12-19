"""
.. module:: hdr_verifier
    :synopsis: Given a FITS file, looks for suggested, recommended, and required
        keywords based on a template.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>,
        Dick Shaw <shaw@stsci.edu>
"""

import logging as log
import operator
import numpy as np
import yaml
from astropy.io import fits

#--------------------

EXTENSION_TYPES = ('IMAGE', 'BINTABLE')
WILDCARD_CHAR = '*'

#--------------------

class KwRecord(object):
    """
    Defines a keyword record that includes a keyword name, the expected location
        within the FITS file, and the actual location within a FITS file.
    """
    _locationTypes = ('PHDU', 'HDU')
    _need_types = ('Suggested', 'Recommended', 'Required')
    _logErrType = {'Required':'error', 'Recommended':'warning',
                   'Suggested':'info'}

    def __init__(self, kw, expected_loc, need):
        self.name = kw
        self.expected_loc = expected_loc
        self.found_loc = []
        self.need = need
        self._expected_loc = None
        self._need = None

    expected_loc = property(operator.attrgetter('_expected_loc'))

    @expected_loc.setter
    def expected_loc(self, exp_loc):
        """
        Ensure that the keyword location attribute is restricted to particular
            values when the object is instantiated.
        """
        if exp_loc not in self._locationTypes:
            raise ValueError('Location must be one of PHDU | HDU')
        self._expected_loc = exp_loc

    need = property(operator.attrgetter('_need'))

    @need.setter
    def need(self, need_type):
        """
        Ensure that the keyword necessity attribute is restricted to
            particular values when the object is instantiated.
        """
        if need_type not in self._need_types:
            raise ValueError('Need must be one of Suggested | Recommended |'
                             ' Required')
        self._need = need_type

    def kw_print_expected(self):
        """
        Prints message that a keyword of a certain type  should have been in a
            given HDU.
        """
        print('%s keyword %s expected in %s' % (self.need, self.name,
                                                self.expected_loc))

    def kw_print_found(self):
        """
        Prints a message that a keyword of a certain requirement was found in
            a given HDU.
        """
        print('%s keyword %s found in %s' % (self.need, self.name,
                                             self.found_loc))

    def kw_log_error(self, severity):
        """
        Format message for the log based on the severity of the error
            encountered.
        """
        log_err_str = '%s keyword %s not found; expected in %s' % (
            self.need, self.name, self.expected_loc)

        if severity == 'error':
            log.error(log_err_str)
        elif severity == 'warning':
            log.warning(log_err_str)
        elif severity == 'info':
            log.info(log_err_str)
        elif severity == 'debug':
            pass

    def kw_report(self):
        """
        Print results of the keyword search to the log.
        """
        log.debug('Keyword name: %s expected: %s found: %s',
                  self.name, self.expected_loc, self.found_loc)
        if self.expected_loc in self.found_loc:
            log.info('%s keyword %s found in %s',
                     self.need, self.name, self.found_loc)
        elif len(self.found_loc) < 1:
            # Keyword not found
            self.kw_log_error(self._logErrType[self.need])
        else:
            # Keyword in header, but not in expected location:
            log.info('%s keyword %s found in %s; expected in %s',
                     self.need, self.name, self.found_loc, self.expected_loc)

#--------------------

class HlspKw(object):
    """
    A collection of HLSP keywords expected, created from an input template.
    """
    def __init__(self, kw_file, n_axes):
        """
        HLSP keyword list is created from an input YAML file.
            Indexed keywords are expanded based on the number of axes in the
            data array.
        """
        self.kw_list = []
        with open(kw_file, 'r') as yaml_file:
            kw_data = yaml.load(yaml_file)

        for loc in kw_data:
            for need, kw_names in kw_data[loc].iteritems():
                kw_full_list = []
                for kword in kw_names:
                    kw_full_list += self.expand_kw(kword, n_axes)
                self.kw_list += [KwRecord(k_word, loc, need.capitalize())
                                 for k_word in kw_full_list]

    def expand_kw(self, kword, n_axes):
        """
        Expand indexed keywords based on the number of axes in the data
            array. Indexes appear as a wildcard in the spelling of the name.
        """
        wild_ch = WILDCARD_CHAR
        count = kword.count(wild_ch)
        if count < 1:
            return [kword]
        elif count == 1:
            return [kword.replace(wild_ch, str(j+1), 1) for j in np.arange(
                n_axes)]
        tmp = [kword.replace(wild_ch, str(j+1), 1) for j in np.arange(
            n_axes)]
        kw_list = []
        for k in tmp:
            kw_list += [k.replace(wild_ch, str(j+1), 1) for j in np.arange(
                n_axes)]
        return kw_list

    def hlsp_report(self):
        """
        Report results for each keyword in the list.
        """
        for k_word in self.kw_list:
            k_word.kw_report()

#--------------------

def hlsp_kw_inspector(hdr, hd_loc, kw_ref):
    """
    Check for existance of keyword records in HDUs, and write the results
        to the log.
    """

    for k_word in kw_ref.kw_list:
        try:
            val = hdr[k_word.name]
            # Keyword found in expected location
            log.debug('Found keyword %s in %s', k_word.name, hd_loc)
            k_word.found_loc.append(hd_loc)

        # Keyword not found
        except KeyError:
            log.debug('%s keyword %s is missing from %s',
                      k_word.need, k_word.name, hd_loc)

#--------------------

def is_sci_extension(hdr, ext_type, ext_name):
    """
    Determine if a FITS extension is of the desired type and name.
    """

    if (hdr['xtension'] == ext_type) and (ext_name == hdr['EXTNAME']):
        return True
    elif (hdr['xtension'] == ext_type) and ext_name == '':
        return True
    return False

#--------------------

def hdr_hlsp(infile, kwfile, extension, extname, log_level):
    """
    Verify that MEF headers of a FITS file contain keywords specified in
       a user-supplied YAML file.
    """

    # Fire up the logger.
    log.basicConfig(format='%(levelname)s:%(message)s', level=log_level.upper())

    print('** Validating: %s using %s' % (infile, kwfile))
    with fits.open(infile) as hdu_list:
        phd = hdu_list[0].header
        if extension == 'None':
            # Simple FITS file, no extensions
            if len(hdu_list) > 1:
                log.warning('Turning off HDU validation')
            else:
                n_axes = phd['NAXIS']
                hdr = None
                if n_axes == 0:
                    raise RuntimeError('Primary header contains no pixel data')

        else:
            hdr = [h.header for h in hdu_list[1:] if is_sci_extension(
                h.header, extension, extname)]
            if len(hdr) < 1:
                log.error('No valid HDU extensions of type: %s',
                          Content['extension'])
                raise RuntimeError('Failed to find HDU extensions')
            else:
                # Assume all science extensions have the same dimensions
                n_axes = hdr[0]['NAXIS']

    # Fetch keywords to verify
    kw_ref = HlspKw(kwfile, n_axes)

    # Check for keyword records in relevant headers; report if not found
    hlsp_kw_inspector(phd, 'PHDU', kw_ref)
    if hdr is not None:
        # Check just the first science extension for now
        hlsp_kw_inspector(hdr[0], 'HDU', kw_ref)

    kw_ref.hlsp_report()

#--------------------
