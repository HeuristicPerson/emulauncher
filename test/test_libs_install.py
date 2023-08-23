import contextlib
import io
import os
import shutil
#import sys
import unittest

import libs.cons as cons
import libs.install as install
import libs.patches as patches
import libs.roms as roms
import libs.romconfig as romconfig
import libs.files as files

import test_tools


# Tests
#=======================================================================================================================
class FunctionInstall(unittest.TestCase):
    def test_single_rom_without_patch(self):
        """
        Installation test for a ROM that only requires to be decompressed.

        :return: Nothing.
        """
        s_out_dir = os.path.join(cons.s_TEST_DATA_OUT, __name__, 'test_single_rom_without_patch')

        o_rom_cfg = self._build_rom_config_single_file()
        o_rom_cfg.s_user = 'anna'

        install.install(po_rom_cfg=o_rom_cfg, ps_dir=s_out_dir)

        ds_expect = {'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).md': 'd6cf8cdb'}

        ds_actual = {}
        for s_elem in os.listdir(s_out_dir):
            s_full_path = os.path.join(s_out_dir, s_elem)
            if os.path.isfile(s_full_path):
                ds_actual[s_elem] = files.compute_crc(s_full_path)

        s_msg = 'The content of install dir differs from expectation.'
        self.assertEqual(ds_expect, ds_actual, s_msg)

    def test_single_rom_without_patch__with_printing(self):
        """
        Installation test for a ROM that only requires to be decompressed.

        :return: Nothing.
        """
        s_out_dir = os.path.join(cons.s_TEST_DATA_OUT, __name__, 'test_single_rom_without_patch')

        o_rom_cfg = self._build_rom_config_single_file()
        o_rom_cfg.s_user = 'anna'

        # Creating a StringIO object that will receive stdout
        o_captured_output = io.StringIO()  # Create StringIO object

        # Redirecting stdout to the StringIO object
        with contextlib.redirect_stdout(o_captured_output):
            install.install(po_rom_cfg=o_rom_cfg, ps_dir=s_out_dir, pb_print=True)

        print(f'Captured: {o_captured_output.getvalue()}')

        s_msg = 'The content of install dir differs from expectation.'
        self.assertEqual(True, False, s_msg)

    def test_linked_roms_without_patch(self):
        """
        Install test for multi-file ROMs (e.g. multi-disc games of Playstation) without patches. Each of the two ROMs
        should be installed in "disc 1", and "disc 2" sub-folders.

        :return: Nothing.
        """
        s_out_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_out_dir)

        o_rom_cfg = self._build_rom_config_multiple_files()

        install.install(po_rom_cfg=o_rom_cfg, ps_dir=s_out_dir)

        ls_actual_files = []
        for s_dir, ls_dirs, ls_files in os.walk(s_out_dir):
            for s_file in ls_files:
                s_full_path = os.path.join(s_dir, s_file)
                ls_actual_files.append(s_full_path)
        ls_actual_files.sort()

        ls_expect_files = [os.path.join(s_out_dir, 'disc 1',
                                        'Strider Hiryuu 1 & 2 (Japan) (Disc 1) (Strider Hiryuu).bin'),
                           os.path.join(s_out_dir, 'disc 1',
                                        'Strider Hiryuu 1 & 2 (Japan) (Disc 1) (Strider Hiryuu).cue'),
                           os.path.join(s_out_dir, 'disc 2',
                                        'Strider Hiryuu 1 & 2 (Japan) (Disc 2) (Strider Hiryuu 2).bin'),
                           os.path.join(s_out_dir, 'disc 2',
                                        'Strider Hiryuu 1 & 2 (Japan) (Disc 2) (Strider Hiryuu 2).cue')
                           ]

        s_msg = 'Installed files for multi-disc game are different from expectation.'
        self.assertEqual(ls_expect_files, ls_actual_files, s_msg)

    def test_single_rom_with_patch(self):
        """
        Installation test for a small ROM that requires a patch_file to be applied.

        :return: Nothing.
        """
        s_out_dir = test_tools.get_test_output_dir(self)

        s_patch = os.path.join(test_tools.get_test_input_dir(self), 'mdr-crt-phantom_gear',
                               'd6cf8cdb - v0.2 to v0.9.zip')
        o_patch = patches.Patch(ps_file=s_patch)

        o_rom_cfg = self._build_rom_config_single_file()
        o_rom_cfg.s_user = 'anna'
        o_rom_cfg.o_patch = o_patch

        install.install(po_rom_cfg=o_rom_cfg, ps_dir=s_out_dir, pb_print=False)

        # If the patching is correct, we will obtain the original ROM name (because patching won't change the name at
        # all) with the CRC32 of the v0.9 because that's the intent of the applied patch_file.
        ds_expect = {'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).md': '3df43d25'}

        ds_actual = {}
        for s_elem in os.listdir(s_out_dir):
            s_full_path = os.path.join(s_out_dir, s_elem)
            if os.path.isfile(s_full_path):
                ds_actual[s_elem] = files.compute_crc(s_full_path)

        s_msg = 'The file(s) contained in the install dir is not what was expected.'
        self.assertEqual(ds_expect, ds_actual, s_msg)

    def test_single_rom_with_patch__with_printing(self):
        """
        Installation printing test for a small ROM that requires a patch_file to be applied. The code of this test must
        be equivalent to the no-printing test but here we will only test that the printed output is correct.

        :return: Nothing.
        """
        s_out_dir = test_tools.get_test_output_dir(self)

        s_patch = os.path.join(test_tools.get_test_input_dir(self), 'mdr-crt-phantom_gear',
                               'd6cf8cdb - v0.2 to v0.9.zip')
        o_patch = patches.Patch(ps_file=s_patch)

        o_rom_cfg = self._build_rom_config_single_file()
        o_rom_cfg.s_user = 'anna'
        o_rom_cfg.o_patch = o_patch

        # Creating a StringIO object that will receive stdout
        o_captured_output = io.StringIO()  # Create StringIO object

        # Redirecting stdout to the StringIO object
        with contextlib.redirect_stdout(o_captured_output):
            install.install(po_rom_cfg=o_rom_cfg, ps_dir=s_out_dir, pb_print=True)

        print(f'Captured: {o_captured_output.getvalue()}')

        s_msg = 'The file(s) contained in the install dir is not what was expected.'
        self.assertEqual(True, False, s_msg)

    def test_linked_roms_with_patch(self):
        """
        Test for the installation and patching of a multi-disc ROMset.

        :return: Nothing.
        """
        # "Creating" a ROM object
        #------------------------
        s_rom_1st = os.path.join(test_tools.get_test_input_dir(self), 'fake-multi_disc', 'game+patch',
                                 'game x - disc 1 of 2.zip')
        s_rom_2nd = os.path.join(test_tools.get_test_input_dir(self), 'fake-multi_disc', 'game+patch',
                                 'game x - disc 2 of 2')

        # The platform itself is not relevant for this test, so I'll use Playstation 1 (ps1) because it's already
        # contained in the program default platforms file.
        o_rom = roms.Rom(ps_platform='ps1', ps_path=s_rom_1st)

        # We have to manually add the linked ROM because normally it's added through a .dat, and I don't want to include
        # that extra dependency and complication in this test function.
        o_rom._ls_linked_roms = [s_rom_2nd]

        # Creating a patch object
        #------------------------
        s_patch = os.path.join(test_tools.get_test_input_dir(self), 'fake-multi_disc', 'game+patch',
                               '00000000 - my patch.zip')
        o_patch = patches.Patch(s_patch)

        # Creating a RomConfig object with all the data
        #----------------------------------------------
        o_rom_cfg = romconfig.generate_default_cfg(po_rom=o_rom, pto_cores_available=())
        o_rom_cfg.o_patch = o_patch

        # Creating output directory
        #--------------------------
        s_install_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_install_dir)

        # Finally we can install the game
        #--------------------------------
        install.install(po_rom_cfg=o_rom_cfg, ps_dir=s_install_dir)

        s_expect_dir = os.path.join(test_tools.get_test_input_dir(self), 'fake-multi_disc', 'mod_game')
        b_equal = test_tools.are_dirs_same(s_install_dir, s_expect_dir)

        s_msg = 'Installed+patched dir is different from expectation.'
        self.assertTrue(b_equal, s_msg)

    def _build_rom_config_single_file(self):
        """
        Function to obtain a valid RomConfig for a small ROM without user or patch_file.
        :return:
        """
        # "Creating" a a ROM object
        #--------------------------
        s_rom = os.path.join(test_tools.get_test_input_dir(self), 'mdr-crt-phantom_gear',
                             'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom)
        o_rom_cfg = romconfig.generate_default_cfg(po_rom=o_rom, pto_cores_available=())
        return o_rom_cfg

    def _build_rom_config_multiple_files(self):
        """
        Function to obtain a valid RomConfig for a small ROM without user or patch_file.
        :return:
        """
        # "Creating" a a ROM object
        #--------------------------
        # Notice the first ROM is "real" file, so it has extension...
        s_rom_1st = os.path.join(test_tools.get_test_input_dir(self), 'ps1-strider_hiryuu_2',
                                 'Strider Hiryuu 1 & 2 (Japan) (Disc 1) (Strider Hiryuu).zip')
        #...while the second one (which is read from a .dat file in a real case), doesn't have extension because it'll
        # assume the same extension as the main ROM.
        s_rom_2nd = os.path.join(test_tools.get_test_input_dir(self), 'ps1-strider_hiryuu_2',
                                 'Strider Hiryuu 1 & 2 (Japan) (Disc 2) (Strider Hiryuu 2)')

        o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom_1st)

        # We have to manually add the linked ROM because normally it's added through a .dat, and I don't want to include
        # that extra dependency and complication in this test function.
        o_rom._ls_linked_roms = [s_rom_2nd]
        o_rom_cfg = romconfig.generate_default_cfg(po_rom=o_rom, pto_cores_available=())

        return o_rom_cfg


# Skipped because the function probably needs to be removed
@unittest.skip
class FunctionPatchDir(unittest.TestCase):
    """
    Tests for the patch_dir function.
    """
    def test_single_file_rom(self):
        self.assertEqual(True, False)

    def test_multi_file_rom(self):
        """
        Test for the patching of a multi-disc rom directory.

        :return: Nothing.
        """

        # The patcher works in-place, so we have to create a copy of the test data
        #-------------------------------------------------------------------------
        s_rom_src_dir = os.path.join(test_tools.get_test_input_dir(self), 'multi_rom', 'raw_game')
        s_rom_dst_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_rom_dst_dir)
        shutil.copytree(s_rom_src_dir, s_rom_dst_dir, dirs_exist_ok=True)

        s_patch_dir = os.path.join(test_tools.get_test_input_dir(self), 'multi_rom', 'patch')

        install.patch_dir(ps_dir=s_rom_src_dir, ps_patch=s_patch_dir)

        self.assertEqual(True, False)


# Helper functions
#=======================================================================================================================



# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
