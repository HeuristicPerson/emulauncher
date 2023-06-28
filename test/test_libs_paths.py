"""
Unit tests for libs/paths library.
"""

import os
import unittest

import libs.config as config
import libs.cons as cons
import libs.paths as paths  # <= The library we're testing
import libs.roms as roms
import libs.romconfig as romconfig


# Test data preparation
# =======================================================================================================================
def _build_prog_and_rom_configs_with_patch():
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
                             'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - with patch.ini')
    o_rom_cfg = romconfig.RomConfig()
    o_rom_cfg.o_rom = o_rom
    o_rom_cfg.load_from_disk(ps_file=s_rom_cfg, po_prog_cfg=o_prog_cfg)

    return o_prog_cfg, o_rom_cfg


def _build_prog_and_rom_configs_without_patch():
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


def _build_prog_and_rom_configs_without_dat():
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
# =======================================================================================================================
@unittest.SkipTest
class TestFunctionBuildRomconfigSaveFile(unittest.TestCase):
    def test_full_romconfig_and_full_programconfig(self):
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_with_patch()
        print(o_prog_cfg)
        print(o_rom_cfg)

        self.assertEqual(True, False)


class TestFunctionBuildRomInstallDirPath(unittest.TestCase):
    """
    Class to test the build_rom_install_dir_path function.
    """

    def test_full_romconfig_and_full_program_config(self):
        """
        Test for the dir path when all the data is provided.

        :return: Nothing.
        """
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_with_patch()
        s_actual_dir = paths.build_rom_install_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/tmp/emulaunch_cache/games/mdr-crt - d6cf8cdb+2e94ed41 - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom with patch applied'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test_partial_romconfig_and_full_program_config(self):
        """
        Test for the dir path when all there is no patch applied.

        :return: Nothing.
        """
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_without_patch()
        s_actual_dir = paths.build_rom_install_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/tmp/emulaunch_cache/games/mdr-crt - d6cf8cdb+xxxxxxxx - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected for rom without patch applied'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test_unknown_romconfig_and_full_program_config(self):
        """
        Test for the dir path when the ROM is not recognised by a dat file, so it doesn't have a CRC32 defined.

        :return: Nothing.
        """
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_without_dat()
        s_actual_dir = paths.build_rom_install_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/tmp/emulaunch_cache/games/mdr-crt - xxxxxxxx+xxxxxxxx - phantom gear (world) (v0.2) (demo) ' \
                       '(aftermarket) (unl)'

        s_msg = 'Installation dir different from what was expected from rom without known CRC32 (and without patch)'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)


class TestFunctionBuildUserGameDirPath(unittest.TestCase):
    def test_full_romconfig_and_full_program_config(self):
        """
        Test for the dir path when all the data is provided (including a patch).

        :return: Nothing.
        """
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_with_patch()
        s_actual_dir = paths.build_user_game_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/tmp/emulaunch_cache/users/joe/mdr-crt'
        s_msg = 'Installation dir different from what was expected for rom with patch applied'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)

    def test_full_romconfig_and_partial_program_config(self):
        """
        Test for the dir path when all the data is provided for a rom not matching a dat

        :return: Nothing.
        """
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_without_dat()
        s_actual_dir = paths.build_user_game_dir_path(o_rom_cfg, o_prog_cfg)
        s_expect_dir = '/tmp/emulaunch_cache/users/joe/mdr-crt'
        s_msg = 'Installation dir different from what was expected for rom with patch applied'
        self.assertEqual(s_expect_dir, s_actual_dir, s_msg)


class TestFunctionBuildUserGameSettings(unittest.TestCase):
    def test_full_romconfig_and_full_program_config(self):
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_without_patch()
        s_actual_file = paths.build_user_game_settings(o_rom_cfg, o_prog_cfg)
        s_expect_file = '/tmp/emulaunch_cache/users/joe/mdr-crt/d6cf8cdb - phantom gear (world) (v0.2) (demo) ' \
                        '(aftermarket) (unl).ini'
        s_msg = 'The user settings file is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)


class TestFunctionBuildRomInstallGameSettings(unittest.TestCase):
    def test_full_romconfig_and_full_program_config(self):
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_without_patch()
        s_actual_file = paths.build_rom_install_game_settings(po_rom_config=o_rom_cfg, po_program_config=o_prog_cfg)
        s_expect_file = '/tmp/emulaunch_cache/games/mdr-crt - d6cf8cdb+xxxxxxxx - phantom gear (world) (v0.2) (demo) ' \
                        '(aftermarket) (unl)/settings.ini'
        s_msg = 'The install settings file path is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)


class TestFunctionBuildRomInstalledFlagFilePath(unittest.TestCase):
    def test_full_romconfig_and_full_program_config(self):
        o_prog_cfg, o_rom_cfg = _build_prog_and_rom_configs_without_patch()
        s_actual_file = paths.build_rom_installed_flag_file_path(po_rom_config=o_rom_cfg, po_program_config=o_prog_cfg)
        s_expect_file = '/tmp/emulaunch_cache/games/mdr-crt - d6cf8cdb+xxxxxxxx - phantom gear (world) (v0.2) (demo) ' \
                        '(aftermarket) (unl)/installed.txt'
        s_msg = 'The installed flag file path is different from the expected result.'
        self.assertEqual(s_expect_file, s_actual_file, s_msg)


# Main code
# =======================================================================================================================
if __name__ == '__main__':
    unittest.main()
