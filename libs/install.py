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

    # Copying of ROMset to destination directory
    #-------------------------------------------
    if po_status is not None:
        po_status.s_message = 'Copying ROM...'

    for i_rom, (s_src_rom, s_dst_rom) in enumerate(zip(ls_src_roms, ls_dst_roms), start=1):
        files.init_dir(os.path.dirname(s_dst_rom))
        shutil.copyfile(s_src_rom, s_dst_rom)
        if pb_print:
            s_position = f'[{i_rom}/{len(ls_src_roms)}]'
            s_msg = f'  < ROM   {s_position} copied   | {os.path.basename(s_dst_rom)}'
            print(s_msg)

        if po_status is not None:
            po_status.f_progress += f_weight_rom_copy / (f_weight_total * len(ls_src_roms))

    # Decompressing ROMset
    #---------------------
    if po_status is not None:
        po_status.s_message = 'Decompressing ROM'

    for i_rom, s_dst_rom in enumerate(ls_dst_roms, start=1):
        s_dst_dir = os.path.dirname(s_dst_rom)
        libs.files.uncompress(ps_file=s_dst_rom, ps_dst_dir=s_dst_dir)

        os.remove(s_dst_rom)
        if pb_print:
            s_position = f'[{i_rom}/{len(ls_src_roms)}]'
            s_msg = f'  < ROM   {s_position} unzipped | {os.path.basename(s_dst_rom)}'
            print(s_msg)

        if po_status is not None:
            po_status.f_progress += f_weight_rom_unzip / (f_weight_total * len(ls_src_roms))

    if po_rom_cfg.o_patch is not None:
        _apply_patch(ps_dir, f_weight_patch_apply, po_rom_cfg.o_patch, po_status, pb_print)

    # TODO: Create a patching completed file or maybe it's not needed
    # TODO: Create an install completed file or maybe it's not needed
    # The reason I want those files is because I want the user to be aware of the issues without the program crashing,
    # but maybe raising an exception with information about the error is good enough.


# TODO: Maybe I should make this function public and create unit tests for it.
def _apply_patch(ps_dir, pf_weight_patch_apply, po_patch, po_status, pb_print):
    """

    :param ps_dir:
    :type ps_dir: Str

    :param pf_weight_patch_apply:
    :type pf_weight_patch_apply: Float

    :param po_patch: Patch to be applied.
    :type po_patch: patch.Patch

    :param po_status:
    :type po_status: Status

    :param pb_print:
    :type pb_print: Bool

    :return:
    """
    dtis_installed_files = files.index_dir(ps_dir=ps_dir, pts_ignore_exts=('cue',))

    # Copying patch_file
    #-------------------
    s_patch_dir = os.path.join(ps_dir, 'patch')
    files.init_dir(s_patch_dir)

    s_src_patch = po_patch.s_path
    s_dst_patch = os.path.join(s_patch_dir, os.path.basename(s_src_patch))
    shutil.copyfile(s_src_patch, s_dst_patch)
    libs.files.uncompress(s_dst_patch)
    os.remove(s_dst_patch)

    if po_status is not None:
        po_status.s_message = 'Downloading patch_file'

    dtis_patches = files.index_patch_dir(s_patch_dir)

    # To get the depth of the patches, we scan the patch indices
    li_depths = [len(ti_index) for ti_index in dtis_patches.keys()]
    i_max_depth = max(li_depths)

    # Applying patch_file
    #--------------------
    f_rom_patch_progress = pf_weight_patch_apply / len(dtis_patches)
    for i_patch, (ti_patch_index, s_patch_file) in enumerate(dtis_patches.items(), start=1):
        s_rom_file = dtis_installed_files[ti_patch_index]

        # ROM file preparation to update progress and/or terminal output. We want to show something legible, so we
        # will only show: a) the name of the file for single-disc ROMs, or b) the disc directory and the file path
        # for multi-sic games.
        o_rom_file = files.FilePath(s_rom_file)
        if i_max_depth == 1:
            s_msg_rom = os.sep.join(o_rom_file.ls_elements[-1:])
        else:
            s_msg_rom = os.sep.join(o_rom_file.ls_elements[-2:])

        if po_status is not None:
            po_status.s_message = f'Patching "{s_msg_rom}"'
            po_status.f_progress += f_rom_patch_progress

        files.patch_file(ps_file=s_rom_file, ps_patch=s_patch_file)

        if pb_print:
            s_position = f'[{i_patch}/{len(dtis_patches)}]'
            s_msg = f'  < Patch {s_position} applied  | {s_msg_rom}'
            print(s_msg)

    shutil.rmtree(s_patch_dir)
