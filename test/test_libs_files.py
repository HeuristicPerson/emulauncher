import os
import unittest

import libs.cons as cons
import libs.files as files


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
        s_out_dir = os.path.join(cons.s_TEST_DATA_OUT, __name__, 'test_uncompress_7z_file_valid')
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
        s_out_dir = os.path.join(cons.s_TEST_DATA_OUT, __name__, 'test_uncompress_rar_file_valid')
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
        s_out_dir = os.path.join(cons.s_TEST_DATA_OUT, __name__, 'test_uncompress_zip_file_valid')
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


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
