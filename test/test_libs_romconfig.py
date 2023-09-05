import configparser
import datetime
import os
import unittest

import libs.cons as cons
import libs.cores as cores
import libs.files as files
import libs.roms as roms
import libs.config as config
import libs.romconfig as romconfig

import test_tools


# Test cases
#=======================================================================================================================
class TestClassRomConfig(unittest.TestCase):
    def test_method_load_from_disk_non_existing_file(self):
        """
        Test for the load of a RomConfig from disk when the file doesn't exist.

        :return: Nothing.
        """
        s_prog_cfg = '/tmp/non-existing-file.ini'
        o_rom_config = romconfig.RomConfig()
        o_prog_config = config.ProgramCfg()

        self.assertRaises(IOError, o_rom_config.load_from_disk, s_prog_cfg, o_prog_config)

    def test_method_load_from_disk_with_rom_unmatched_ccrc32_a(self):
        """
        Test for the load of a RomConfig from disk when the CRC32 of the loaded rom is empty but the romconfig ini file
        has a ccrc32 defined.

        :return: Nothing.
        """
        o_prog_cfg = self._load_program_cfg()

        # Preparation of the ROM to be used
        #----------------------------------
        o_rom = self._load_rom_without_dat_info()

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(test_tools.get_test_input_dir(self), 'ini_files',
                                        'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - '
                                        'no patch.ini')
        o_config = romconfig.RomConfig()
        o_config.o_rom = o_rom

        self.assertRaises(ValueError, o_config.load_from_disk, s_romconfig_file, o_prog_cfg)

    def test_method_load_from_disk_with_rom_unmatched_ccrc32_b(self):
        """
        Test for the load of a RomConfig from disk when the crc32 of the loaded rom is populated but the romconfig ini
        file doesn't have the ccrc32 defined.

        :return: Nothing.
        """
        o_prog_cfg = self._load_program_cfg()
        o_rom = self._load_rom_with_dat_info()

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(test_tools.get_test_input_dir(self), 'ini_files',
                                        'xxxxxxxx - phantom gear (world) (v0.2) (demo) (aftermarket) (unl).ini')
        o_rom_config = romconfig.RomConfig()
        o_rom_config.o_rom = o_rom

        self.assertRaises(ValueError, o_rom_config.load_from_disk, s_romconfig_file, o_prog_cfg)

    def test_method_load_from_disk_with_no_rom_loaded(self):
        """
        Test for the case when a RomConfig is wanted to be loaded from a file but no Rom has been previously loaded in
        the RomConfig object.

        :return: Nothing.
        """
        # Preparation of a program config that will provide the path of the patches
        #--------------------------------------------------------------------------
        o_prog_cfg = self._load_program_cfg()

        # Trying to load the romconfig from a file
        #-----------------------------------------
        s_file = os.path.join(test_tools.get_test_input_dir(self), 'ini_files',
                              'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - no patch.ini')

        o_config = romconfig.RomConfig()
        self.assertRaises(ValueError, o_config.load_from_disk, s_file, o_prog_cfg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_no_patch(self):
        """
        Test for the load of a RomConfig from disk when the CRC32 of the loaded rom and the romconfig .ini match.

        :return: Nothing.
        """
        o_prog_cfg = self._load_program_cfg()

        # Preparation of the ROM to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(test_tools.get_test_input_dir(self), 'ini_files',
                                        'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - '
                                        'no patch.ini')
        o_config = romconfig.RomConfig()
        o_config.o_rom = o_rom

        o_config.load_from_disk(ps_file=s_romconfig_file, po_prog_cfg=o_prog_cfg)

        # Comparison of the outputs
        #--------------------------
        s_expect_core = os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'picodrive_libretro.so')
        o_expect_core = cores.Core(s_expect_core)
        o_expect_rom = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        lx_actual = []
        lx_expect = []

        lx_actual.append(o_config.s_region)
        lx_expect.append('japan')

        lx_actual.append(o_config.f_refresh)
        lx_expect.append(60.0)

        lx_actual.append(o_config.o_core)
        lx_expect.append(o_expect_core)

        lx_actual.append(o_config.o_patch)
        lx_expect.append(None)

        lx_actual.append(o_config.o_rom)
        lx_expect.append(o_expect_rom)

        s_msg = 'The configuration loaded from disk doesn\'t match the expected results'
        self.assertEqual(lx_expect, lx_actual, s_msg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_and_everything_defined__user_test(self):
        """
        When loading a fully defined romconfig file, is the user properly read?

        :return: Nothing.
        """
        o_config = self._load_config_with_matched_ccrc32_and_patch()
        s_expect = 'joe'
        s_actual = o_config.s_user

        s_msg = 'The user read from the romconfig is not what was expected'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_and_everything_defined__rom_test(self):
        """
        When loading a fully defined romconfig file, is the rom object properly read?

        :return: Nothing.
        """
        o_config = self._load_config_with_matched_ccrc32_and_patch()

        # Data preparation
        #-----------------
        s_rom_path = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_path = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom(ps_platform='mdr-crt',
                         ps_path=s_rom_path,
                         ps_dat=s_dat_path)

        # Comparison
        #-----------
        o_expect = o_rom
        o_actual = o_config.o_rom

        s_msg = 'The rom read from the romconfig is not what was expected'
        self.assertEqual(o_expect, o_actual, s_msg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_and_everything_defined__region_test(self):
        """
        When loading a fully defined romconfig file, is the region properly read?

        :return: Nothing.
        """
        o_config = self._load_config_with_matched_ccrc32_and_patch()

        # Comparison
        #-----------
        o_expect = 'japan'
        o_actual = o_config.s_region

        s_msg = 'The region read from the romconfig is not what was expected'
        self.assertEqual(o_expect, o_actual, s_msg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_and_everything_defined__core_test(self):
        """
        When loading a fully defined romconfig file, is the core properly read?

        :return: Nothing.
        """
        o_rom_config = self._load_config_with_matched_ccrc32_and_patch()

        # Data loading
        #-------------
        o_expect = cores.Core(os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'picodrive_libretro.so'))

        # Comparison
        #-----------
        o_actual = o_rom_config.o_core

        s_msg = 'The core read from the romconfig is not what was expected'
        self.assertEqual(o_expect, o_actual, s_msg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_and_everything_defined__refresh_test(self):
        """
        When loading a fully defined romconfig file, is the refresh properly read?

        :return: Nothing.
        """
        o_config = self._load_config_with_matched_ccrc32_and_patch()

        # Comparison
        #-----------
        f_expect = 60.0
        f_actual = o_config.f_refresh

        s_msg = 'The refresh read from the romconfig is not what was expected'
        self.assertEqual(f_expect, f_actual, s_msg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_and_patch_not_found(self):
        """
        Test to load a RomConfig from disk with when the specified patch_file is not found in the current patches' dir.

        :return: Nothing.
        """
        o_prog_cfg = self._load_program_cfg()
        o_rom = self._load_rom_with_dat_info()

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(test_tools.get_test_input_dir(self), 'ini_files',
                                        'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - '
                                        'non-existing patch.ini')
        o_config = romconfig.RomConfig()
        o_config.o_rom = o_rom

        # Finally, we try to load a configuration with a non-existing patch
        #------------------------------------------------------------------
        ls_error_msgs_actual = o_config.load_from_disk(ps_file=s_romconfig_file, po_prog_cfg=o_prog_cfg)

        s_patches_dir = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'mdr-crt')
        ls_error_msgs_expect = [f'ERROR: patch "non-existing-patch" not found in "{s_patches_dir}"']

        s_msg = 'The error message returned when loading a non-existing patch differs from expectation.'
        self.assertEqual(ls_error_msgs_expect, ls_error_msgs_actual, s_msg)

    def test_method_save_to_disk(self):
        """
        After testing the load for each individual parameter of the RomConfig, we can simply save to disk, load, and
        compare both configs to ensure they are the same.

        :return: Nothing.
        """
        # Preparing a ProgramConfig object
        #---------------------------------
        #o_prog_cfg = self._load_program_cfg()
        o_romconfig_original = self._load_config_with_matched_ccrc32_and_patch()

        # Saving the ROMconfig to disk
        #-----------------------------
        s_test_output_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_test_output_dir)
        s_save_file = os.path.join(s_test_output_dir, 'saved_romconfig.ini')
        o_romconfig_original.save_to_disk(s_save_file)

        # Now we build a dictionary with all the saved values
        #----------------------------------------------------
        o_saved_file = configparser.ConfigParser()
        o_saved_file.read(s_save_file)

        ddss_actual_data = {}
        for s_section in o_saved_file.sections():
            ddss_actual_data[s_section] = {}
            for s_key, s_value in o_saved_file[s_section].items():
                ddss_actual_data[s_section][s_key] = s_value

        # Creation of the expected data dictionary (everything will be text)
        #-------------------------------------------------------------------
        # We have the manually replace the date with the date from the saved file, otherwise they won't match
        ddss_expect_data = {'meta':
                                {'builder':  'EmuLaunch v1.0.2023-03-21',
                                 'date':     ddss_actual_data['meta']['date'],
                                 'user':     'joe'},
                            'rom':
                                {'name':     'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl)',
                                 'ccrc32':   'd6cf8cdb',
                                 'platform': 'mdr-crt',
                                 'patch':    'v0.2 to v0.9'},
                            'settings':
                                {'core':     'picodrive',
                                 'region':   'japan',
                                 'refresh':  '60.0'}}

        s_msg = 'The saved configuration doesn\'t contain the right information'
        self.assertEqual(ddss_expect_data, ddss_actual_data, s_msg)

    @staticmethod
    def _load_program_cfg():
        """
        Method to load a generic ProgramConfig.
        :return: A program configuration just with cores path.
        :rtype: cfg.ProgramCfg
        """
        o_prog_cfg = config.ProgramCfg()
        o_prog_cfg.s_cores_dir = os.path.join(cons.s_TEST_DATA_DIR, 'cores')
        o_prog_cfg.ds_patch_dirs = {'mdr-crt': os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'mdr-crt')}
        return o_prog_cfg

    @staticmethod
    def _load_rom_with_dat_info():
        """
        Method to load a ROM object with .dat information.

        :return: A rom object populated with .dat information.
        :rtype: roms.Rom
        """
        s_dat = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        s_rom = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                             'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom, ps_dat=s_dat)

        return o_rom

    @staticmethod
    def _load_rom_without_dat_info():
        """
        Method to load a ROM object with .dat information.

        :return: A rom object populated with .dat information.
        :rtype: roms.Rom
        """
        s_rom = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                             'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom)

        return o_rom

    def _load_config_with_matched_ccrc32_and_patch(self):
        """
        Method to fully load a romconfig matching the ROM ccrc32 and specifying a patch_file. This method is auxiliary
        for other test methods.

        :return:
        :rtype: romconfig.RomConfig
        """
        o_prog_cfg = self._load_program_cfg()
        o_rom = self._load_rom_with_dat_info()

        # Building ROMconfig and loading settings from disk
        #--------------------------------------------------
        o_rom_config = romconfig.RomConfig()
        o_rom_config.o_rom = o_rom
        s_rom_config = os.path.join(test_tools.get_test_input_dir(self), 'ini_files',
                                    'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - '
                                    'with patch.ini')

        ls_errors = o_rom_config.load_from_disk(s_rom_config, o_prog_cfg)

        return o_rom_config


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
