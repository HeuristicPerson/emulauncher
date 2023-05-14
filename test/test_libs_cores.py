import os
import unittest

import libs.cons as cons
import libs.cores as cores


# Tests
#=======================================================================================================================
class TestClassCores(unittest.TestCase):

    def test_equality_success(self):
        """
        Test for the equality comparator of the class when both instances should be considered the same.

        :return: Nothing.
        """
        s_core_a = os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'core_a_dummy_libretro.so')
        o_core_a = cores.Core(s_core_a)

        s_core_b = os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'core_a_dummy_libretro.so')
        o_core_b = cores.Core(s_core_b)

        self.assertTrue(o_core_a == o_core_b)

    def test_equality_fail(self):
        """
        Test for the equality comparator of the class when both instances should be considered different.

        :return: Nothing.
        """
        s_core_a = os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'core_a_dummy_libretro.so')
        o_core_a = cores.Core(s_core_a)

        s_core_b = os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'core_b_dummy_libretro.so')
        o_core_b = cores.Core(s_core_b)

        self.assertFalse(o_core_a == o_core_b)

    def test_initialization_valid_file(self):
        """
        Test to initialize a Core object from a valid file.

        :return: Nothing.
        """
        s_core_file = os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'core_a_dummy_libretro.so')
        o_core = cores.Core(s_core_file)

        ls_actual = []
        ls_expect = []

        ls_expect.append('core_a_dummy')
        ls_actual.append(o_core.s_name)

        ls_expect.append(s_core_file)
        ls_actual.append(o_core.s_path)

        s_msg = 'The initialization of the Core object didn\'t work with valid input'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_initialization_invalid_file(self):
        """
        Test to initialize a Core object from a valid file.

        :return: Nothing.
        """
        s_core_file = os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'core_a_dummy_foo.txt')
        self.assertRaises(ValueError, cores.Core, s_core_file)



class TestFunctionGetCores(unittest.TestCase):
    def test_get_cores_valid_folder(self):
        """
        Test to read the cores available in a dir with some cores.
        :return: Nothing.
        """
        pass


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
