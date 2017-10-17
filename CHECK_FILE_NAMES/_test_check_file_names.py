"""
.. module:: _test_check_file_names.py

   :synopsis: Test module for check_file_names modules.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import unittest
from check_dirpath_lower import check_dirpath_lower

#--------------------

class TestCheckFileNames(unittest.TestCase):
    """ Main test class. """

    def test_dirpath_not_lower_single(self):
        """ Test case where array is a single path, not all lowercase. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_dirpath_lower(['/root/All_lower/'], None)
            check_string = ("WARNING:root:Subdirectory is not all lowercase:"
                            " /root/All_lower")
            self.assertEqual(len(context_manager.output), 1)
            self.assertEqual(context_manager.output[0], check_string)

    def test_dirpath_not_lower_multi(self):
        """ Test case where array has multiple paths, not all lowercase.
        Note that check_dirpath_lower does not preserve order. """
        with self.assertLogs(level="DEBUG") as context_manager:
            check_dirpath_lower(['/root/All_lower/', '/root2/All_lower2/'], None)
            check_string = ("WARNING:root:Subdirectory is not all lowercase:"
                            " /root/All_lower")
            check_string2 = ("WARNING:root:Subdirectory is not all lowercase:"
                             " /root2/All_lower2")
            self.assertEqual(len(context_manager.output), 2)
            self.assertIn(check_string, context_manager.output)
            self.assertIn(check_string2, context_manager.output)

    def test_dirpath_is_lower_single(self):
        """ Test case where array is a single path, is all lowercase. """
        try:
            # If there are any DEBUG levels issued, catch them here.
            with self.assertLogs(level="DEBUG") as context_manager:
                check_dirpath_lower(['/root/all_lower/'], None)
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
                check_dirpath_lower(['/root/all_lower/', '/root2/all_lower2/'],
                                    None)
                self.assertEqual(len(context_manager.output), 0)
        except AssertionError:
            # Otherwise, the assertLogs() will return with an error, in which
            # case we know there were no Warnings raised, so pass the test.
            return True

#--------------------

if __name__ == "__main__":
    unittest.main()
