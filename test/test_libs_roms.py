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


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
