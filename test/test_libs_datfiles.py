"""
Unit tests for the dat_files library.
"""

import os
import unittest

from libs import cons
from libs import datfiles

# Constants
#=======================================================================================================================
# A short generic XML
s_DAT_XML_SHORT = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'dat-generic-xml-short.xml')
o_DAT_XML_SHORT = datfiles.Dat(s_DAT_XML_SHORT)

# This is a ClrMamePro dat
s_DAT_CLRMAMEPRO_SHORT = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'dat-clrmamepro-short.dat')
o_DAT_CLRMAMEPRO_SHORT = datfiles.Dat(s_DAT_CLRMAMEPRO_SHORT)

# This is a generic XML.
s_DAT_XML_GENERIC = os.path.join(cons.s_TEST_DATA_DIR, 'dats', 'ps1-partial-xmlgeneric.dat')
o_DAT_XML_GENERIC = datfiles.Dat(s_DAT_XML_GENERIC)


# Tests
#=======================================================================================================================
class TestsClassDat(unittest.TestCase):
    # Reading from generic XML dat
    #-----------------------------
    def test_method_read_from_dat__clrmamepro_s_author(self):
        """
        Test for reading .dat author from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        s_expect = 'redump.org'
        s_actual = o_dat.s_author

        s_msg = 'Generic XML author not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__clrmamepro_s_date(self):
        """
        Test for reading .dat author from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        s_expect = '2020-02-10 11-41-26'
        s_actual = o_dat.s_date

        s_msg = 'Generic XML date not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__clrmamepro_s_description(self):
        """
        Test for reading .dat description from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        s_expect = 'Sony - PlayStation - Discs (10201) (2020-02-10 11-41-26)'
        s_actual = o_dat.s_description

        s_msg = 'Generic XML description not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__clrmamepro_s_homepage(self):
        """
        Test for reading .dat homepage from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        s_expect = 'redump.org'
        s_actual = o_dat.s_homepage

        s_msg = 'Generic XML homepage not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__clrmamepro_s_name(self):
        """
        Test for reading .dat name from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        s_expect = 'Sony - PlayStation'
        s_actual = o_dat.s_name

        s_msg = 'Generic XML name not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__clrmamepro_i_romsets(self):
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        i_expect = 2
        i_actual = o_dat.i_romsets
        s_msg = 'The number of ROMsets found is not correct.'
        self.assertEqual(i_expect, i_actual, s_msg)

    def test_method_read_from_dat__clrmamepro_s_version(self):
        """
        Test for reading .dat name from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        s_expect = '2020-02-10 11-41-26'
        s_actual = o_dat.s_version

        s_msg = 'Generic XML version not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__clrmamepro_romset_data__romset_names(self):
        """
        Method to test that ROMset names read from a generic xml are what is expected.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        ls_expect_romset_names = ['Ace Combat 3 - Electrosphere (Europe) (En,Fr,De,Es,It)', 'Dino Crisis (USA)']
        ls_actual_romset_names = [o_romset.s_name for o_romset in o_dat]

        s_msg = 'ROMset names read from the file are not correct.'
        self.assertEqual(ls_expect_romset_names, ls_actual_romset_names, s_msg)

    def test_method_read_from_dat__clrmamepro_romset_data__romset_descs(self):
        """
        Method to test that ROMset descriptions read from a generic xml are what is expected.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        ls_expect_romset_descs = ['Ace Combat 3 - Electrosphere (Europe) (En,Fr,De,Es,It)', 'Dino Crisis (USA)']
        ls_actual_romset_descs = [o_romset.s_desc for o_romset in o_dat]

        s_msg = 'ROMset descriptions read from the file are not correct.'
        self.assertEqual(ls_expect_romset_descs, ls_actual_romset_descs, s_msg)

    def test_method_read_from_dat__clrmamepro_romset_data__rom_names(self):
        """
        Method to test rom names read from the generic xml are what was expected.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        ls_expect_rom_names = ['Ace Combat 3 - Electrosphere (Europe) (En,Fr,De,Es,It).cue',
                               'Ace Combat 3 - Electrosphere (Europe) (En,Fr,De,Es,It).bin',
                               'Dino Crisis (USA).cue',
                               'Dino Crisis (USA) (Track 1).bin',
                               'Dino Crisis (USA) (Track 2).bin']
        ls_actual_rom_names = [o_rom.s_name for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'ROM names read from the file are not correct.'
        self.assertEqual(ls_expect_rom_names, ls_actual_rom_names, s_msg)

    def test_method_read_from_dat__clrmamepro_romset_data__rom_sizes(self):
        """
        Method to test rom sizes are correctly read from a generic XML.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        li_expect_rom_sizes = [120, 470999760, 204, 379984416, 37396800]
        li_actual_rom_sizes = [o_rom.i_size for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'ROM sizes read from the file are not correct.'
        self.assertEqual(li_expect_rom_sizes, li_actual_rom_sizes, s_msg)

    def test_method_read_from_dat__clrmamepro_romset_data__rom_crc32(self):
        """
        Method to test that ROM CRC32 is correctly read from a generic XML file.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        ls_expect_rom_crc32 = ['92b3ff37', '91cad2df', 'd300424f', 'bd09f6d5', '7976083e']
        ls_actual_rom_crc32 = [o_rom.s_crc32 for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'ROM CRC32 not correctly read from the file.'
        self.assertEqual(ls_expect_rom_crc32, ls_actual_rom_crc32, s_msg)

    def test_method_read_from_dat__clrmamepro_romset_data__rom_md5(self):
        """
        Method to test ROM MD5 data is correctly read from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        # ClrMamePro dats don't support MD5, so the result will be empty.
        ls_expect_rom_md5 = ['',
                             '',
                             '',
                             '',
                             '']
        ls_actual_rom_md5 = [o_rom.s_md5 for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'MD5 data not correctly read from a generic XML file.'
        self.assertEqual(ls_expect_rom_md5, ls_actual_rom_md5, s_msg)

    def test_method_read_from_dat__clrmamepro_romset_data__rom_sha1(self):
        """
        Method to test all ROM SHA1 data is correctly read from a generic XML file.
        :return: Nothing.
        """
        o_dat = o_DAT_CLRMAMEPRO_SHORT
        ls_expect_rom_sha1 = ['5cc0e2d25792ae13ec7dab7b2ee8974c700c3337',
                              '8c215d983ad7d7f5f8aa122981cbd79d846532ec',
                              '6496a64bf92d4f6aca185d55e7214f877b3608bd',
                              '0f1dc456c40bd0839afd0c0947a71ebb4e16d836',
                              'd9f92af296360772e62caa4cb276de3fa74f5538']
        ls_actual_rom_sha1 = [o_rom.s_sha1 for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'ROM SHA1 data not correctly read from a genric XML file.'
        self.assertEqual(ls_expect_rom_sha1, ls_actual_rom_sha1, s_msg)

    # Reading from generic XML dat
    #-----------------------------
    def test_method_read_from_dat__generic_xml_s_author(self):
        """
        Test for reading .dat author from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_GENERIC
        s_expect = 'redump.org'
        s_actual = o_dat.s_author

        s_msg = 'Generic XML author not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__generic_xml_s_date(self):
        """
        Test for reading .dat author from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_GENERIC
        s_expect = '2020-02-10 11-41-26'
        s_actual = o_dat.s_date

        s_msg = 'Generic XML date not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__generic_xml_s_description(self):
        """
        Test for reading .dat description from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_GENERIC
        s_expect = 'Sony - PlayStation - Discs (10201) (2020-02-10 11-41-26)'
        s_actual = o_dat.s_description

        s_msg = 'Generic XML description not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__generic_xml_s_homepage(self):
        """
        Test for reading .dat homepage from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_GENERIC
        s_expect = 'redump.org'
        s_actual = o_dat.s_homepage

        s_msg = 'Generic XML homepage not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__generic_xml_s_name(self):
        """
        Test for reading .dat name from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_GENERIC
        s_expect = 'Sony - PlayStation'
        s_actual = o_dat.s_name

        s_msg = 'Generic XML name not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__generic_xml_i_romsets(self):
        o_dat = o_DAT_XML_GENERIC
        i_expect = 43
        i_actual = o_dat.i_romsets
        s_msg = 'The number of ROMsets found is not correct.'
        self.assertEqual(i_expect, i_actual, s_msg)

    def test_method_read_from_dat__generic_xml_s_version(self):
        """
        Test for reading .dat name from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_GENERIC
        s_expect = '2020-02-10 11-41-26'
        s_actual = o_dat.s_version

        s_msg = 'Generic XML version not read properly.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_method_read_from_dat__generic_xml_romset_data__romset_names(self):
        """
        Method to test that ROMset names read from a generic xml are what is expected.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_SHORT
        ls_expect_romset_names = ['Ace Combat 3 - Electrosphere (Europe) (En,Fr,De,Es,It)', 'Dino Crisis (USA)']
        ls_actual_romset_names = [o_romset.s_name for o_romset in o_dat]

        s_msg = 'ROMset names read from the file are not correct.'
        self.assertEqual(ls_expect_romset_names, ls_actual_romset_names, s_msg)

    def test_method_read_from_dat__generic_xml_romset_data__romset_descs(self):
        """
        Method to test that ROMset descriptions read from a generic xml are what is expected.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_SHORT
        ls_expect_romset_descs = ['Ace Combat 3 - Electrosphere (Europe) (En,Fr,De,Es,It)', 'Dino Crisis (USA)']
        ls_actual_romset_descs = [o_romset.s_desc for o_romset in o_dat]

        s_msg = 'ROMset descriptions read from the file are not correct.'
        self.assertEqual(ls_expect_romset_descs, ls_actual_romset_descs, s_msg)

    def test_method_read_from_dat__generic_xml_romset_data__rom_names(self):
        """
        Method to test rom names read from the generic xml are what was expected.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_SHORT
        ls_expect_rom_names = ['Ace Combat 3 - Electrosphere (Europe) (En,Fr,De,Es,It).cue',
                               'Ace Combat 3 - Electrosphere (Europe) (En,Fr,De,Es,It).bin',
                               'Dino Crisis (USA).cue',
                               'Dino Crisis (USA) (Track 1).bin',
                               'Dino Crisis (USA) (Track 2).bin']
        ls_actual_rom_names = [o_rom.s_name for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'ROM names read from the file are not correct.'
        self.assertEqual(ls_expect_rom_names, ls_actual_rom_names, s_msg)

    def test_method_read_from_dat__generic_xml_romset_data__rom_sizes(self):
        """
        Method to test rom sizes are correctly read from a generic XML.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_SHORT
        li_expect_rom_sizes = [120, 470999760, 204, 379984416, 37396800]
        li_actual_rom_sizes = [o_rom.i_size for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'ROM sizes read from the file are not correct.'
        self.assertEqual(li_expect_rom_sizes, li_actual_rom_sizes, s_msg)

    def test_method_read_from_dat__generic_xml_romset_data__rom_crc32(self):
        """
        Method to test that ROM CRC32 is correctly read from a generic XML file.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_SHORT
        ls_expect_rom_crc32 = ['92b3ff37', '91cad2df', 'd300424f', 'bd09f6d5', '7976083e']
        ls_actual_rom_crc32 = [o_rom.s_crc32 for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'ROM CRC32 not correctly read from the file.'
        self.assertEqual(ls_expect_rom_crc32, ls_actual_rom_crc32, s_msg)

    def test_method_read_from_dat__generic_xml_romset_data__rom_md5(self):
        """
        Method to test ROM MD5 data is correctly read from generic XML files.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_SHORT
        ls_expect_rom_md5 = ['56125070a7f679f547133512543a3585',
                             '24c2f5a5e43e4bc4c41081f5ef4dc818',
                             '149a0e24421d396746d696dafc5f459c',
                             '4990bb2a9e3374a234885ac983a9397a',
                             '2d7b5e8e94a91bf5423b2356f6a34863']
        ls_actual_rom_md5 = [o_rom.s_md5 for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'MD5 data not correctly read from a generic XML file.'
        self.assertEqual(ls_expect_rom_md5, ls_actual_rom_md5, s_msg)

    def test_method_read_from_dat__generic_xml_romset_data__rom_sha1(self):
        """
        Method to test all ROM SHA1 data is correctly read from a generic XML file.
        :return: Nothing.
        """
        o_dat = o_DAT_XML_SHORT
        ls_expect_rom_sha1 = ['5cc0e2d25792ae13ec7dab7b2ee8974c700c3337',
                              '8c215d983ad7d7f5f8aa122981cbd79d846532ec',
                              '6496a64bf92d4f6aca185d55e7214f877b3608bd',
                              '0f1dc456c40bd0839afd0c0947a71ebb4e16d836',
                              'd9f92af296360772e62caa4cb276de3fa74f5538']
        ls_actual_rom_sha1 = [o_rom.s_sha1 for o_romset in o_dat for o_rom in o_romset]

        s_msg = 'ROM SHA1 data not correctly read from a genric XML file.'
        self.assertEqual(ls_expect_rom_sha1, ls_actual_rom_sha1, s_msg)

    def test_get_linked_roms_tier_a(self):
        """
        Test to find linked ROMS where only the disc number is different. This is what I call tier-A.

        :return: Nothing.
        """
        o_dat = datfiles.Dat(s_DAT_XML_GENERIC)

        s_title = 'Tokimeki Memorial 2 (Japan) (Disc 3) (Rev 1)'
        lo_results = o_dat.get_linked_roms(s_title)

        ls_actual = sorted([o_result.s_name for o_result in lo_results])
        ls_expect = ['Tokimeki Memorial 2 (Japan) (Disc 1) (Rev 1)',
                     'Tokimeki Memorial 2 (Japan) (Disc 2) (Rev 1)',
                     'Tokimeki Memorial 2 (Japan) (Disc 4) (Rev 1)',
                     'Tokimeki Memorial 2 (Japan) (Disc 5) (Rev 1)']

        s_msg = 'The list of "tier-A" linked ROMs is not what was expected.'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_get_linked_roms_tier_b_case_a(self):
        """
        Test to find linked ROMS where only the disc number is different but also the bit after the disc number. This is
        what I call tier-B.

        :return: Nothing.
        """
        o_dat = datfiles.Dat(s_DAT_XML_GENERIC)

        s_title = 'Tomb Raider III - Adventures of Lara Croft (Asia) (Disc 1) (Japanese Version)'
        lo_results = o_dat.get_linked_roms(s_title)

        ls_actual = sorted([o_result.s_name for o_result in lo_results])
        ls_expect = ['Tomb Raider III - Adventures of Lara Croft (Asia) (Disc 2) (International Version)']

        s_msg = 'The list of "tier-A" linked ROMs is not what was expected.'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_get_linked_roms_tier_b_case_b(self):
        """
        Test to find linked ROMS where only the disc number is different but also the bit after the disc number. This is
        what I call tier-B.

        :return: Nothing.
        """
        o_dat = datfiles.Dat(s_DAT_XML_GENERIC)

        s_title = 'Strider Hiryuu 1 & 2 (Japan) (Disc 1) (Strider Hiryuu)'
        lo_results = o_dat.get_linked_roms(s_title)

        ls_actual = sorted([o_result.s_name for o_result in lo_results])
        ls_expect = ['Strider Hiryuu 1 & 2 (Japan) (Disc 2) (Strider Hiryuu 2)']

        s_msg = 'The list of "tier-A" linked ROMs is not what was expected.'
        self.assertEqual(ls_expect, ls_actual, s_msg)


# RomSet tests
#=======================================================================================================================
class TestClassRomSet(unittest.TestCase):
    def test_attribute_i_dirty_size(self):
        """
        Test for dirty size calculation using a "dirty" .cue ROM
        :return: Nothing.
        """
        o_rom_a = datfiles.Rom()
        o_rom_a.s_name = 'disc.cue'
        o_rom_a.i_size = 100

        o_rom_b = datfiles.Rom()
        o_rom_b.s_name = 'disc.bin'
        o_rom_b.i_size = 1000

        o_romset = datfiles.RomSet(ps_name='ROMset A', ps_description='ROMset A')
        o_romset.add_rom(o_rom_a)
        o_romset.add_rom(o_rom_b)

        i_expect = 1100
        i_actual = o_romset.i_dsize
        s_msg = 'The dirty size is not what was expected'
        self.assertEqual(i_expect, i_actual, s_msg)

    def test_attribute_i_clean_size__cue_skipping(self):
        """
        Test for dirty size calculation using a "dirty" .cue ROM
        :return: Nothing.
        """
        o_rom_a = datfiles.Rom()
        o_rom_a.s_name = 'disc.cue'
        o_rom_a.i_size = 100

        o_rom_b = datfiles.Rom()
        o_rom_b.s_name = 'disc.bin'
        o_rom_b.i_size = 1000

        o_romset = datfiles.RomSet(ps_name='ROMset A', ps_description='ROMset A')
        o_romset.add_rom(o_rom_a)
        o_romset.add_rom(o_rom_b)

        i_expect = 1000
        i_actual = o_romset.i_csize
        s_msg = 'The clean size is not what was expected'
        self.assertEqual(i_expect, i_actual, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
