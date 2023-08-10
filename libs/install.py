"""
Library with functions related to the installation of ROMs.
"""

import os
import shutil
import time
import zipfile

import libs.files
from . import files
from . import cli_tools


# Main functions
#=======================================================================================================================
def install(po_rom_cfg, ps_dir, po_status=None, pb_print=False):
    """
    Function
    :param pb_print:
    :param po_rom_cfg:
    :type po_rom_cfg: libs.romconfig.RomConfig

    :param ps_dir: Installation directory
    :type ps_dir: Str

    :param po_status:
    :type po_status: Status

    :param pb_print: Whether the function will print results to terminal or not.
    :type pb_print: Bool

    :return: Nothing.
    """
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
    if pb_print:
        s_msg = '  < Install dir initialization'
        print(s_msg)

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
        if pb_print:
            s_msg = f'  < ROM #{i_rom} copied'
            print(s_msg)

        if po_status is not None:
            po_status.f_progress += f_weight_rom_copy / (f_weight_total * len(ls_src_roms))

    time.sleep(2)

    # Decompressing ROM
    #------------------
    if po_status is not None:
        po_status.s_message = 'Decompressing ROM'

    for i_rom, s_dst_rom in enumerate(ls_dst_roms, start=1):
        s_dst_dir = os.path.dirname(s_dst_rom)
        libs.files.uncompress(ps_file=s_dst_rom, ps_dst_dir=s_dst_dir)

        os.remove(s_dst_rom)
        if pb_print:
            s_msg = f'  < ROM #{i_rom} decompressed'
            print(s_msg)

        if po_status is not None:
            po_status.f_progress += f_weight_rom_unzip / (f_weight_total * len(ls_src_roms))

    # TODO: The rom dir will contain the proper subfolders for multi-disc games, and the patch, all the patches.
    # Probably I should also incorporate the patch download and unzipping into the same function.
    # So, in principle, the function will only need two parameters to work.
    patch(ps_rom_dir, ps_patch_dir)
    if po_rom_cfg.o_patch is not None:
        # Copying patch
        #--------------
        s_patch_dir = os.path.join(ps_dir, 'patch')
        files.init_dir(s_patch_dir)

        s_src_patch = po_rom_cfg.o_patch.s_path
        s_dst_patch = os.path.join(s_patch_dir, os.path.basename(s_src_patch))
        shutil.copyfile(s_src_patch, s_dst_patch)
        libs.files.uncompress(s_dst_patch)
        os.remove(s_dst_patch)

        if po_status is not None:
            po_status.s_message = 'Downloading patch'

        # Applying patch
        #---------------
        # TODO: Convert this patching code to a private function
        if po_rom_cfg.o_patch is not None:
            for s_elem in os.listdir(s_patch_dir):
                # TODO: Capture patch ROM CRC32, and two digits (disc, and file number)
                s_full_path = os.path.join()

            if po_status is not None:
                po_status.s_message = 'Applying patch'

    time.sleep(2)


def patch(ps_dir, ps_patch):
    """
    Function to apply a patch to an uncompressed ROM directory.

    If the ROM directory belongs to a multi-disc game, it must contain "disc 1", "disc 2", ... directories for each of
    the discs. The patch must be a single compressed file containing all the patches required for the whole game.

    :param ps_dir: Directory path of the uncompressed ROM. If the ROM belongs to a multi-disc game, different games will
    :type ps_dir: Str

    :param ps_patch: Path of the compressed file containing all the patches for the game.
    :type ps_patch: Str

    :return: Nothing.
    """
    pass
