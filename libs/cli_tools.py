"""
Library to work or interface with common command line tools of the system.
"""

import os.path
from shutil import which
import subprocess
import zipfile


# Main functions
#=======================================================================================================================
def is_tool_installed(ps_name):
    """
    Check whether `ps_name` is on PATH and marked as executable.

    :param ps_name:
    :type ps_name: Str

    :return:
    :rtype: Bool
    """

    return which(ps_name) is not None


def uncompress(ps_file, ps_dst_dir=''):
    """
    Function to uncompress files.

    :param ps_file: Path of the file we want to decompress.
    :type ps_file: Str

    :param ps_dst_dir: Path of the dir where the uncompressed data will be placed.
    :type ps_dst_dir: Str

    :return: Nothing.
    """
    s_file = os.path.basename(ps_file)
    s_name, _, s_ext = s_file.rpartition('.')

    s_ext = s_ext.lower()
    dsc_decompressors = {'7z': _uncompress_7z, 'rar': _uncompress_rar, 'zip': _uncompress_zip}

    if s_ext in dsc_decompressors:
        c_decompressor = dsc_decompressors[s_ext]
        c_decompressor(ps_file=ps_file, ps_dst_dir=ps_dst_dir)


def _uncompress_7z(ps_file, ps_dst_dir=''):
    """
    Function to uncompress 7z files.

    :param ps_file: Path of the file we want to decompress.
    :type ps_file: Str

    :param ps_dst_dir: Path of the dir where the uncompressed data will be placed.
    :type ps_dst_dir: Str

    :return: Nothing.
    """
    ls_cmd = ['7z', 'x', ps_file]

    if ps_dst_dir:
        ls_cmd += [f'-o{ps_dst_dir}']

    o_process = subprocess.Popen(ls_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_stdout, s_stderr = o_process.communicate()

    # TODO: Handle error messages


def _uncompress_rar(ps_file, ps_dst_dir=''):
    """
    Function to uncompress rar files.

    :param ps_file: Path of the file we want to decompress.
    :type ps_file: Str

    :param ps_dst_dir: Path of the dir where the uncompressed data will be placed.
    :type ps_dst_dir: Str

    :return: Nothing.
    """
    ls_cmd = ['unrar', 'x', ps_file]

    if ps_dst_dir:
        ls_cmd += [ps_dst_dir]

    o_process = subprocess.Popen(ls_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_stdout, s_stderr = o_process.communicate()

    # TODO: Handle error messages


def _uncompress_zip(ps_file, ps_dst_dir=''):
    """
    Function to uncompress zip files.

    :param ps_file: Path of the file we want to decompress.
    :type ps_file: Str

    :param ps_dst_dir: Path of the dir where the uncompressed data will be placed.
    :type ps_dst_dir: Str

    :return: Nothing.
    """
    with zipfile.ZipFile(ps_file, 'r') as o_file:
        o_file.extractall(ps_dst_dir)
