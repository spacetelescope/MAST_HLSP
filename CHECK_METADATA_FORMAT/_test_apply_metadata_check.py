"""
.. module:: _test_apply_metadata_check.py

   :synopsis: Test module for apply_metadata_check modules.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import io
import itertools
import logging
import sys
import unittest
from astropy.io import fits
from apply_metadata_check import validate_date, validate_time, check_date_obs
from apply_metadata_check import apply_check

sys.path.append("../")
from lib import FitsKeyword

LOGGER = logging.getLogger()

# --------------------
# @unittest.skip('Skip TestValidateDate')


class TestValidateDate(unittest.TestCase):
    """
    Test class for the validate_date() method.
    """
    good_date = ['2018', '04', '16']
    bad_date_yr = ['18', '04', '16']
    bad_date_mn = ['2018', '4', '16']
    bad_date_mn2 = ['2018', '16', '04']
    bad_date_da = ['2018', '04', '4']
    bad_date_da2 = ['2018', '04', '32']

    def test_good_date(self):
        """
        Test of a valid date.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ''
        validate_date(self.good_date, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_date_year(self):
        """
        Test of a bad date due to the year not being 4-digits.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; first part of "DATE-OBS" does not look like' +
                        ' a 4-digit year.')
        validate_date(self.bad_date_yr, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_date_month(self):
        """
        Test of a bad date due to the month not being 2-digits.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; second part of "DATE-OBS" does not look like' +
                        ' a 2-digit month.')
        validate_date(self.bad_date_mn, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_date_month2(self):
        """
        Test of a bad date due to the month not being 0 < month < 13, often
            due to the day and month being swapped in order.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; second part of "DATE-OBS" does not look like' +
                        ' a 2-digit month.')
        validate_date(self.bad_date_mn2, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_date_day(self):
        """
        Test of a bad date due to the day not being 2-digits.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; third part of "DATE-OBS" does not look like' +
                        ' a 2-digit day.')
        validate_date(self.bad_date_da, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_date_day2(self):
        """
        Test of a bad date due to the day not being 0 <= day <= 31.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; third part of "DATE-OBS" does not look like' +
                        ' a 2-digit day.')
        validate_date(self.bad_date_da2, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

# --------------------
# @unittest.skip('Skip TestValidateTime')


class TestValidateTime(unittest.TestCase):
    """
    Test class for the validate_time() method.
    """
    good_time = ['01', '11', '11.11']
    good_time2 = ['01', '11', '11.11Z']
    bad_time = ['01', '01']
    bad_time_hr = ['0', '11', '11']
    bad_time_hr2 = ['25', '11', '11']
    bad_time_mi = ['01', '1', '11']
    bad_time_mi2 = ['01', '61', '11']
    bad_time_se = ['01', '01', '61.1']
    bad_time_se2 = ['01', '01', '61.1Z']

    def test_good_time(self):
        """
        Test of a valid time.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ''
        validate_time(self.good_time, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_good_time2(self):
        """
        Test of a valid time that includes a 'z' at the end, which should be
            ignored.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ''
        validate_time(self.good_time2, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_time(self):
        """
        Test of a bad time that doesn't have three components.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; keyword "TIME-OBS" is not in a "hh:mm:ss.ss"' +

                        ' format.')
        validate_time(self.bad_time, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_time_hour(self):
        """
        Test of a bad time because the hours value is only a single-digit.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; first part of "TIME-OBS" does not look like' +

                        ' a 2-digit hour.')
        validate_time(self.bad_time_hr, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_time_hour2(self):
        """
        Test of a bad time because the hours value is not >= 0 and <= 24.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; first part of "TIME-OBS" does not look like' +

                        ' a 2-digit hour.')
        validate_time(self.bad_time_hr2, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_time_minute(self):
        """
        Test of a bad time because the minutes value is only a single digit.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; second part of "TIME-OBS" does not look like' +

                        ' a 2-digit minute.')
        validate_time(self.bad_time_mi, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_time_minute2(self):
        """
        Test of a bad time because the minutes value is not >= 0 and <= 60.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; second part of "TIME-OBS" does not look like' +

                        ' a 2-digit minute.')
        validate_time(self.bad_time_mi2, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_time_second(self):
        """
        Test of a bad time because the seconds value is not >= 0 and <= 60.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; third part of "TIME-OBS" does not look like' +

                        ' a valid seconds field.')
        validate_time(self.bad_time_se, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_time_second2(self):
        """
        Test of a bad time because the seconds value is not >= 0 and <= 60, but
            does contain a 'z' at the end, which should be ignored.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; third part of "TIME-OBS" does not look like' +

                        ' a valid seconds field.')
        validate_time(self.bad_time_se2, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

# --------------------
# @unittest.skip('Skip TestCheckDateObs')


class TestCheckDateObs(unittest.TestCase):
    """
    Test class for the check_date_obs() method.
    """
    # Define some basic date and time for use later.
    good_date = '2016-08-13'
    good_time = '01:22:34.56'
    bad_time_z = '01:22:34.56Z'
    short_time = '01:22'

    # This tests a good, full DATE-OBS
    good_dateobs_full = fits.PrimaryHDU()
    good_dateobs_full.header.set('DATE-OBS', good_date + 'T' + good_time)

    # This tests a bad, full DATE-OBS due to presence of a 'z' at the end
    bad_dateobs_full = fits.PrimaryHDU()
    bad_dateobs_full.header.set('DATE-OBS', good_date + 'T' + bad_time_z)

    # This tests a bad, full DATE-OBS due to not being at least 19 characters
    bad_dateobs_short = fits.PrimaryHDU()
    bad_dateobs_short.header.set('DATE-OBS', good_date + 'T' + short_time)

    # This tests a good DATE-OBS that also has a good TIME-OBS
    good_dateobs_timeobs = fits.PrimaryHDU()
    good_dateobs_timeobs.header.set('DATE-OBS', good_date)
    good_dateobs_timeobs.header.set('TIME-OBS', good_time)

    # This tests a good DATE-OBS that is missing a TIME-OBS
    bad_dateobs_timeobs = fits.PrimaryHDU()
    bad_dateobs_timeobs.header.set('DATE-OBS', good_date)

    # This tests a good DATE-OBS that has a bad TIME-OBS
    bad_dateobs_timeobs_z = fits.PrimaryHDU()
    bad_dateobs_timeobs_z.header.set('DATE-OBS', good_date)
    bad_dateobs_timeobs_z.header.set('TIME-OBS', bad_time_z)

    def test_good_full_date_obs(self):
        """
        Test of a valid, full DATE-OBS.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ''
        check_date_obs(self.good_dateobs_full.header, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_full_date_obs_z(self):
        """
        Test of a bad, full DATE-OBS due to a 'z' at the end of it.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; "z" or "Z" for "zulu" is not allowed in' +
                        ' "DATE-OBS" string.')
        check_date_obs(self.bad_dateobs_full.header, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_full_date_obs_short(self):
        """
        Test of a bad, full DATE-OBS due to it being shorter than expected.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; keyword "DATE-OBS" is in the header' +
                        ' but is not in either a "YYYY-MM-DD" or' +
                        ' "YYYY-MM-DDThh:mm:ss.ss" format.')
        check_date_obs(self.bad_dateobs_short.header, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_good_date_obs_time_obs(self):
        """
        Test of a valid DATE-OBS that also has a valid TIME-OBS.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ''
        check_date_obs(self.good_dateobs_timeobs.header, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_date_obs_time_obs(self):
        """
        Test of a valid DATE-OBS that should have a TIME-OBS keyword but doesn't.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; header contains the' +
                        ' "DATE-OBS" keyword with only the date information,' +
                        ' but does not include the "TIME-OBS keyword" with' +
                        'the time information.')
        check_date_obs(self.bad_dateobs_timeobs.header, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

    def test_bad_date_obs_time_obs_z(self):
        """
        Test of a valid DATE-OBS that has a bad TIME-OBS due to a 'z' at the end.
        """
        sys.stdout = io.StringIO()
        stream_handler = logging.StreamHandler(sys.stdout)
        LOGGER.addHandler(stream_handler)
        expected_str = ('File: ; "z" or "Z" for "zulu" is not allowed in' +
                        ' time string.')
        check_date_obs(self.bad_dateobs_timeobs_z.header, '', {})
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, expected_str)
        LOGGER.removeHandler(stream_handler)

# --------------------
# @unittest.skip('Skip TestApplyCheck')


class TestApplyCheck(unittest.TestCase):
    """
    Test class for the apply_check() method.
      There are multiple combinations tested, which inolve combinations of:
      - required, recommened
      - in header, missing in header
      - no alternate, with alternate
      - no default, with default
      - header < 0, header >= 0
      - hlsp, caom (for required/recommended)
    """
    simulated_fits_file = '_test_apply_check.fits'
    primary_keyword = 'PRIHDRKY'
    alternate_keyword = 'ALTHDRKY'
    hlsp_status_vals = ["required", "recommended"]
    caom_status_vals = ["required", "recommended"]
    # This defines whether the primary keyword is in the header or not.
    pri_in_header_vals = [True, False]
    # This defines whether the alternate keyword is in the header or not.
    alt_in_header_vals = [True, False]
    # This sets up an alternate keyword to check for, or none.
    alternate_vals = [[], [alternate_keyword]]
    # This sets up a default value to fall back to, or none.
    default_vals = ['None', 'Kepler']
    # This determines whether a valid header extension is there to check, or not.
    exten_vals = [-999, 1]

    def make_template(self, trial_params):
        """
        Creates a trial template to use based on a combination of parameters.

        :param trial_params: The combination of parameters to use.

        :type trial_params: dict

        returns: lib.FitsKeyword.FitsKeywordList -- the simulated template based
            on these parameters
        """

        return_template = {self.primary_keyword: {
            'header': trial_params['exten_val'],
            'hlsp_status': trial_params['hlsp_stat'],
            'caom_status': trial_params['caom_stat'],
            'caom_keyword': 'instrument_keywords',
            'xml_parent': 'metadataList',
            'multiple': False}}
        if trial_params['alt_val']:
            return_template[self.primary_keyword]['alternates'] = (
                trial_params['alt_val'])
        if trial_params['def_val']:
            return_template[self.primary_keyword]['default'] = (
                trial_params['def_val'])
        return FitsKeyword.FitsKeywordList('timeseries', 'k2', return_template)

    def get_expected_str_len(self, trial_params):
        """
        Generates the expected string length given the parameter set.  If no
            errors, then expect a zero-length string from STDOUT.

        :param trial_params: The combination of parameters to use.

        :type trial_params: dict

        returns: int -- the expected string length to see in STDOUT
        """
        # Assume a zero length string, make this non-zero for any parameter
        # combination that would result in a failure.  Any non-zero length
        # counts as an error message in the unit test when checking (check is
        # zero or not).
        expected_str_len = 0
        # Everything fails HLSP requirements if the extension is less than 0 for
        # the keyword.
        if trial_params['exten_val'] < 0:
            expected_str_len = 1
        # If the primary keyword is missing, and the alternate keyword is
        # missing, and there is no default, it's a fail.
        if (not trial_params['pri_in_hdr'] and
                not trial_params['alt_in_hdr'] and
                trial_params['def_val'] == 'None'):
            expected_str_len = 1
        # If the primary keyword is missing, the alternate is supposed to be
        # there but no actual alternate value was given, and there is no default
        # to fall back to, that's a fail.
        if (not trial_params['pri_in_hdr'] and
                trial_params['alt_in_hdr'] and not
                trial_params['alt_val'] and
                trial_params['def_val'] == 'None'):
            expected_str_len = 1
        # For an HLSP required/recommended keyword, if the primary is missing,
        # and the alternate is missing or not given, but there is a default, it
        # is still a failure since the default satisfies the CAOM requirement but
        # not the HLSP requirement.
        if ((trial_params['hlsp_stat'] == 'required' or
             trial_params['hlsp_stat'] == 'recommended') and
                not trial_params['pri_in_hdr'] and
                (not trial_params['alt_in_hdr'] or
                 (trial_params['alt_in_hdr'] and not
                  trial_params['alt_val'])) and
                trial_params['def_val'] != 'None'):
            expected_str_len = 1
        return expected_str_len

    def make_header(self, trial_params):
        """
        Creates a trial header to use based on a combination of parameters.

        :param trial_params: The combination of parameters to use.

        :type trial_params: dict

        returns: astropy.io.fits.hdu.hdulist.HDUList -- the simulated header
            based on these parameters
        """
        return_header_list = [fits.PrimaryHDU()]
        # If the extension is >=0 add the primary/alt header if it's expected.
        if trial_params['exten_val'] >= 0:
            # Add extension headers to the HDUList if needed.
            if trial_params['exten_val'] > 0:
                for i in range(1, trial_params['exten_val'] + 1):
                    return_header_list.append(fits.ImageHDU())
            # Create the HDUList object.
            hdu = fits.HDUList(return_header_list)
            if trial_params['pri_in_hdr']:
                hdu[trial_params['exten_val']].header.set(
                    self.primary_keyword, 4., 'A primary keyword.')
            if (trial_params['alt_in_hdr'] and
                    trial_params['alt_val']):
                hdu[trial_params['exten_val']].header.set(
                    trial_params['alt_val'][0], 4., 'An alternate keyword.')
        else:
            # There there is no need to add anything to the header, since
            # we are not checking it anyways, so just return an empty header.
            hdu = fits.HDUList(return_header_list)
        return hdu

    # This loops over every combination of the above options, sets up a template
    # and constructs a header to test, and tests the output.
    def test_apply_check(self):
        """
        Tests the logic behind header checking based on combaintions of
          template parameters.
        """
        for combo in itertools.product(*[self.hlsp_status_vals,
                                         self.caom_status_vals,
                                         self.pri_in_header_vals,
                                         self.alt_in_header_vals,
                                         self.alternate_vals,
                                         self.default_vals, self.exten_vals]):
            trial_params = {'hlsp_stat': combo[0],
                            'caom_stat': combo[1],
                            'pri_in_hdr': combo[2],
                            'alt_in_hdr': combo[3],
                            'alt_val': combo[4],
                            'def_val': combo[5],
                            'exten_val': combo[6]}
            with self.subTest(trial_params=trial_params):
                # Construct the template to pass to apply_check().
                trial_template = self.make_template(trial_params)
                # Determine the expected error string length.
                expected_str_len = self.get_expected_str_len(trial_params)
                # Construct the header object to pass to apply_check().
                trial_header = self.make_header(trial_params)
                sys.stdout = io.StringIO()
                stream_handler = logging.StreamHandler(sys.stdout)
                LOGGER.addHandler(stream_handler)
                # Run apply_check().
                apply_check('', trial_template, trial_header, {})
                output = sys.stdout.getvalue().strip()
                if output:
                    actual_str_len = 1
                else:
                    actual_str_len = 0
                self.assertEqual(actual_str_len, expected_str_len)
                LOGGER.removeHandler(stream_handler)

    @unittest.skip('Skip TestMulti')
    def test_multi(self):
        """
        Tests apply_check() when dealing with a 'multi' keyword(s).
        """
        pass

# --------------------


if __name__ == "__main__":
    unittest.main()
