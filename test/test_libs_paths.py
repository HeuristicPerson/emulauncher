"""
Unit tests for libs/paths library.
"""

import os
import unittest

import libs.config as config
import libs.cons as cons
import libs.install
import libs.paths as paths  # <= The library we're testing
import libs.roms as roms
import libs.romconfig as romconfig
import libs.patches as patches

import test_tools


# Test data preparation
# =======================================================================================================================
def _TO_DELETE_build_prog_config(po_test):
    """
    Function to build a valid program config.

    :param po_test:
    :type po_test: unittest.TestCase

    :return:
    :rtype: config.ProgramCfg
    """
    s_prog_cfg = os.path.join(test_tools.get_test_input_dir(po_test), 'program_config.yaml')
    o_prog_cfg = config.ProgramCfg(s_prog_cfg)
    return o_prog_cfg


def _TO_DELETE_build_rom_config_full(po_test):
    """

    :param po_test:
    :return:
    """

    s_rom = os.path.join(cons.s_TEST_DATA_DIR, 'roms',
                         'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
    s_dat = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')

    o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom)
    o_rom.populate_from_dat(s_dat)

    s_rom_cfg = os.path.join(cons.s_TEST_DATA_DIR,
                             'romconfig',
                             'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - with patch_file.ini')
    o_rom_cfg = romconfig.RomConfig()
    o_rom_cfg.o_rom = o_rom
    o_rom_cfg.load_from_disk(ps_file=s_rom_cfg, po_prog_cfg=o_prog_cfg)



def _TO_DELETE_build_prog_and_rom_configs_with_patch():
    """
    Function to build a valid romconfig
    :return:
    """
    s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR,
                              'config',
                              'config-for_path_library_testing_a.yaml')
    o_prog_cfg = config.ProgramCfg(s_prog_cfg)

    s_rom = os.path.join(cons.s_TEST_DATA_DIR,
                         'roms',
                         'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
    s_dat = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')

    o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom)
    o_rom.populate_from_dat(s_dat)

    s_rom_cfg = os.path.join(cons.s_TEST_DATA_DIR,
                             'romconfig',
                             'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - with patch_file.ini')
    o_rom_cfg = romconfig.RomConfig()
    o_rom_cfg.o_rom = o_rom
    o_rom_cfg.load_from_disk(ps_file=s_rom_cfg, po_prog_cfg=o_prog_cfg)

    return o_prog_cfg, o_rom_cfg


def _TO_DELETE__build_prog_and_rom_configs_without_patch():
    """
    Function to build a valid romconfig
    :return:
    """
    s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR,
                              'config',
                              'config-for_path_library_testing_a.yaml')
    o_prog_cfg = config.ProgramCfg(s_prog_cfg)

    s_rom = os.path.join(cons.s_TEST_DATA_DIR,
                         'roms',
                         'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
    s_dat = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')

    o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom)
    o_rom.populate_from_dat(s_dat)

    s_rom_cfg = os.path.join(cons.s_TEST_DATA_DIR,
                             'romconfig',
                             'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl).ini')
    o_rom_cfg = romconfig.RomConfig()
    o_rom_cfg.o_rom = o_rom
    o_rom_cfg.load_from_disk(ps_file=s_rom_cfg, po_prog_cfg=o_prog_cfg)

    return o_prog_cfg, o_rom_cfg


def _TO_DELETE__build_prog_and_rom_configs_without_dat():
    """
    Function to build a valid romconfig
    :return:
    """
    s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR,
                              'config',
                              'config-for_path_library_testing_a.yaml')
    o_prog_cfg = config.ProgramCfg(s_prog_cfg)

    s_rom = os.path.join(cons.s_TEST_DATA_DIR,
                         'roms',
                         'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')

    o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom)

    s_rom_cfg = os.path.join(cons.s_TEST_DATA_DIR,
                             'romconfig',
                             'xxxxxxxx - phantom gear (world) (v0.2) (demo) (aftermarket) (unl).ini')
    o_rom_cfg = romconfig.RomConfig()
    o_rom_cfg.o_rom = o_rom
    o_rom_cfg.load_from_disk(ps_file=s_rom_cfg, po_prog_cfg=o_prog_cfg)

    return o_prog_cfg, o_rom_cfg


# Test cases
#=======================================================================================================================
class TestFunctionBuildRomInstallDirPath(unittest.TestCase):
    """
    Class to test the build_rom_install_dir_path function.
    """

    def test_rom_with_crc32_and_no_patch(self):
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

        s_actual_dir = paths.build_rom_install_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/foo/games/mdr-crt - d6cf8cdb+xxxxxxxx - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom with CRC32 but no patch.'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test_rom_without_crc32_and_no_patch(self):
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

        s_actual_dir = paths.build_rom_install_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/foo/games/mdr-crt - xxxxxxxx+xxxxxxxx - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom without CRC32 and no patch.'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test_rom_with_crc32_and_patch(self):
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

        s_actual_dir = paths.build_rom_install_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/foo/games/mdr-crt - d6cf8cdb+13818f29 - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom with CRC32 but no patch.'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test_rom_without_crc32_and_patch(self):
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

        s_actual_dir = paths.build_rom_install_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/foo/games/mdr-crt - xxxxxxxx+13818f29 - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom with CRC32 but no patch.'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)


class TestFunctionBuildUserGameDirPath(unittest.TestCase):
    def test_with_proper_inputs(self):
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

        s_actual_dir = paths.build_user_game_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/foo/users/paul/mdr-crt'

        s_msg = 'Installation dir different from what was expected for rom with patch_file applied'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)


class TestFunctionBuildUserGameSettingsPath(unittest.TestCase):
    def test_rom_with_crc32(self):
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
        s_actual_file = paths.build_user_game_settings_path(o_rom_cfg, o_prog_cfg)
        s_expect_file = '/this/that/users/tanatos/mdr-crt/87654321 - sonic is fast as hell.ini'
        s_msg = 'The user settings file is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)

    def test_rom_without_crc32(self):
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
        s_actual_file = paths.build_user_game_settings_path(o_rom_cfg, o_prog_cfg)
        s_expect_file = '/this/that/users/tanatos/mdr-crt/xxxxxxxx - sonic is fast as hell.ini'
        s_msg = 'The user settings file is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)


class TestFunctionBuildRomInstallGameSettings(unittest.TestCase):
    def test_rom_with_crc32(self):
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo/bar'

        o_rom = roms.Rom(ps_platform='mdr-crt', ps_path='This is a game.rar')
        o_rom.s_ccrc32 = '12345678'

        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom

        s_actual_file = paths.build_rom_install_game_settings(po_rom_config=o_rom_cfg, po_program_config=o_prog_cfg)
        s_expect_file = '/foo/bar/games/mdr-crt - 12345678+xxxxxxxx - this is a game/settings.ini'
        s_msg = 'The install settings file path is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)

    def test_rom_without_crc32(self):
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/foo/bar'

        o_rom = roms.Rom(ps_platform='mdr-crt', ps_path='This is a game.rar')

        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom

        s_actual_file = paths.build_rom_install_game_settings(po_rom_config=o_rom_cfg, po_program_config=o_prog_cfg)
        s_expect_file = '/foo/bar/games/mdr-crt - xxxxxxxx+xxxxxxxx - this is a game/settings.ini'
        s_msg = 'The install settings file path is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)


class TestFunctionBuildRomInstalledFlagFilePath(unittest.TestCase):
    def test_creation_of_install_flag_file__rom_with_crc32_no_patch(self):
        """
        Test for the creation of an installed flag file for a ROM with CRC32.
        :return:
        """
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/tmp/this_dir'

        o_rom = roms.Rom('mdr-crt', 'This game.zip')
        o_rom.s_ccrc32 = '1a1a1a1a'

        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.s_user = 'joe'

        s_actual_file = libs.install._build_rom_installed_flag_file_path(po_rom_config=o_rom_cfg, po_program_config=o_prog_cfg)
        s_expect_file = '/tmp/this_dir/games/mdr-crt - 1a1a1a1a+xxxxxxxx - this game/installed.txt'

        s_msg = 'The installed flag file path is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)

    def test_creation_of_install_flag_file__rom_without_crc32_no_patch(self):
        """
        Test for the creation of an installed flag file for a ROM with CRC32.
        :return:
        """
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cache_dir = '/tmp/this_dir'

        o_rom = roms.Rom('mdr-crt', 'This game.zip')

        o_rom_cfg = romconfig.RomConfig()
        o_rom_cfg.o_rom = o_rom
        o_rom_cfg.s_user = 'joe'

        s_actual_file = libs.install._build_rom_installed_flag_file_path(po_rom_config=o_rom_cfg, po_program_config=o_prog_cfg)
        s_expect_file = '/tmp/this_dir/games/mdr-crt - xxxxxxxx+xxxxxxxx - this game/installed.txt'

        s_msg = 'The installed flag file path is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)

# Main code
# =======================================================================================================================
if __name__ == '__main__':
    unittest.main()
