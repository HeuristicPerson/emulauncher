"""
Library with functions related to the installation of ROMs.
"""

import os
import shutil
import time
import zipfile

from . import paths


# Helper functions
#=======================================================================================================================
def _clean_dir(ps_dir):
    """
    Function to clean the contents of a directory.

    :param ps_dir:
    :type ps_dir: Str

    :return: Nothing.
    """
    for s_element in os.listdir(ps_dir):
        file_path = os.path.join(ps_dir, s_element)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


# Main functions
#=======================================================================================================================
def install(po_rom_cfg, ps_dir, po_status=None):
    """
    Function
    :param po_rom_cfg:
    :type po_rom_cfg: libs.romconfig.RomConfig

    :param ps_dir: Installation directory
    :type ps_dir: Str

    :param po_status:
    :type po_status: Status

    :return:
    """
    # Initialization of weights
    #--------------------------
    f_weight_rom_copy = 0.3
    f_weight_rom_unzip = 0.1
    f_weight_patch_copy = 0.2
    f_weight_patch_unzip = 0.1
    f_weight_patch_apply = 0.1

    if po_rom_cfg.o_patch is None:
        f_weight_total = f_weight_rom_copy + f_weight_rom_unzip
    else:
        f_weight_total = f_weight_rom_copy + f_weight_rom_unzip + f_weight_patch_copy + f_weight_patch_unzip + \
                         f_weight_patch_apply

    # Cleaning/creation of the install directory
    #-------------------------------------------
    if os.path.isdir(ps_dir):
        print('  < Cleaned directory')
        _clean_dir(ps_dir)
    else:
        print('  < Created directory')
        os.makedirs(ps_dir)

    # Copying of ROM to destination directory
    #----------------------------------------
    if po_status is not None:
        po_status.s_message = 'Copying ROM...'

    s_src_file = po_rom_cfg.o_rom.s_path
    s_dst_file = os.path.join(ps_dir, os.path.basename(s_src_file))

    shutil.copyfile(s_src_file, s_dst_file)
    print('  < ROM copied')

    if po_status is not None:
        po_status.f_progress += f_weight_rom_copy / f_weight_total

    time.sleep(2)

    # Decompressing ROM
    #------------------
    if po_status is not None:
        po_status.s_message = 'Decompressing ROM'

    with zipfile.ZipFile(s_dst_file, 'r') as o_file:
        o_file.extractall(ps_dir)

    os.remove(s_dst_file)
    print('  < ROM decompressed')

    if po_status is not None:
        po_status.f_progress += f_weight_rom_unzip / f_weight_total

    # Copying patch
    #--------------
    if po_rom_cfg.o_patch is not None:
        if po_status is not None:
            po_status.s_message = 'Downloading patch'

    # Applying patch
    #---------------
    if po_rom_cfg.o_patch is not None:
        if po_status is not None:
            po_status.s_message = 'Applying patch'

    time.sleep(2)


def dummy(po_status, po_romconfig=None):
    """
    Function
    :param po_romconfig:

    :param po_status:
    :type po_status: Status

    :return:
    """
    for i_iter in range(10):
        po_status.f_progress += 0.1
        po_status.s_message = f'iteration {i_iter}'
        time.sleep(1)


