import os
import unittest

import libs.cons as cons
import libs.roms as roms


# Test cases
#=======================================================================================================================
class TestClassRom(unittest.TestCase):
    def test_initialization_non_existing_platform(self):
        self.assertRaises(KeyError, roms.Rom, 'foo-bar', '/tmp/foo.zip')

    def test_equality_true(self):
        """
        Equality test when two Rom instances point to the same Rom file
        :return: Nothing
        """
        # Preparation of the ROMs to be used
        # ----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom_a = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)
        o_rom_b = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        self.assertEqual(o_rom_a, o_rom_b)

    def test_equality_false_because_platform(self):
        """
        Equality test when two Rom instances point to different Rom files
        :return: Nothing.
        """
        # Preparation of the ROMs to be used
        # ----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom_a = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)
        o_rom_b = roms.Rom('snt-crt', s_rom_file, ps_dat=s_dat_file)

        self.assertNotEqual(o_rom_a, o_rom_b)

    def test_equality_false_because_ccrc32(self):
        """
        Equality test when two Rom instances point to different Rom files
        :return: Nothing.
        """
        # Preparation of the ROMs to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom_a = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)
        o_rom_b = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Manually tweaking the ccrc32 of one of the ROMs
        o_rom_b.s_ccrc32 = '00000000'

        self.assertNotEqual(o_rom_a, o_rom_b)

    def test_equality_false_because_dcrc32(self):
        """
        Equality test when two Rom instances point to different Rom files
        :return: Nothing.
        """
        # Preparation of the ROMs to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom_a = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)
        o_rom_b = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Manually tweaking the ccrc32 of one of the ROMs
        o_rom_b.s_dcrc32 = '00000000'

        print(o_rom_a)
        print(o_rom_b)

        self.assertNotEqual(o_rom_a, o_rom_b)

    def test_equality_false_because_csize(self):
        """
        Equality test when two Rom instances point to different Rom files
        :return: Nothing.
        """
        # Preparation of the ROMs to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom_a = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)
        o_rom_b = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Manually tweaking the ccrc32 of one of the ROMs
        o_rom_b.i_csize = 0

        print(o_rom_a)
        print(o_rom_b)

        self.assertNotEqual(o_rom_a, o_rom_b)

    def test_equality_false_because_dsize(self):
        """
        Equality test when two Rom instances point to different Rom files
        :return: Nothing.
        """
        # Preparation of the ROMs to be used
        #----------------------------------
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                                  'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
        s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
        o_rom_a = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)
        o_rom_b = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)

        # Manually tweaking the ccrc32 of one of the ROMs
        o_rom_b.i_dsize = 0

        print(o_rom_a)
        print(o_rom_b)

        self.assertNotEqual(o_rom_a, o_rom_b)

    # Attribute tests
    #----------------
    def test_attribute_s_ccrc32_safe_populated(self):
        """
        Method to test that a "safe" clean CRC32 is produced when a valid clean CRC32 is present in the Rom.
        :return: Nothing.
        """
        o_rom = _get_full_rom()

        s_expect = 'd6cf8cdb'
        s_actual = o_rom.s_ccrc32_safe
        s_msg = 'Safe clean CRC32 value not matching when a ROM contains a valid clean CRC32.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_attribute_s_ccrc32_safe_unpopulated(self):
        """
        Method to test that a "safe" clean CRC32 is produced when no valid clean CRC32 is present in the Rom.
        :return: Nothing.
        """
        o_rom = _get_incomplete_rom()
        s_expect = 'xxxxxxxx'
        s_actual = o_rom.s_ccrc32_safe
        s_msg = 'Safe clean CRC32 value not matching when a ROM does not contain a valid clean CRC32.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_attribute_s_dcrc32_safe_populated(self):
        """
        Method to test that a "safe" clean CRC32 is produced when a valid clean CRC32 is present in the Rom.
        :return: Nothing.
        """
        o_rom = _get_full_rom()
        s_expect = 'd6cf8cdb'
        s_actual = o_rom.s_dcrc32_safe
        s_msg = 'Safe dirty CRC32 value not matching when a ROM contains a valid clean CRC32.'
        self.assertEqual(s_expect, s_actual, s_msg)

    # Initialisation tests
    #---------------------
    def test_init_non_existing_file(self):
        s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt', 'Non existing.md')
        o_rom = roms.Rom('mdr-crt', s_rom_file)
        print(o_rom)
        self.assertEqual(True, False)

    # TODO: Test for non existing ROM file
    # TODO: Test for existing ROM file
    # TODO: Test for rom not included in dat
    # TODO: Test for rom included in dat


# Helping functions
#=======================================================================================================================
def _get_full_rom():
    """
    Function that returns a fully populated ROM (including .dat information).
    :return:
    :rtype: roms.Rom
    """
    s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                              'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl).zip')
    s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
    o_rom = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)
    return o_rom


def _get_incomplete_rom():
    """
    Function that returns a partially populated Rom object just including data from the file itself (so, not recognised
    by any .dat file).

    :return: A partially populated Rom object.
    :rtype: roms.Rom
    """
    s_rom_file = os.path.join(cons.s_TEST_DATA_DIR, 'roms', 'mdr-crt',
                              'Phantom Gear (World) (v0.2) (Demo) (Aftermarket) (Unl) - fake.zip')
    s_dat_file = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'mdr-crt.dat')
    o_rom = roms.Rom('mdr-crt', s_rom_file, ps_dat=s_dat_file)
    return o_rom


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
