"""
.. module:: _test_apply_metadata_check.py

   :synopsis: Test module for apply_metadata_check modules.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import io
import logging
import sys
import unittest
from astropy.io import fits
from apply_metadata_check import validate_date, validate_time, check_date_obs
from apply_metadata_check import apply_check

LOGGER = logging.getLogger()

#--------------------

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

#--------------------

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

#--------------------

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

#--------------------

class TestApplyCheck(unittest.TestCase):
    """
    Test class for the apply_check() method.
    """
    pass

#--------------------

if __name__ == "__main__":
    unittest.main()
