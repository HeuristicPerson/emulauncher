"""
Library to work with patch files.
"""

import natsort
import os

from . import roms
from . import string_helpers


# Classes
#=======================================================================================================================
class Patch:
    """
    Class to store information about a patch .zip file.

    :ivar s_path: Str
    :ivar s_ccrc32: Str
    :ivar s_title: Str
    """
    def __init__(self, ps_file=''):
        self.s_path = ''         # Full path of the patch.
        self.s_ccrc32 = ''       # Clean CRC32 of the ROM the patch can be applied onto. e.g. 'a23f017d'
        self.s_title = ''        # Title of the patch, short and descriptive.
        if ps_file:
            self.load_from_file(ps_file)

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        s_out = '<Patch>\n'
        s_out += f'  .s_path:   {self.s_path}\n'
        s_out += f'  .s_ccrc32: {self.s_ccrc32}\n'
        s_out += f'  .s_title:  {self.s_title}\n'
        return s_out

    def load_from_file(self, ps_file):
        """
        Method to initialise the patch from a file and, optionally, from a Rom object.

        :param ps_file: Path of the patch.
        :type ps_file: Str

        :return: Nothing, the object will be populated in place.
        """
        self.s_path = ps_file

        # Extracting information from the file name
        s_file = os.path.basename(ps_file).rpartition('.')[0]

        s_ccrc32, _, s_title = s_file.partition(' - ')

        # Reading as much information as possible from the patch file
        #------------------------------------------------------------
        if string_helpers.is_crc32(s_ccrc32):
            self.s_ccrc32 = s_ccrc32
        else:
            s_msg = 'The first part of the patch file name is not a valid CRC32.'
            raise ValueError(s_msg)

        if s_title:
            self.s_title = s_title
        else:
            s_msg = 'The description of the patch file name is empty.'
            raise ValueError(s_msg)


# Functions
#=======================================================================================================================
def get_patches(ps_dir, po_rom):
    """
    Function to get available patches in a dir for certain ROM. By default, the function will search for patches
    following the name scheme:

      - "0a0b0c0d - description.zip" where the first 8 chars are the (clean) CRC32 of the ROM.
      - "sonic the hedgehog (usa) - description.zip" where anything below - description is the ROM name. This second
        method is NOT recommended at all.

    :param ps_dir:
    :type ps_dir: Str

    :param po_rom:
    :type po_rom: rom.Rom

    :return:
    :rtype: List[Patch]
    """

    # Getting the list of patches compatible with the given ROM
    #----------------------------------------------------------
    lo_patches = []
    ls_elems = os.listdir(ps_dir)
    ls_elems = natsort.os_sorted(ls_elems)

    for s_elem in sorted(ls_elems):
        s_full_path = os.path.join(ps_dir, s_elem)

        if os.path.isfile(s_full_path):
            try:
                o_patch = Patch(s_full_path)
            except ValueError:
                continue

            if o_patch.s_ccrc32 == po_rom.s_ccrc32:
                lo_patches.append(o_patch)

    return lo_patches


# Rom patching
#=======================================================================================================================
def apply_patch(ps_src_file, ps_patch, ps_dst_file):
    """
    Function to generalize the application to patch files using different patching programs based on the extension of
    the patch.

    :param ps_src_file: Patch of the file to be patched.
    :type ps_src_file: Str

    :param ps_patch:
    :type ps_patch: Str

    :param ps_dst_file:
    :type ps_dst_file: Final file generated by the patching tool.

    :return: Nothing
    """
    pass
