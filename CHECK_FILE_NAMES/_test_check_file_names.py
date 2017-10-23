"""
.. module:: _test_check_file_names.py

   :synopsis: Test module for check_file_names modules.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import os
import unittest
from check_file_names import read_known_missions, read_known_filters
from check_dirpath_lower import check_dirpath_lower
from check_file_compliance import check_file_compliance
from check_in_known_filters import check_in_known_filters
from check_in_known_missions import check_in_known_missions
from check_is_version_string import check_is_version_string

#--------------------

class TestCheckDirpathLower(unittest.TestCase):
    """ Main test class for check_dirpath_lower module. """
    # Define test directory paths.
    good_dir_1 = '/root/all_lower/'
    good_dir_2 = '/root2/all_lower2/'
    bad_dir_1 = '/root/All_lower/'
    bad_dir_2 = '/root2/All_lower2/'
    # Directory list of a single path that should pass.
    dir_list_single_good = [good_dir_1]
    # Directory list of a single path that should fail.
    dir_list_single_bad = [bad_dir_1]
    # Directory list of multiple paths that should pass.
    dir_list_multi_good = [good_dir_1, good_dir_2]
    # Directory list of multiple paths that should fail.
    dir_list_multi_bad = [bad_dir_1, bad_dir_2]
    # Message to compare against when first bad path fails.
    check_string_1 = ("WARNING:root:Subdirectory is not all lowercase: " +
                      os.path.dirname(bad_dir_1))
    # Message to compare against when second bad path fails.
    check_string_2 = ("WARNING:root:Subdirectory is not all lowercase: " +
                      os.path.dirname(bad_dir_2))

    def test_dirpath_is_lower_single(self):
        """ Test case where array is a single path, is all lowercase. """
        try:
            # If there are any DEBUG levels issued, catch them here.
            with self.assertLogs(level="DEBUG") as context_manager:
                check_dirpath_lower(self.dir_list_single_good, None)
                self.assertEqual(len(context_manager.output), 0)
        except AssertionError:
            # Otherwise, the assertLogs() will return with an error, in which
            # case we know there were no Warnings raised, so pass the test.
            return True

    def test_dirpath_is_lower_multi(self):
        """ Test case where array has multiple paths, are all lowercase.
        Note that check_dirpath_lower does not preserve order. """
        try:
            # If there are any DEBUG levels issued, catch them here.
            with self.assertLogs(level="DEBUG") as context_manager:
                check_dirpath_lower(self.dir_list_multi_good, None)
                self.assertEqual(len(context_manager.output), 0)
        except AssertionError:
            # Otherwise, the assertLogs() will return with an error, in which
            # case we know there were no Warnings raised, so pass the test.
            return True

    def test_dirpath_not_lower_single(self):
        """ Test case where array is a single path, not all lowercase. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_dirpath_lower(self.dir_list_single_bad, None)
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0], self.check_string_1)

    def test_dirpath_not_lower_multi(self):
        """ Test case where array has multiple paths, not all lowercase.
        Note that check_dirpath_lower does not preserve order. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_dirpath_lower(self.dir_list_multi_bad, None)
            self.assertEqual(len(context_manager.output), 2)
            self.assertIn(self.check_string_1, context_manager.output)
            self.assertIn(self.check_string_2, context_manager.output)

#--------------------

class TestCheckFileCompliance(unittest.TestCase):
    """ Main test class for check_file_compliance module. """

    # Define input parameters.
    mission = "k2gap"
    # Get the lists of known missions and known filters.
    known_missions = read_known_missions()
    known_filters = read_known_filters()
    # Define a bunch of test files.
    good_file_1 = ("/root/all_lower/hlsp_k2gap_k2_lightcurve"
                   "_201121245-c01_kepler_v1_ts.txt")
    good_file_2 = ("/root/all_lower/hlsp_relics_hst_wfc3ir-30mas_abell3192_"
                   "f105w_v1_drz.fits")
    bad_fields_file = ("/root/all_lower/hlsp_k2gap_k2_lc_target_kepler_v1_"
                       "extra_ts.txt")
    bad_part1_file = ("/root/all_lower/bad_k2gap_k2_lc_target_kepler_v1_"
                      "ts.txt")
    bad_part2_file = ("/root/all_lower/hlsp_bad_k2_lc_target_kepler_v1_"
                      "ts.txt")
    bad_part3_file = ("/root/all_lower/hlsp_k2gap_bad_lc_target_kepler_v1_"
                      "ts.txt")
    bad_part6_file = ("/root/all_lower/hlsp_k2gap_k2_lc_target_bad_v1_"
                      "ts.txt")
    bad_part7_file = ("/root/all_lower/hlsp_k2gap_k2_lc_target_kepler_bad_"
                      "ts.txt")
    bad_part8_file = ("/root/all_lower/hlsp_k2gap_k2_lc_target_kepler_v1_"
                      "bad")
    file_list_single_good = [good_file_1]
    file_list_multi_good = [good_file_1, good_file_2]
    file_list_bad_fields = [bad_fields_file]
    file_list_bad_part1 = [bad_part1_file]
    file_list_bad_part2 = [bad_part2_file]
    file_list_bad_part3 = [bad_part3_file]
    file_list_bad_part6 = [bad_part6_file]
    file_list_bad_part7 = [bad_part7_file]
    file_list_bad_part8 = [bad_part8_file]
    # Message to compare against when file doesn't contain expected number of
    # parts.
    bad_file_fields_string = ("WARNING:root:File does not have 8 parts: " +
                              bad_fields_file)
    # Message to compare against when file doesn't begin with 'hlsp'.
    bad_file_part1_string = ('WARNING:root:Field 1 is not "hlsp": ' +
                             bad_part1_file)
    # Message to compare against when file's second component doesn't match HLSP.
    bad_file_part2_string = ('WARNING:root:Field 2 is not "' + mission + '": ' +
                             bad_part2_file)
    # Message to compare against when file's third component doesn't match
    # known missions.
    bad_file_part3_string = ('WARNING:root:Field 3 ("bad") is not in list of ' +
                             'known missions: ' + bad_part3_file)
    # Message to compare against when file's sixth component doesn't match
    # known filters.
    bad_file_part6_string = ('WARNING:root:Field 6 ("bad") is not in list of ' +
                             'known filters: ' + bad_part6_file)
    # Message to compare against when file's seventh component doesn't look
    # like a version string.
    bad_file_part7_string = ("WARNING:root:Field 7 does not appear to be a"
                             " valid version string: " + bad_part7_file)
    # Message to compare against when file's eighth component doesn't have
    # the form <x>.<y>.
    bad_file_part8_string = ("WARNING:root:Field 8 does not have"
                             " <product>.<extension> format: " + bad_part8_file)

    def test_single_good(self):
        """ Test case where an array of a single file is provided that
        passes. """
        try:
            # If there are any DEBUG levels issued, catch them here.
            with self.assertLogs(level="DEBUG") as context_manager:
                check_file_compliance(self.file_list_single_good, self.mission,
                                      self.known_missions, self.known_filters,
                                      None, None)
                self.assertEqual(len(context_manager.output), 0)
        except AssertionError:
            # Otherwise, the assertLogs() will return with an error, in which
            # case we know there were no Warnings raised, so pass the test.
            return True

    def test_multi_good(self):
        """ Test case where an array of a multiple files is provided that
        passes. """
        try:
            # If there are any DEBUG levels issued, catch them here.
            with self.assertLogs(level="DEBUG") as context_manager:
                check_file_compliance(self.file_list_multi_good, self.mission,
                                      self.known_missions, self.known_filters,
                                      None, None)
                self.assertEqual(len(context_manager.output), 0)
        except AssertionError:
            # Otherwise, the assertLogs() will return with an error, in which
            # case we know there were no Warnings raised, so pass the test.
            return True

    def test_single_bad_fields(self):
        """ Test case of a file that does not have expected number of
        components. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_file_compliance(self.file_list_bad_fields, self.mission,
                                  self.known_missions, self.known_filters,
                                  None, None)
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0],
                             self.bad_file_fields_string)

    def test_single_bad_part1(self):
        """ Test case of a file that does not begin with 'hlsp'. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_file_compliance(self.file_list_bad_part1, self.mission,
                                  self.known_missions, self.known_filters,
                                  None, None)
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0],
                             self.bad_file_part1_string)

    def test_single_bad_part2(self):
        """ Test case of a file whose second component is not the HLSP name. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_file_compliance(self.file_list_bad_part2, self.mission,
                                  self.known_missions, self.known_filters,
                                  None, None)
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0],
                             self.bad_file_part2_string)

    def test_single_bad_part3(self):
        """ Test case of a file that whose third component is not in list of
        known missions. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_file_compliance(self.file_list_bad_part3, self.mission,
                                  self.known_missions, self.known_filters,
                                  None, None)
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0],
                             self.bad_file_part3_string)

    def test_single_bad_part6(self):
        """ Test case of a file that whose sixth component is not in list of
        known filters. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_file_compliance(self.file_list_bad_part6, self.mission,
                                  self.known_missions, self.known_filters,
                                  None, None)
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0],
                             self.bad_file_part6_string)

    def test_single_bad_part7(self):
        """ Test case of a file that whose seventh component does not look
        like a version string. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_file_compliance(self.file_list_bad_part7, self.mission,
                                  self.known_missions, self.known_filters,
                                  None, None)
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0],
                             self.bad_file_part7_string)

    def test_single_bad_part8(self):
        """ Test case of a file that whose eighth component does not have
        a <product>.<extension> format. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_file_compliance(self.file_list_bad_part8, self.mission,
                                  self.known_missions, self.known_filters,
                                  None, None)
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0],
                             self.bad_file_part8_string)


#--------------------

class TestInKnownMissions(unittest.TestCase):
    """ Main test class for check_in_known_missions module. """

    # Get the lists of known missions.
    known_missions = read_known_missions()

    known_mission_single = "k2"
    known_mission_composite = "k2-hst"
    unknown_mission_single = "bad"
    unknown_mission_composite = "bad-k2"
    allowed_mission_single = "any"
    allowd_mission_composite = "k2-any"

    def test_known_single(self):
        """ Test a single known mission. """
        self.assertTrue(check_in_known_missions(self.known_mission_single,
                                                self.known_missions, None))

    def test_known_composite(self):
        """ Test a composite known mission. """
        self.assertTrue(check_in_known_missions(self.known_mission_composite,
                                                self.known_missions, None))

    def test_unknown_single(self):
        """ Test a single unknown mission. """
        self.assertFalse(check_in_known_missions(self.unknown_mission_single,
                                                 self.known_missions, None))

    def test_unknown_composite(self):
        """ Test a composite unknown mission. """
        self.assertFalse(check_in_known_missions(self.unknown_mission_composite,
                                                 self.known_missions, None))

    def test_allowed_single(self):
        """ Test a single temporarily allowed mission. """
        self.assertTrue(check_in_known_missions(self.allowed_mission_single,
                                                self.known_missions,
                                                [self.allowed_mission_single]))

    def test_allowed_composite(self):
        """ Test a composite temporarily allowed mission. """
        self.assertTrue(check_in_known_missions(self.known_mission_composite,
                                                self.known_missions,
                                                [self.allowed_mission_single]))

#--------------------

class TestInKnownFilters(unittest.TestCase):
    """ Main test class for check_in_known_filters module. """

    # Get the lists of known filters.
    known_filters = read_known_filters()

    known_filter_single = "kepler"
    known_filter_composite = "kepler-f105w"
    unknown_filter_single = "bad"
    unknown_filter_composite = "bad-kepler"
    allowed_filter_single = "any"
    allowd_filter_composite = "kepler-any"

    def test_known_single(self):
        """ Test a single known filter. """
        self.assertTrue(check_in_known_filters(self.known_filter_single,
                                               self.known_filters, None))

    def test_known_composite(self):
        """ Test a composite known filter. """
        self.assertTrue(check_in_known_filters(self.known_filter_composite,
                                               self.known_filters, None))

    def test_unknown_single(self):
        """ Test a single unknown filter. """
        self.assertFalse(check_in_known_filters(self.unknown_filter_single,
                                                self.known_filters, None))

    def test_unknown_composite(self):
        """ Test a composite unknown filter. """
        self.assertFalse(check_in_known_filters(self.unknown_filter_composite,
                                                self.known_filters, None))

    def test_allowed_single(self):
        """ Test a single temporarily allowed filter. """
        self.assertTrue(check_in_known_filters(self.allowed_filter_single,
                                               self.known_filters,
                                               [self.allowed_filter_single]))

    def test_allowed_composite(self):
        """ Test a composite temporarily allowed filter. """
        self.assertTrue(check_in_known_filters(self.known_filter_composite,
                                               self.known_filters,
                                               [self.allowed_filter_single]))

#--------------------

class TestIsVersionString(unittest.TestCase):
    """ Main test class for check_is_version_string module. """

    good_version_string_1 = "v1"
    good_version_string_2 = "v1.0"
    bad_version_string_1 = "1"
    bad_version_string_2 = "1.0"

    def test_good_1(self):
        """ Test a good version string with no period. """
        self.assertTrue(check_is_version_string(self.good_version_string_1))

    def test_good_2(self):
        """ Test a good version string with a period. """
        self.assertTrue(check_is_version_string(self.good_version_string_2))

    def test_bad_1(self):
        """ Test a bad version string with no period. """
        self.assertFalse(check_is_version_string(self.bad_version_string_1))

    def test_bad_2(self):
        """ Test a bad version string with a period. """
        self.assertFalse(check_is_version_string(self.bad_version_string_2))

#--------------------

if __name__ == "__main__":
    unittest.main()
