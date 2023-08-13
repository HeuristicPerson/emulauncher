"""
Library with functions related to the installation of ROMs.
"""

import os
import re
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

    dtis_installed_files = files.index_dir(ps_dir=ps_dir, pts_ignore_exts=('cue',))

    # TODO: Decompress patch
    # TODO: Get index of patch files
    # TODO: Apply patches (at this point I'll have a 1:1 relationship between files and patches. If any of the patching
    #       tools is not able to patch in-place, create the temporary files in the patch directory.
    # TODO: Remove the whole patch directory (so all temporary files and patches will be removed).

    # TODO: The rom dir will contain the proper subfolders for multi-disc games, and the patch_file, all the patches.
    # Probably I should also incorporate the patch_file download and unzipping into the same function.
    # So, in principle, the function will only need two parameters to work.
    #if po_rom_cfg.o_patch is not None:
    #    patch_dir(ps_dir=ps_dir, ps_patch=po_rom_cfg.o_patch.s_path)

    if po_rom_cfg.o_patch is not None:
        # Copying patch_file
        #-------------------
        s_patch_dir = os.path.join(ps_dir, 'patch')
        files.init_dir(s_patch_dir)

        s_src_patch = po_rom_cfg.o_patch.s_path
        s_dst_patch = os.path.join(s_patch_dir, os.path.basename(s_src_patch))
        shutil.copyfile(s_src_patch, s_dst_patch)
        libs.files.uncompress(s_dst_patch)
        os.remove(s_dst_patch)

        if po_status is not None:
            po_status.s_message = 'Downloading patch_file'

        dtis_patches = files.index_patch_dir(s_patch_dir)

        # --- test code ---
        print()
        for s_key, s_value in dtis_installed_files.items():
            print(s_key, s_value)
        print('------')
        for s_key, s_value in dtis_patches.items():
            print(s_key, s_value)
        quit()
        # ------ end ------


        # Applying patch_file
        #---------------
        # TODO: Convert this patching code to a private function
        if po_rom_cfg.o_patch is not None:
            for s_elem in os.listdir(s_patch_dir):
                # TODO: Capture patch_file ROM CRC32, and two digits (disc, and file number)
                s_full_path = os.path.join()

            if po_status is not None:
                po_status.s_message = 'Applying patch_file'

    time.sleep(2)


def patch_dir(ps_dir, ps_patch, po_status=None, pb_print=False):
    """
    Function to apply a patch to an uncompressed ROM directory.

    If the ROM directory belongs to a multi-disc game, it must contain "disc 1", "disc 2", ... directories for each of
    the discs. The patch_file must be a single compressed file containing all the patches required for the whole game.

    :param ps_dir: Directory path of the uncompressed ROM. If the ROM belongs to a multi-disc game, different games will
    :type ps_dir: Str

    :param ps_patch: Path of the compressed file containing all the patches for the game.
    :type ps_patch: Str

    :param po_status: Status object so the patching process can update the progress (message and progress percentage).
    :type po_status: Status

    :param pb_print: Whether the function will print results to terminal or not.
    :type pb_print: Bool

    :return: Nothing.
    """

    # TODO: For consistency, it makes sense that both, the dir to be patched, and the patching data are decompressed.
    # That will probably make the code messier; explore the option and think about alternatives.

    # Getting a "list" of all ROM files
    #----------------------------------
    # This step has to be done at the beginning se we don't need extra code to ignore patch files from the scan.
    dtis_indexed_rom_files = files.index_dir(ps_dir, pts_ignore_exts=('cue',))

    # Copying the patch to a sub-folder of the installation dir, and decompressing it
    #--------------------------------------------------------------------------------
    if po_status is not None:
        po_status.s_message = 'Downloading patch_file'

    s_patch_dir = os.path.join(ps_dir, 'patch')
    files.init_dir(s_patch_dir)
    s_dst_patch = os.path.join(s_patch_dir, os.path.basename(ps_patch))
    shutil.copyfile(ps_patch, s_dst_patch)

    libs.files.uncompress(s_dst_patch)
    os.remove(s_dst_patch)

    # "Indexing" the patches, so they have the same index as the files to be applied
    #-------------------------------------------------------------------------------
    dtis_indexed_patch_files = files.index_patch_dir(s_patch_dir)

    # --- test code ---
    print()
    print(sorted(set(dtis_indexed_rom_files.keys())))
    print(sorted(set(dtis_indexed_patch_files.keys())))
    quit()
    # ------ end ------

    po_status.s_message = 'Applying patch_file'



