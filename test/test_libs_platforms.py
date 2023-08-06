import os
import unittest

import libs.cons as cons
import libs.platforms as platforms


# Constants
#=======================================================================================================================
_u_PLATFORMS_SINGLE_VALID = os.path.join(cons.s_TEST_DATA_DIR, 'platforms', 'platforms_single_valid.yaml')


# Tests for functions
#=======================================================================================================================
class TestFunctionReadPlatformsFile(unittest.TestCase):
    """
    Tests for the
    """
    def test_file_with_single_platform(self):
        """
        Test to read a .json file with a single platform definition inside.
        :return: Nothing
        """
        do_platforms = platforms.read_platforms_file(_u_PLATFORMS_SINGLE_VALID)

        s_first_key = sorted(do_platforms.keys())[0]
        o_platform = do_platforms[s_first_key]

        # I'll simply check the values read from the json file are what we expected
        tx_expected = []
        tx_actual = []

        tx_actual.append(o_platform.s_alias)
        tx_expected.append('mdr-crt')

        tx_actual.append(o_platform.s_name)
        tx_expected.append('Megadrive (cartridge)')

        tx_actual.append(o_platform.f_aspect)
        tx_expected.append(1.333333)

        tx_actual.append(o_platform.lf_freqs)
        tx_expected.append([60.0, 60.0, 50.0])

        tx_actual.append(o_platform.ls_region_pats)
        tx_expected.append(['[\\(,\\s](usa|world)[\\),]',
                            '[\\(,\\s](japan)[\\),]',
                            '[\\(,\\s](europe|spain|sweden)[\\),]'])

        tx_actual.append(o_platform.ls_cores)
        tx_expected.append(["genesis_plus_gx",
                            "genesis_plus_gx_wide",
                            "picodrive",
                            "smsplus"])

        s_msg = 'Values read from .json file are different from what was expected.'
        self.assertEqual(tx_expected, tx_actual, s_msg)


# Test for classes
#=======================================================================================================================
class TestClassPlatform(unittest.TestCase):
    def test_get_frequency_for_rom_2ops_1st_match(self):
        """
        Test to get the frequency for a ROM with two frequencies when we should get the 1st one.
        :return: Nothing
        """
        # Creating a ROM file (just the path), and a Platform object
        #-----------------------------------------------------------
        u_rom = os.path.join('/foo', 'bar',
                             'Battle Squadron (USA, Europe) (Rev 1) (Beta) (1991-01-18) (Sega Channel).zip')

        do_platforms = platforms.read_platforms_file(_u_PLATFORMS_SINGLE_VALID)
        o_platform = do_platforms['mdr-crt']

        # Testing the ROM gets the 1st frequency
        #---------------------------------------
        f_actual_result = o_platform.get_frequency_for_rom(u_rom)
        f_expected_result = 60.0

        s_msg = 'Not able to get the correct 1st frequency when two available'
        self.assertEqual(f_actual_result, f_expected_result, s_msg)

    def test_get_frequency_for_rom_2ops_2nd_match(self):
        """
        Test to get the frequency for a ROM with two frequencies when we should get the 2nd one.

        :return: Nothing
        """
        # Creating a ROM file (just the path), and a Platform object
        #-----------------------------------------------------------
        u_rom = os.path.join('Sonic 3 (Europe).zip')

        do_platforms = platforms.read_platforms_file(_u_PLATFORMS_SINGLE_VALID)
        o_platform = do_platforms['mdr-crt']

        # Testing the ROM gets the 1st frequency
        #---------------------------------------
        f_actual_result = o_platform.get_frequency_for_rom(u_rom)
        f_expected_result = 50.0

        s_msg = 'Not able to get the correct 2nd frequency when two available'
        self.assertEqual(f_expected_result, f_actual_result, s_msg)

    def test_get_frequency_for_rom_2ops_no_match(self):
        """
        Test to get the frequency for a ROM with two frequencies when we should get the 1st one.
        :return: Nothing
        """
        # Creating a ROM file (just the path), and a Platform object
        #-----------------------------------------------------------
        u_rom = os.path.join('Sonic 3.zip')

        do_platforms = platforms.read_platforms_file(_u_PLATFORMS_SINGLE_VALID)
        o_platform = do_platforms['mdr-crt']

        # Testing the ROM gets the 1st frequency
        #---------------------------------------
        f_actual_result = o_platform.get_frequency_for_rom(u_rom)
        f_expected_result = 60.0

        s_msg = 'Not able to get the default frequency when no match available'
        self.assertEqual(f_actual_result, f_expected_result, s_msg)

    def test_foo(self):
        do_platforms = platforms.read_platforms_file(_u_PLATFORMS_SINGLE_VALID)
        o_platform = do_platforms['mdr-crt']
        print(o_platform)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
