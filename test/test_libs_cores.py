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
    # TODO: get existing core
    # TODO: try to get non existing core
    def test_get_cores_valid_folder(self):
        """
        Test to read the cores available in a dir with some cores.

        :return: Nothing.
        """
        s_cores_dir = os.path.join(cons.s_TEST_DATA_DIR, 'cores')
        lo_cores = cores.get_cores(ps_dir=s_cores_dir, pls_cores_wanted=['picodrive'])

        lx_expect = [1,            # Number of cores
                     True,         # Instance of cores.Core
                     'picodrive',  # Name of the core
                     ]
        lx_actual = [len(lo_cores),
                     isinstance(lo_cores[0], cores.Core),
                     lo_cores[0].s_name]

        s_msg = 'The obtained core is not what was expected.'
        self.assertEqual(lx_expect, lx_actual, s_msg)

    def test_get_cores_non_existing_core(self):
        """
        Test for trying to get a non-existing core.

        :return:  Nothing.
        """
        s_cores_dir = os.path.join(cons.s_TEST_DATA_DIR, 'cores')
        lo_cores = cores.get_cores(ps_dir=s_cores_dir, pls_cores_wanted=['picodrive', 'foo'])

        lx_expect = [1,            # Number of cores
                     True,         # Instance of cores.Core
                     'picodrive',  # Name of the core
                     ]
        lx_actual = [len(lo_cores),
                     isinstance(lo_cores[0], cores.Core),
                     lo_cores[0].s_name]

        s_msg = 'The obtained cores is not what was expected.'
        self.assertEqual(lx_expect, lx_actual, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
