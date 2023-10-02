import os
import unittest

import libs.cons as cons
import libs.config as config
import libs.patches as patches
import libs.roms as roms
import libs.romconfig as romconfig
import testtools


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

    def test_init_from_file__data_directories(self):
        """
        Method to test the reading of data directories from the configuration file.
        :return: Nothing.
        """
        s_cfg_file = os.path.join(testtools.get_test_input_dir(self), 'config__data_section_user_directory.yaml')
        o_program_config = config.ProgramCfg(s_cfg_file)
        print()
        print(o_program_config)

        self.assertEqual(True, False)

    # Method build_rom_install_dir_path
    #----------------------------------
    def test__build_rom_install_dir_path__rom_with_crc32_and_no_patch(self):
        """
        Test for the dir path when all ROM data is provided but no patch has to be applied.

        :return: Nothing.
        """
        # Data initialization
        #--------------------
        # Program config - Only the path of the cache dir is needed.
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo'

        # A ROM - Only the platform, the name, and the clean CRC32 are needed
        #--------------------------------------------------------------------
        o_rom = roms.Rom('mdr-crt', 'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        o_rom.s_ccrc32 = 'd6cf8cdb'

        # A ROM config - Only the Rom and the user are needed
        #----------------------------------------------------
        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.s_user = 'john'

        s_actual_dir = o_prog_cfg.build_rom_install_dir_path(o_rom_cfg)
        s_expect_dir = '/foo/games/mdr-crt - d6cf8cdb+xxxxxxxx - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom with CRC32 but no patch.'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test__build_rom_install_dir_path__rom_without_crc32_and_no_patch(self):
        """
        Test for the dir path when ROM doesn't have CRC32 data and no patch has to be applied.

        :return: Nothing.
        """
        # Data initialization
        #--------------------
        # Program config - Only the path of the cache dir is needed.
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo'

        # A ROM - Only the platform, the name, and the clean CRC32 are needed
        #--------------------------------------------------------------------
        o_rom = roms.Rom('mdr-crt', 'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')

        # A ROM config - Only the Rom and the user are needed
        #----------------------------------------------------
        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.s_user = 'john'

        s_actual_dir = o_prog_cfg.build_rom_install_dir_path(o_rom_cfg)
        s_expect_dir = '/foo/games/mdr-crt - xxxxxxxx+xxxxxxxx - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom without CRC32 and no patch.'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test__build_rom_install_dir_path__rom_with_crc32_and_patch(self):
        """
        Test for the dir path when all ROM data is provided but no patch has to be applied.

        :return: Nothing.
        """
        # Data initialization
        #--------------------
        # Program config - Only the path of the cache dir is needed.
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo'

        # A ROM - Only the platform, the name, and the clean CRC32 are needed
        #--------------------------------------------------------------------
        o_rom = roms.Rom('mdr-crt', 'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        o_rom.s_ccrc32 = 'd6cf8cdb'

        # A Patch
        #--------
        o_patch = patches.Patch()
        o_patch.s_title = 'Test patch'

        # A ROM config - Only the Rom and the user are needed
        #----------------------------------------------------
        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.o_patch = o_patch
        o_rom_cfg.s_user = 'john'

        s_actual_dir = o_prog_cfg.build_rom_install_dir_path(o_rom_cfg)
        s_expect_dir = '/foo/games/mdr-crt - d6cf8cdb+13818f29 - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom with CRC32 but no patch.'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test__build_rom_install_dir_path__rom_without_crc32_and_patch(self):
        """
        Test for the dir path when a ROM doesn't have CRC32 and a patch has to be applied.

        :return: Nothing.
        """
        # Data initialization
        #--------------------
        # Program config - Only the path of the cache dir is needed.
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo'

        # A ROM - Only the platform, the name, and the clean CRC32 are needed
        #--------------------------------------------------------------------
        o_rom = roms.Rom('mdr-crt', 'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')

        # A Patch
        #--------
        o_patch = patches.Patch()
        o_patch.s_title = 'Test patch'

        # A ROM config - Only the Rom and the user are needed
        #----------------------------------------------------
        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.o_patch = o_patch
        o_rom_cfg.s_user = 'john'

        s_actual_dir = o_prog_cfg.build_rom_install_dir_path(o_rom_cfg)
        s_expect_dir = '/foo/games/mdr-crt - xxxxxxxx+13818f29 - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom with CRC32 but no patch.'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    # Method build_user_game_dir_path
    #--------------------------------
    def test__build_user_game_dir_path__with_proper_inputs(self):
        """
        Test for the dir path when all the data is provided (including a patch_file).

        :return: Nothing.
        """
        # Program configuration object - Only the cache dir path is required
        #-------------------------------------------------------------------
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo'

        # RomConfig including a Rom and a user
        #-------------------------------------
        o_rom = roms.Rom('mdr-crt', 'Sonic the Hedgehog 2.zip')
        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.s_user = 'paul'

        s_actual_dir = o_prog_cfg.build_user_game_dir_path(o_rom_cfg)
        s_expect_dir = '/foo/users/paul/mdr-crt'

        s_msg = 'Installation dir different from what was expected for rom with patch_file applied'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    # Method build_user_game_settings_path
    #-------------------------------------
    def test__build_user_game_settings_path__rom_with_crc32(self):
        """
        Test for a ROM having CRC32.

        :return: Nothing.
        """
        # Data preparation
        #-----------------
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/this/that'

        o_rom = roms.Rom('mdr-crt', 'Sonic is fast as hell.7z')
        o_rom.s_ccrc32 = '87654321'

        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.s_user = 'tanatos'

        # Obtaining the path and comparing with the expectation
        #------------------------------------------------------
        s_actual_file = o_prog_cfg.build_user_game_settings_path(o_rom_cfg)
        s_expect_file = '/this/that/users/tanatos/mdr-crt/87654321 - sonic is fast as hell.ini'
        s_msg = 'The user settings file is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)

    def test__build_user_game_settings_path__rom_without_crc32(self):
        """
        Test for a ROM without CRC32.

        :return: Nothing.
        """
        # Data preparation
        #-----------------
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/this/that'

        o_rom = roms.Rom('mdr-crt', 'Sonic is fast as hell.7z')

        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.s_user = 'tanatos'

        # Obtaining the path and comparing with the expectation
        #------------------------------------------------------
        s_actual_file = o_prog_cfg.build_user_game_settings_path(o_rom_cfg)
        s_expect_file = '/this/that/users/tanatos/mdr-crt/xxxxxxxx - sonic is fast as hell.ini'
        s_msg = 'The user settings file is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)

    # Method build_rom_install_game_settings
    #---------------------------------------
    def test__build_rom_install_game_settings__rom_with_crc32(self):
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo/bar'

        o_rom = roms.Rom(ps_platform='mdr-crt', ps_path='This is a game.rar')
        o_rom.s_ccrc32 = '12345678'

        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom

        s_actual_file = o_prog_cfg.build_rom_install_game_settings(o_rom_cfg)
        s_expect_file = '/foo/bar/games/mdr-crt - 12345678+xxxxxxxx - this is a game/settings.ini'
        s_msg = 'The install settings file path is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)

    def test__build_rom_install_game_settings__rom_without_crc32(self):
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo/bar'

        o_rom = roms.Rom(ps_platform='mdr-crt', ps_path='This is a game.rar')

        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom

        s_actual_file = o_prog_cfg.build_rom_install_game_settings(o_rom_cfg)
        s_expect_file = '/foo/bar/games/mdr-crt - xxxxxxxx+xxxxxxxx - this is a game/settings.ini'
        s_msg = 'The install settings file path is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
