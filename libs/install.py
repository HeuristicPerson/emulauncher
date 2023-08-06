"""
Library with functions related to the installation of ROMs.
"""

import os
import shutil
import time
import zipfile

from .files import clean_dir


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
    # TODO: Add function to identify other "ROMs" from multi-disc games (probably it has to be done way upstream)
    # TODO: When ROMs are multi-disc, decompress each one in sub-folders (disc 1, disc 2...)
    # TODO: Apply patches to required files
    # TODO: For multi-disc games, create a playlist file containing all discs (whatever format is used by RetroArch)

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
        clean_dir(ps_dir)
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


def patch(ps_file, ps_patch):
    """

    :param ps_file:
    :param ps_patch:
    :return:
    """
    pass


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


