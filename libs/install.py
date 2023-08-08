"""
Library with functions related to the installation of ROMs.
"""

import os
import shutil
import time
import zipfile

from . import files


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
    #TODO: When ROMs are multi-disc, decompress each one in sub-folders (disc 1, disc 2...)
    #TODO: Apply patches to required files
    #TODO: For multi-disc games, create a playlist file containing all discs (whatever format is used by RetroArch)

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
    print('  < Install dir initialization')
    files.init_dir(ps_dir)

    # Creation of directories for associated ROMs
    #--------------------------------------------
    ls_src_roms = sorted([po_rom_cfg.o_rom.s_path] + po_rom_cfg.o_rom.ls_linked_roms)
    ls_dst_roms = []

    for i_rom, s_src_rom in enumerate(ls_src_roms, start=1):
        if len(ls_src_roms) == 1:
            s_dst_rom = os.path.join(ps_dir, os.path.basename(s_src_rom))
        else:
            s_dst_rom = os.path.join(ps_dir, f'disc {i_rom}', os.path.basename(s_src_rom))

        ls_dst_roms.append(s_dst_rom)

    # Copying of ROMs to destination directory
    #-----------------------------------------
    if po_status is not None:
        po_status.s_message = 'Copying ROM...'

    for i_rom, (s_src_rom, s_dst_rom) in enumerate(zip(ls_src_roms, ls_dst_roms), start=1):
        files.init_dir(os.path.dirname(s_dst_rom))
        shutil.copyfile(s_src_rom, s_dst_rom)
        print(f'  < ROM #{i_rom} copied')

        if po_status is not None:
            po_status.f_progress += f_weight_rom_copy / (f_weight_total * len(ls_src_roms))

    time.sleep(2)

    # Decompressing ROM
    #------------------
    if po_status is not None:
        po_status.s_message = 'Decompressing ROM'

    for i_rom, s_dst_rom in enumerate(ls_dst_roms, start=1):
        with zipfile.ZipFile(s_dst_rom, 'r') as o_file:
            s_dst_dir = os.path.dirname(s_dst_rom)
            o_file.extractall(s_dst_dir)

        os.remove(s_dst_rom)
        s_msg = f'  < ROM #{i_rom} decompressed'
        print(s_msg)

        if po_status is not None:
            po_status.f_progress += f_weight_rom_unzip / (f_weight_total * len(ls_src_roms))

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


