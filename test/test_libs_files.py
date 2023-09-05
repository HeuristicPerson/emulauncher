import os
import shutil
import unittest

import libs.cons as cons
import libs.files as files

import test_tools


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
        s_out_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_out_dir)

        # Decompressing the file
        #-----------------------
        s_7z_file = os.path.join(test_tools.get_test_input_dir(self), 'patch_a.7z')

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
        s_out_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_out_dir)

        # Decompressing the file
        #-----------------------
        s_rar_file = os.path.join(test_tools.get_test_input_dir(self), 'patch_a.rar')
        files.uncompress(s_rar_file, ps_dst_dir=s_out_dir)

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
        s_out_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_out_dir)

        # Decompressing the file
        #-----------------------
        s_zip_file = os.path.join(test_tools.get_test_input_dir(self), 'patch_a.zip')
        files.uncompress(s_zip_file, ps_dst_dir=s_out_dir)

        # Getting the CRC32 of the decompressed file
        #-------------------------------------------
        s_expect = 'a0e6f70c'

        s_extracted_file = os.path.join(s_out_dir, 'patch_a.xdelta')
        s_actual = files.compute_crc(s_extracted_file)

        s_msg = 'The CRC32 of the extracted file is not what was expected.'
        self.assertEqual(s_expect, s_actual, s_msg)


class TestFunctionPatchFile(unittest.TestCase):
    def test_patch_xdelta3(self):
        """
        Test for xdelta3 patch_file format (.xdelta extension).

        :return: Nothing.
        """
        s_results_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_results_dir)

        s_src_file = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'file_a.txt')
        s_dst_file = os.path.join(s_results_dir, 'test_file.txt')

        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'patch_a_to_b.xdelta')

        shutil.copyfile(src=s_src_file, dst=s_dst_file)
        files.patch_file(ps_file=s_dst_file, ps_patch=s_patch)

        s_expect = 'modified file'
        with open(s_dst_file, 'r') as o_file:
            s_actual = o_file.read()

        s_msg = 'Patched file content is different from expectation.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_patch_ppf(self):
        """
        Test for ppf patch_file format (.ppf extension).

        :return: Nothing.
        """
        s_results_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_results_dir)

        s_src_file = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'file_a.txt')
        s_dst_file = os.path.join(s_results_dir, 'patched_file.txt')
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'patch_a_to_b.ppf')

        shutil.copyfile(src=s_src_file, dst=s_dst_file)
        files.patch_file(ps_file=s_dst_file, ps_patch=s_patch)  #, ps_result=s_dst_file)

        s_expect = 'modified file'
        with open(s_dst_file, 'r') as o_file:
            s_actual = o_file.read()

        s_msg = 'Patched file content is different from expectation.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_patch_bps(self):
        """
        Test for bps patch_file format (.bps extension).

        :return: Nothing.
        """
        s_results_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_results_dir)

        s_src_file = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'file_a.txt')
        s_dst_file = os.path.join(s_results_dir, 'patched_file.txt')
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'patch_a_to_b.bps')

        shutil.copyfile(src=s_src_file, dst=s_dst_file)
        files.patch_file(ps_file=s_dst_file, ps_patch=s_patch)

        s_expect = 'modified file'
        with open(s_dst_file, 'r') as o_file:
            s_actual = o_file.read()

        s_msg = 'Patched file content is different from expectation.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_patch_ips(self):
        """
        Test for ppf patch_file format (.ips extension).

        :return: Nothing.
        """
        s_results_dir = test_tools.get_test_output_dir(self)
        files.init_dir(s_results_dir)

        s_src_file = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'file_a.txt')
        s_dst_file = os.path.join(s_results_dir, 'patched_file.txt')
        s_patch = os.path.join(cons.s_TEST_DATA_DIR, 'patches', 'uncompressed', 'patch_a_to_b.ips')

        shutil.copyfile(src=s_src_file, dst=s_dst_file)
        files.patch_file(ps_file=s_dst_file, ps_patch=s_patch)

        s_expect = 'modified file'
        with open(s_dst_file, 'r') as o_file:
            s_actual = o_file.read()

        s_msg = 'Patched file content is different from expectation.'
        self.assertEqual(s_expect, s_actual, s_msg)


class TestFunctionIndexDir(unittest.TestCase):
    """
    Tests for the index_files function.
    """
    def test_full_tree(self):
        """
        Test for a tree fully populated.

        :return: Nothing.
        """
        s_dir = os.path.join(test_tools.get_test_input_dir(self), 'test_full_tree')

        dts_actual = files.index_dir(s_dir)

        # Relative paths
        dts_expect = {(0,):      'file_a.txt',
                      (1,):      'file_b.txt',
                      (0, 0):    'subdir_a/file_a_a.txt',
                      (0, 1):    'subdir_a/file_a_b.txt',
                      (1, 0):    'subdir_b/file_b_a.txt',
                      (1, 1):    'subdir_b/file_b_b.txt',
                      (1, 0, 0): 'subdir_b/subdir_c/file_b_c_a.txt'}

        # Making paths absolute
        for t_key in dts_expect.keys():
            s_new_value = os.path.join(s_dir, dts_expect[t_key])
            dts_expect[t_key] = s_new_value

        s_msg = 'The index of the directory differs from expectation.'
        self.assertEqual(dts_expect, dts_actual, s_msg)

    def test_ignoring_extension(self):
        """
        Test for a tree fully populated.

        :return: Nothing.
        """
        s_dir = os.path.join(test_tools.get_test_input_dir(self), 'test_full_ignoring_extension')
        dts_actual = files.index_dir(s_dir, pts_ignore_exts=('foo',))

        # Relative paths
        dts_expect = {(0,):      'file_a.txt',
                      (1,):      'file_b.txt',
                      (0, 0):    'subdir_a/file_a_a.txt',
                      (0, 1):    'subdir_a/file_a_b.txt',
                      (1, 0):    'subdir_b/file_b_a.txt',
                      (1, 1):    'subdir_b/file_b_b.txt',
                      (1, 0, 0): 'subdir_b/subdir_c/file_b_c_a.txt'}

        # Making paths absolute
        for t_key in dts_expect.keys():
            s_new_value = os.path.join(s_dir, dts_expect[t_key])
            dts_expect[t_key] = s_new_value

        s_msg = 'The index of the directory differs from expectation.'
        self.assertEqual(dts_expect, dts_actual, s_msg)


class TestFunctionIndexPatchDir(unittest.TestCase):
    """
    Tests for the index_patch_dir function.
    """
    def test_multi_disc_rom_directory(self):
        """
        Test for a multi-disc ROM directory.

        :return: Nothing.
        """
        s_input_dir = os.path.join(test_tools.get_test_input_dir(self), 'multi_patch_dir')

        # Actual result
        #--------------
        dtis_patch_dir_index_actual = files.index_patch_dir(s_input_dir)

        # Expected result
        #----------------
        # For convenience, just the file names...
        dtis_patch_dir_index_expect = {(0, 0): 'kdj flkaj lkj dlkfj dlkjf-0-0.xdelta',
                                       (0, 1): 'foo (this)-0-1.xdelta',
                                       (1, 0): '00000000-1-0.xdelta',
                                       (1, 1): '00000000-1-1.xdelta'}

        # ...then I make all paths absolute
        for ti_key, s_value in dtis_patch_dir_index_expect.items():
            dtis_patch_dir_index_expect[ti_key] = os.path.join(s_input_dir, s_value)

        s_msg = 'The index for a multi-patch directory differs from expectation.'
        self.assertEqual(dtis_patch_dir_index_expect, dtis_patch_dir_index_actual, s_msg)

    def test_single_disc_rom_directory(self):
        """
        Test for a single-part ROM directory
        :return:
        """
        # TODO:


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
