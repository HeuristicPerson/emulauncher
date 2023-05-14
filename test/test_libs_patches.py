import os
import unittest

import libs.cons as cons
import libs.patches as patches
import libs.roms as roms


# Test cases
#=======================================================================================================================
class TestClassPatch(unittest.TestCase):
    def test_method_init_from_valid_file(self):
        """
        Test for the initialization from a valid file.
        :return: Nothing.
        """
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'e01fa526 - double x hack.zip')
        o_patch = patches.Patch(s_patch)

        ls_expect = []
        ls_actual = []

        ls_actual.append(o_patch.s_ccrc32)
        ls_expect.append('e01fa526')

        ls_actual.append(o_patch.s_title)
        ls_expect.append('double x hack')

        s_msg = 'The information read from the patch file is not correct.'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_method_init_from_file_with_invalid_crc32(self):
        """
        Test for the initialization using a file that doesn't have a valid CRC32 in the file name.
        :return: Nothing.
        """
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'foo.bar')
        self.assertRaises(ValueError, patches.Patch, s_patch)

    def test_method_init_from_file_with_no_description(self):
        """
        Test for the initialization using a file that doesn't have a valid description in the file name.
        :return: Nothing.
        """
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'aaaaaaaa.bar')
        self.assertRaises(ValueError, patches.Patch, s_patch)


class TestFunctionGetPatches(unittest.TestCase):
    """
    Tests for the function to get patches for certain rom.
    """
    def test_valid_dir_and_valid_rom_with_two_results(self):
        """
        Method to test the function when valid inputs are given and two results are expected.
        :return: Nothing.
        """
        # Building the Rom object that will be used to query for compatible patches
        #--------------------------------------------------------------------------
        s_rom = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                             'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom('mdr-crt', s_rom, s_dat)

        # Querying compatible patches
        #----------------------------
        ps_patches_dir = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'mdr-crt')
        lo_patches = patches.get_patches(ps_patches_dir, o_rom)

        # Comparison of result and expectation
        #-------------------------------------
        lts_expect = sorted([('d6cf8cdb', 'v0.2 to v0.9'),
                             ('d6cf8cdb', 'v0.2 to v0.9 (bis)')])
        lts_actual = sorted([(o_patch.s_ccrc32, o_patch.s_title) for o_patch in lo_patches])

        s_msg = 'Found patches for ROM are different from the expected ones'
        self.assertEqual(lts_expect, lts_actual, s_msg)

    def test_valid_dir_and_valid_rom_with_no_results(self):
        """
        Method to test the function a no patches are found for a given Rom.
        :return: Nothing.
        """
        # Building the Rom object that will be used to query for compatible patches
        #--------------------------------------------------------------------------
        s_rom = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt', 'Phelios (Japan) (Virtual Console).zip')
        s_dat = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom = roms.Rom('mdr-crt', s_rom, s_dat)

        # Querying compatible patches
        #----------------------------
        ps_patches_dir = os.path.join(cons.s_TEST_DATA_DIR, 'patches')
        lo_patches = patches.get_patches(ps_patches_dir, o_rom)

        # Comparison of result and expectation
        #-------------------------------------
        lo_expect = []
        lo_actual = lo_patches

        s_msg = 'Expected number of patches differs from the actual result.'
        self.assertEqual(lo_expect, lo_actual, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
