import os
import unittest

import libs.cons as cons
import libs.config as config


# Test classes
#=======================================================================================================================
class TestClassProgramCfg(unittest.TestCase):
    def test_init_from_file(self):
        # TODO: Delete this full-read test and write individual ones for each of the parameters in the config file.
        s_file = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'config', 'config-for_romconfig_testing_b.yaml')
        o_cfg = config.ProgramCfg(ps_file=s_file)

        lx_actual = []
        lx_expect = []

        lx_actual.append(o_cfg.s_cache_dir)
        lx_expect.append('/tmp/emulaunch_cache')

        lx_actual.append(o_cfg.i_cache_size)
        lx_expect.append(5000)

        lx_actual.append(o_cfg.ds_rom_dirs)
        lx_expect.append({'mdr-crt': '/tmp/mdr-crt'})

        # TODO: Continue adding values of missing attributes

        s_msg = 'Read data from program config yaml is not what was expected'
        self.assertEqual(lx_expect, lx_actual, s_msg)

    def test_init_from_file_users(self):
        """
        Test to check list of users is properly read from the ini file.
        :return: Nothing.
        """
        s_file = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'config', 'config-for_romconfig_testing_b.yaml')
        o_cfg = config.ProgramCfg(ps_file=s_file)

        ls_expect = ['Guest', 'John', 'Charlie']
        ls_actual = o_cfg.ls_users

        s_msg = 'Users read from program config file are not what was expected'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_init_from_file_users_complicated(self):
        """
        Test to check list of complicated usernames is properly read from the ini file.
        :return: Nothing.
        """
        s_file = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'config', 'config-for_romconfig_testing_c.yaml')
        o_cfg = config.ProgramCfg(ps_file=s_file)

        ls_expect = ['123456', 'this user', 'cañón']
        ls_actual = o_cfg.ls_users

        s_msg = 'Users read from program config file are not what was expected'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_init_from_file_cache_size_from_integer(self):
        """
        Test to check the cache size is properly defined as an integer.
        :return: Nothing.
        """
        s_file = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'config', 'config-for_romconfig_testing_c.yaml')
        o_cfg = config.ProgramCfg(ps_file=s_file)

        i_expect = 5000
        i_actual = o_cfg.i_cache_size

        s_msg = 'Cache size not properly read from config file when defined as an integer.'
        self.assertEqual(i_expect, i_actual, s_msg)

    def test_init_from_file_cache_size_from_string(self):
        """
        Test to check the cache size is properly defined as an integer.
        :return: Nothing.
        """
        s_file = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'config',
                              'config-for_romconfig_testing_d_cache_as_string.yaml')
        o_cfg = config.ProgramCfg(ps_file=s_file)

        i_expect = 5000
        i_actual = o_cfg.i_cache_size

        s_msg = 'Cache size not properly read from config file when defined as an string.'
        self.assertEqual(i_expect, i_actual, s_msg)

    def test_init_from_file_cache_size_from_float(self):
        """
        Test to check the cache size is properly defined as an integer.
        :return: Nothing.
        """
        s_file = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'config',
                              'config-for_romconfig_testing_e_cache_as_float.yaml')
        o_cfg = config.ProgramCfg(ps_file=s_file)

        i_expect = 5000
        i_actual = o_cfg.i_cache_size

        s_msg = 'Cache size not properly read from config file when defined as an string.'
        self.assertEqual(i_expect, i_actual, s_msg)

    def test_init_from_file_cores_dir_with_home_expansion(self):
        """
        Test for home expansion "~" in cores dir.
        :return: Nothing
        """
        s_file = os.path.join(cons.s_TEST_DATA_DIR, 'config',
                              'config-for_romconfig_testing_f_cores_dir_home_expansion.yaml')
        o_cfg = config.ProgramCfg(ps_file=s_file)

        s_expect = os.path.expanduser('~/foo')
        s_actual = o_cfg.s_cores_dir
        s_msg = 'Cores dir using ~ as shortcut to home not read properly from config.'
        self.assertEqual(s_expect, s_actual, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
