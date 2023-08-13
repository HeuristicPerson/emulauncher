import configparser
import datetime
import io
import os
import unittest

import libs.cons as cons
import libs.cores as cores
import libs.roms as roms
import libs.config as config
import libs.romconfig as romconfig


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
        Test for the load of a RomConfig from disk when the crc32 of the loaded rom is empty but the romconfig ini file
        has a ccrc32 defined.

        :return: Nothing.
        """
        # Preparation of a program config that will provide the path of the patches
        #--------------------------------------------------------------------------
        s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR, 'config', 'config-for_romconfig_testing_a.yaml')
        o_prog_cfg = config.ProgramCfg(ps_file=s_prog_cfg)

        # Preparation of the ROM to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Miniplanets (World) (Rev 3) (Aftermarket) (Unl).zip')
        o_rom = roms.Rom('mdr-crt', s_rom_file)

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(cons.s_TEST_DATA_DIR, 'romconfig',
                                        'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl).ini')
        o_config = romconfig.RomConfig()
        o_config.o_rom = o_rom

        self.assertRaises(ValueError, o_config.load_from_disk, s_romconfig_file, o_prog_cfg)

    def test_method_load_from_disk_with_rom_unmatched_ccrc32_b(self):
        """
        Test for the load of a RomConfig from disk when the crc32 of the loaded rom is populated but the romconfig ini
        file doesn't have the ccrc32 defined.

        :return: Nothing.
        """
        # Preparation of a program config that will provide the path of the patches
        #--------------------------------------------------------------------------
        s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR, 'config', 'config-for_romconfig_testing_a.yaml')
        o_prog_cfg = config.ProgramCfg(ps_file=s_prog_cfg)

        # Preparation of the ROM to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(cons.s_TEST_DATA_DIR, 'romconfig',
                                        'xxxxxxxx - phantom gear (world) (v0.2) (demo) (aftermarket) (unl).ini')
        o_config = romconfig.RomConfig()
        o_config.o_rom = o_rom

        self.assertRaises(ValueError, o_config.load_from_disk, s_romconfig_file, o_prog_cfg)

    def test_method_load_from_disk_with_no_rom_loaded(self):
        """
        Test for the case when a RomConfig is wanted to be loaded from a file but no Rom has been previously loaded in
        the RomConfig object.

        :return: Nothing.
        """
        # Preparation of a program config that will provide the path of the patches
        #--------------------------------------------------------------------------
        s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR, 'config', 'config-for_romconfig_testing_a.yaml')
        o_prog_cfg = config.ProgramCfg(ps_file=s_prog_cfg)

        # Trying to load the romconfig from a file
        #-----------------------------------------
        s_file = os.path.join(cons.s_TEST_DATA_DIR, 'romconfig',
                              'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl).ini')
        o_config = romconfig.RomConfig()
        self.assertRaises(ValueError, o_config.load_from_disk, s_file, o_prog_cfg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_no_patch(self):
        """
        Test for the load of a RomConfig from disk when the crc32 of the loaded rom and the romconfig ini match.

        :return: Nothing.
        """
        # Preparation of a program config that will provide the path of the patches
        #--------------------------------------------------------------------------
        s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR, 'config', 'config-for_romconfig_testing_a.yaml')
        o_prog_cfg = config.ProgramCfg(ps_file=s_prog_cfg)

        # Preparation of the ROM to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(cons.s_TEST_DATA_DIR, 'romconfig',
                                        'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl).ini')
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
        o_config = self._load_config_with_matched_ccrc32_and_patch()

        # Data loading
        #-------------
        o_core = cores.Core(os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'picodrive_libretro.so'))

        # Comparison
        #-----------
        o_expect = o_core
        o_actual = o_config.o_core

        s_msg = 'The core read from the romconfig is not what was expected'
        self.assertEqual(o_expect, o_actual, s_msg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_and_everything_defined__refresh_test(self):
        """
        When loading a fully defined romconfig file, is the refresh properly read?

        :return: Nothing.
        """
        o_config = self._load_config_with_matched_ccrc32_and_patch()

        # Data loading
        #-------------
        o_core = cores.Core(os.path.join(cons.s_TEST_DATA_DIR, 'cores', 'picodrive_libretro.so'))

        # Comparison
        #-----------
        f_expect = 60.0
        f_actual = o_config.f_refresh

        s_msg = 'The refresh read from the romconfig is not what was expected'
        self.assertEqual(f_expect, f_actual, s_msg)

    def test_method_load_from_disk_with_rom_matched_ccrc32_and_patch_not_found(self):
        """
        Test to load a RomConfig from disk with when the specified patch_file is not found in the current patches dir.
        :return: Nothing.
        """
        # Preparation of a program config that will provide the path of the patches
        #--------------------------------------------------------------------------
        s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR, 'config', 'config-for_romconfig_testing_a.yaml')
        o_prog_cfg = config.ProgramCfg(ps_file=s_prog_cfg)

        # Preparation of the ROM to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(cons.s_TEST_DATA_DIR, 'romconfig',
                                        'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl).ini')
        o_config = romconfig.RomConfig()
        o_config.o_rom = o_rom

        o_config.load_from_disk(ps_file=s_romconfig_file, po_prog_cfg=o_prog_cfg)

    def test_method_save_to_disk(self):

        # Preparing a ROM object
        #-----------------------
        s_rom_path = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'roms', 'mdr-ctr',
                                  'Miniplanets (World) (Rev 3) (Aftermarket) (Unl).zip')
        s_dat_path = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom('mdr-crt', s_rom_path)
        o_rom.populate_from_dat(s_dat_path)

        # Preparing a core object
        #------------------------
        s_cores_dir = os.path.join(cons.s_SCRIPT_ROOT, 'test', 'test_data', 'cores')
        to_cores = cores.get_cores(s_cores_dir, ['picodrive'])
        o_core = to_cores[0]

        # Creation of a sample RomConfig
        #-------------------------------
        o_rom_config = romconfig.RomConfig()
        o_rom_config.o_rom = o_rom
        o_rom_config.s_user = 'joe'
        o_rom_config.s_region = 'japan'
        o_rom_config.o_core = o_core
        o_rom_config.f_refresh = 60.0

        # Saving the RomConfig to disk
        #-----------------------------
        s_save_file = '/tmp/romconfig.foo'
        o_rom_config.save_to_disk(s_save_file)

        # Reading back the configuration file as a regular .ini file and making the comparison with the expected output
        #--------------------------------------------------------------------------------------------------------------
        o_now = datetime.datetime.now()

        o_actual_config = configparser.ConfigParser()
        o_actual_config.read(s_save_file)
        # I'll replace the date with tht current one, otherwise I won't be able to match it
        o_actual_config.set('meta', 'date', str(o_now))

        o_expect_config = configparser.ConfigParser()
        o_expect_config.add_section('meta')
        o_expect_config.set('meta', 'builder', cons.s_PRG)
        o_expect_config.set('meta', 'date', str(o_now))
        o_expect_config.set('meta', 'user', 'joe')
        o_expect_config.add_section('rom')
        o_expect_config.set('rom', 'ps_name', 'Miniplanets (World) (Rev 3) (Aftermarket) (Unl)')
        o_expect_config.set('rom', 'ccrc32', '8ea40d2f')
        o_expect_config.set('rom', 'platform', 'mdr-crt')
        o_expect_config.set('rom', 'patch_file', 'foo')
        o_expect_config.add_section('settings')
        o_expect_config.set('settings', 'core', 'picodrive')
        o_expect_config.set('settings', 'region', 'japan')
        o_expect_config.set('settings', 'refresh', '60.0')

        dds_actual = {}
        dds_expect = {}
        for s_section in set(o_actual_config.sections() + o_expect_config.sections()):
            dds_expect[s_section] = dict(o_expect_config[s_section])
            dds_actual[s_section] = dict(o_actual_config[s_section])

        self.assertEqual(dds_expect, dds_actual, 'The saved configuration doesn\'t contain the right information')

    @staticmethod
    def _load_config_with_matched_ccrc32_and_patch():
        """
        Method to fully load a romconfig matching the ROM ccrc32 and specifying a patch_file. This method is auxiliary for
        other test methods.

        :return:
        :rtype: romconfig.RomConfig
        """
        # Preparation of a program config that will provide the path of the patches
        #--------------------------------------------------------------------------
        s_prog_cfg = os.path.join(cons.s_TEST_DATA_DIR, 'config', 'config-for_romconfig_testing_a.yaml')
        o_prog_cfg = config.ProgramCfg(ps_file=s_prog_cfg)

        # Preparation of the ROM to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Creation of the RomConfig object
        #---------------------------------
        s_romconfig_file = os.path.join(
                               cons.s_TEST_DATA_DIR, 'romconfig',
                               'd6cf8cdb - phantom gear (world) (v0.2) (demo) (aftermarket) (unl) - with patch_file.ini')
        o_config = romconfig.RomConfig()
        o_config.o_rom = o_rom

        o_config.load_from_disk(ps_file=s_romconfig_file, po_prog_cfg=o_prog_cfg)
        return o_config


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
