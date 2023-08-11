import os
import shutil
import unittest
import sys

import libs.cons as cons
import libs.files as files

import tools


# Tests
#=======================================================================================================================
class TestFunctionUncompress(unittest.TestCase):
    def test_uncompress_7z_file_valid(self):
        """
        Decompression test for a valid 7z file.

        :return: Nothing.
        """
        # Creating a directory for the output data
        #-----------------------------------------
        s_out_dir = tools.get_test_folder(self)
        files.init_dir(s_out_dir)

        # Decompressing the file
        #-----------------------
        s_7z_file = os.path.join(cons.s_TEST_DATA_DIR, 'compressed_data', 'patch_a.7z')
        files.uncompress(s_7z_file, ps_dst_dir=s_out_dir)

        # Getting the CRC32 of the decompressed file
        #-------------------------------------------
        s_expect = 'a0e6f70c'

        s_extracted_file = os.path.join(s_out_dir, 'patch_a.xdelta')
        s_actual = files.compute_crc(s_extracted_file)

        s_msg = 'The CRC32 of the extracted file is not what was expected.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_uncompress_rar_file_valid(self):
        """
        Decompression test for a valid rar file.

        :return: Nothing.
        """
        # Creating a directory for the output data
        #-----------------------------------------
        s_out_dir = tools.get_test_folder(self)
        files.init_dir(s_out_dir)

        # Decompressing the file
        #-----------------------
        s_7z_file = os.path.join(cons.s_TEST_DATA_DIR, 'compressed_data', 'patch_a.rar')
        files.uncompress(s_7z_file, ps_dst_dir=s_out_dir)

        # Getting the CRC32 of the decompressed file
        #-------------------------------------------
        s_expect = 'a0e6f70c'

        s_extracted_file = os.path.join(s_out_dir, 'patch_a.xdelta')
        s_actual = files.compute_crc(s_extracted_file)

        s_msg = 'The CRC32 of the extracted file is not what was expected.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_uncompress_zip_file_valid(self):
        """
        Decompression test for a valid zip file.

        :return: Nothing.
        """
        # Creating a directory for the output data
        #-----------------------------------------
        s_out_dir = tools.get_test_folder(self)
        files.init_dir(s_out_dir)

        # Decompressing the file
        #-----------------------
        s_zip_file = os.path.join(cons.s_TEST_DATA_DIR, 'compressed_data', 'patch_a.zip')
        files.uncompress(s_zip_file, ps_dst_dir=s_out_dir)

        # Getting the CRC32 of the decompressed file
        #-------------------------------------------
        s_expect = 'a0e6f70c'

        s_extracted_file = os.path.join(s_out_dir, 'patch_a.xdelta')
        s_actual = files.compute_crc(s_extracted_file)

        s_msg = 'The CRC32 of the extracted file is not what was expected.'
        self.assertEqual(s_expect, s_actual, s_msg)


class TestFunctionPatch(unittest.TestCase):
    def test_patch_xdelta3(self):
        """
        Test for xdelta3 patch format (.xdelta extension).

        :return: Nothing.
        """
        s_results_dir = tools.get_test_folder(self)
        files.init_dir(s_results_dir)

        s_src_file = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'file_a.txt')
        s_dst_file = os.path.join(s_results_dir, 'test_file.txt')

        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'patch_a_to_b.xdelta')

        shutil.copyfile(src=s_src_file, dst=s_dst_file)
        files.patch(ps_file=s_dst_file, ps_patch=s_patch)

        s_expect = 'modified file'
        with open(s_dst_file, 'r') as o_file:
            s_actual = o_file.read()

        s_msg = 'Patched file content is different from expectation.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_patch_ppf(self):
        """
        Test for ppf patch format (.ppf extension).

        :return: Nothing.
        """
        s_results_dir = tools.get_test_folder(self)
        files.init_dir(s_results_dir)

        s_src_file = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'file_a.txt')
        s_dst_file = os.path.join(s_results_dir, 'patched_file.txt')
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'patch_a_to_b.ppf')

        shutil.copyfile(src=s_src_file, dst=s_dst_file)
        files.patch(ps_file=s_dst_file, ps_patch=s_patch)  #, ps_result=s_dst_file)

        s_expect = 'modified file'
        with open(s_dst_file, 'r') as o_file:
            s_actual = o_file.read()

        s_msg = 'Patched file content is different from expectation.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_patch_bps(self):
        """
        Test for bps patch format (.bps extension).

        :return: Nothing.
        """
        s_results_dir = tools.get_test_folder(self)
        files.init_dir(s_results_dir)

        s_src_file = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'file_a.txt')
        s_dst_file = os.path.join(s_results_dir, 'patched_file.txt')
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'patch_a_to_b.bps')

        shutil.copyfile(src=s_src_file, dst=s_dst_file)
        files.patch(ps_file=s_dst_file, ps_patch=s_patch)

        s_expect = 'modified file'
        with open(s_dst_file, 'r') as o_file:
            s_actual = o_file.read()

        s_msg = 'Patched file content is different from expectation.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_patch_ips(self):
        """
        Test for ppf patch format (.ips extension).

        :return: Nothing.
        """
        s_results_dir = tools.get_test_folder(self)
        files.init_dir(s_results_dir)

        s_src_file = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'file_a.txt')
        s_dst_file = os.path.join(s_results_dir, 'patched_file.txt')
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'patch_a_to_b.ips')

        shutil.copyfile(src=s_src_file, dst=s_dst_file)
        files.patch(ps_file=s_dst_file, ps_patch=s_patch)

        s_expect = 'modified file'
        with open(s_dst_file, 'r') as o_file:
            s_actual = o_file.read()

        s_msg = 'Patched file content is different from expectation.'
        self.assertEqual(s_expect, s_actual, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
