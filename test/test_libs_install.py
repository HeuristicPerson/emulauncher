import os
import unittest

import libs.cons as cons
import libs.cores as cores
import libs.install as install
import libs.patches as patches
import libs.roms as roms
import libs.romconfig as romconfig
from libs.files import compute_crc


class FunctionInstall(unittest.TestCase):
    def test_rom_that_only_requires_decompressing(self):
        """
        Installation test for a ROM that only requires to be decompressed.

        :return: Nothing.
        """
        s_out_dir = os.path.join(cons.s_TEST_DATA_OUT, __name__, 'test_rom_that_only_requires_decompressing')

        o_rom_cfg = _build_rom_config_single_file()
        o_rom_cfg.s_user = 'anna'

        install.install(po_rom_cfg=o_rom_cfg,
                        ps_dir=s_out_dir)

        ds_expect = {'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).md': 'd6cf8cdb'}

        ds_actual = {}
        for s_elem in os.listdir(s_out_dir):
            s_full_path = os.path.join(s_out_dir, s_elem)
            if os.path.isfile(s_full_path):
                ds_actual[s_elem] = compute_crc(s_full_path)

        s_msg = 'The file(s) contained in the install dir is not what was expected.'
        self.assertEqual(ds_expect, ds_actual, s_msg)

    def test_rom_with_several_discs(self):
        s_out_dir = os.path.join(cons.s_TEST_DATA_OUT, __name__, 'test_rom_with_several_discs')
        o_rom_cfg = _build_rom_config_multiple_files()
        o_rom_cfg.s_user = 'jonh'

        install.install(po_rom_cfg=o_rom_cfg,
                        ps_dir=s_out_dir)
        self.assertEqual(True, False)

    def test_rom_with_patch(self):
        """
        Installation test for a small ROM that requires a patch to be applied.

        :return: Nothing.
        """
        s_out_dir = os.path.join(cons.s_TEST_DATA_OUT, __name__, 'test_rom_with_patch_required')

        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'mdr-crt', 'd6cf8cdb - v0.2 to v0.9.zip')
        o_patch = patches.Patch(ps_file=s_patch)

        o_rom_cfg = _build_rom_config_single_file()
        o_rom_cfg.s_user = 'anna'
        o_rom_cfg.o_patch = o_patch

        install.install(po_rom_cfg=o_rom_cfg,
                        ps_dir=s_out_dir)

        # If the patching is correct, we will obtain the original ROM ps_name (because patching won't change the ps_name at
        # all) with the CRC32 of the v0.9 because that's the intent of the applied patch.
        ds_expect = {'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).md': '3df43d25'}

        ds_actual = {}
        for s_elem in os.listdir(s_out_dir):
            s_full_path = os.path.join(s_out_dir, s_elem)
            if os.path.isfile(s_full_path):
                ds_actual[s_elem] = compute_crc(s_full_path)

        s_msg = 'The file(s) contained in the install dir is not what was expected.'
        self.assertEqual(ds_expect, ds_actual, s_msg)


# Helper functions
#=======================================================================================================================
def _build_rom_config_single_file():
    """
    Function to obtain a valid RomConfig for a small ROM without user or patch.
    :return:
    """
    # "Creating" a a ROM object
    # --------------------------
    s_rom = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                         'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
    o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom)
    o_rom_cfg = romconfig.generate_default_cfg(po_rom=o_rom, pto_cores_available=())
    return o_rom_cfg


def _build_rom_config_multiple_files():
    """
    Function to obtain a valid RomConfig for a small ROM without user or patch.
    :return:
    """
    # "Creating" a a ROM object
    #--------------------------
    s_rom_1st = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'ps1',
                             'Strider Hiryuu 1 & 2 (Japan) (Disc 1) (Strider Hiryuu).zip')
    s_rom_2nd = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'ps1',
                             'Strider Hiryuu 1 & 2 (Japan) (Disc 2) (Strider Hiryuu 2).zip')
    o_rom = roms.Rom(ps_platform='mdr-crt', ps_path=s_rom_1st)

    # We have to manually add the linked ROM because normally it's added through a .dat, and I don't want to include
    # that extra dependency and complication in this test function.
    o_rom._ls_linked_roms = [s_rom_2nd]
    o_rom_cfg = romconfig.generate_default_cfg(po_rom=o_rom, pto_cores_available=())
    return o_rom_cfg



# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
