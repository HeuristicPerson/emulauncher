"""
Library with a class to store information about a ROM file
"""

import os
import re

from . import class_to_string
from . import cons
from . import datfiles
from . import files
from . import string_helpers


# Classes
#=======================================================================================================================
class Rom:
    """
    :ivar o_platform: platform.PlatformCfg
    """
    def __init__(self, ps_platform, ps_path, ps_dat='', pb_linked=True):
        """
        :param ps_platform: Alias of the platform that runs the ROM.
        :type ps_platform: Str

        :param ps_path: Path of the ROM.
        :type ps_path: Str

        :param ps_dat: Path of a dat file to get more information from
        :type ps_dat: Str

        :param pb_linked: Whether linked (e.g. multi-file or multi-disc ROMs need to be identified and stored).
        :type pb_linked: Bool
        """
        self.s_path = ps_path     # Full path of the ROM.
        self.s_ccrc32 = ''        # Clean additive CRC32 of the ROM.
        self.s_dcrc32 = ''        # Dirty additive CRC32 of the ROM.
        self.s_name = ''          # Name of the ROM.
        self.i_csize = None       # Clean size of the ROM.
        self.i_dsize = None       # Dirty size of the ROM.
        self.i_psize = None       # Path-size of the ROM (or real disk size if the file actually exists).
        self.s_dat = ''           # Dat file the ROM is matched against.
        self.s_dat_ver = ''       # Version of the dat file the ROM is matched against.

        # Linked ROMs (e.g. for multi disc games, the other discs) paths. There is no point in creating full Rom objects
        # for linked ROMs since we don't need most of the data. Only the path will be used to install the ROMs. The
        # attribute is private because the data stored will only be the NAME of the linked ROMs, without path or file
        # extension. The full path will be built by a get method.
        self._ls_linked_roms = []

        try:
            self.o_platform = cons.do_PLATFORMS[ps_platform]
        except KeyError as o_exception:
            s_msg = f'Platform with alias "{ps_platform}" not found in {cons._s_PLATFORMS_FILE}'
            raise KeyError(s_msg) from o_exception

        self.populate_from_file(ps_path)

        if ps_dat:
            self.populate_from_dat(ps_dat)

        if pb_linked:
            self._find_linked_roms()

    def __eq__(self, po_other):
        """
        :param po_other:
        :type po_other: Rom

        :return:
        :rtype: Bool
        """
        b_equal = True
        ts_attribs = ('s_path', 's_ccrc32', 's_dcrc32', 's_name', 'i_csize', 'i_dsize', 's_dat', 's_dat_ver',
                      'o_platform')
        for s_attrib in ts_attribs:
            if getattr(self, s_attrib) != getattr(po_other, s_attrib):
                b_equal = False
                break

        return b_equal

    def __str__(self):
        """
        Method to build a text representation of the instance.
        :return: A text representation of the instance.
        :rtype: Str
        """
        s_out = class_to_string.class_to_string(self)
        return s_out

    def nice_format(self):
        """
        Method to generate a nice human-readable summary of ROM information.

        :Return: A text summary with ROM information.
        :rtype: Str
        """

        s_file_size = files.file_size_format(self.i_psize)
        s_rom_csize = files.file_size_format(self.i_csize)
        s_rom_dsize = files.file_size_format(self.i_dsize)

        s_out = ''
        s_out += f'┌[ROM Information]───────\n'
        s_out += f'├ From file \n'
        s_out += f'│   Name: ...... {self.s_name}\n'
        s_out += f'│   System: .... {self.o_platform.s_name}\n'
        s_out += f'│   Size: ...... {self.i_psize} ({s_file_size})\n'
        s_out += f'├ From .dat\n'
        s_out += f'│   Dat: ....... {self.s_dat} - {self.s_dat_ver}\n'
        s_out += f'│   Size: ...... dirty={self.i_dsize} ({s_rom_dsize}), clean={self.i_csize} ({s_rom_csize})\n'
        s_out += f'│   CRC32: ..... dirty={self.s_dcrc32}, clean={self.s_ccrc32}\n'
        s_out += f'├ From platform\n'
        s_out += f'│   Cores: ..... %s\n' % ', '.join(self.o_platform.ls_cores)
        s_out += f'│   Aspect: .... {self.o_platform.f_aspect:.3f}\n'
        s_out += f'│   Regions: ... %s\n' % ', '.join([str(s_region) for s_region in self.o_platform.ls_regions])
        s_out += f'│   Refresh: ... %s\n' % ', '.join([str(f_freq) for f_freq in self.o_platform.lf_freqs])
        s_out += f'│   R. patterns: %s\n' % ', '.join(self.o_platform.ls_region_pats)
        s_out += f'└────────────────────────'
        return s_out

    def populate_from_dat(self, ps_dat):
        """
        Method to populate the Rom object with information from a .dat file.

        :param ps_dat: Path of the .dat file to be used to extract extra information for the ROM.
        :type ps_dat: Str

        :return: Nothing, the object will be populated in place.
        """
        o_dat = datfiles.Dat(ps_file=ps_dat)
        self.s_dat = o_dat.s_name
        self.s_dat_ver = o_dat.s_version

        s_file = os.path.basename(self.s_path)
        s_file_name, _, s_file_ext = s_file.rpartition('.')

        o_dat_rom = o_dat.get_romset_by_name(s_file_name)

        if o_dat_rom is not None:
            self.s_name = o_dat_rom.s_desc
            self.i_dsize = o_dat_rom.i_dsize
            self.i_csize = o_dat_rom.i_csize
            self.s_dcrc32 = o_dat_rom.s_dcrc32
            self.s_ccrc32 = o_dat_rom.s_ccrc32

        # Method to identify and store linked ROMs (e.g. when the current ROM is the first disc of a multi-disc game,
        # this method will try to identify the other discs of the game). At the moment, the only way to identify linked
        # ROMs is through the use of .dat files. Naming convention for non-.dat ROMs is not standardise in any way, so
        # it's not worth wasting time in coding that will never be reliable.
        lo_linked_dat_roms = o_dat.get_linked_roms(self.s_name)
        self._ls_linked_roms = [o_dat_rom.s_name for o_dat_rom in lo_linked_dat_roms]

    def populate_from_file(self, ps_file):
        """
        Method to populate the Rom object with information from a file.

        :param ps_file: Path of the file to be used.
        :type ps_file: Str

        :return: Nothing
        """
        s_file_name = os.path.basename(ps_file)
        s_name, _, s_ext = s_file_name.rpartition('.')
        self.s_name = s_name

        try:
            self.i_psize = os.stat(self.s_path).st_size
        except FileNotFoundError:
            self.i_psize = None

    def _find_linked_roms(self):
        """
        Method to identify and store linked ROMs (e.g. when the current ROM is the first disc of a multi-disc game, this
        method will try to identify the other discs of the game). At the moment, the only way to identify linked ROMs is
        through the use of .dat files. Naming convention for non-.dat ROMs is not standardise in any way, so it's not
        worth wasting time in coding that will never be reliable.
        :return: Nothing.
        """

    def _get_ls_linked_roms(self):
        """
        Method to build the linked roms list that will contain the full path of the linked ROMs. Please keep in mind the
        existence of the paths won't be checked.

        :return: A list with the full path of all the linked ROMs.
        :rtype: List[Str]
        """
        s_rom_dir = os.path.dirname(self.s_path)
        s_rom_ext = self.s_path.rpartition('.')[2]
        ls_linked_roms = [os.path.join(s_rom_dir, s_linked_rom)
                          for s_linked_rom in self._ls_linked_roms]
        return ls_linked_roms

    def _get_s_region_auto(self):
        """
        Method to get the automatic region for the current ROM. The region will be obtained from the platform settings
        and the ROM ps_name.

        :return: The automatic region of the ROM.
        :rtype: Str
        """
        s_def_region = self.o_platform.ls_regions[0]
        for s_region, s_pattern in zip(self.o_platform.ls_regions, self.o_platform.ls_region_pats):
            if re.search(s_pattern, self.s_name):
                s_def_region = s_region
                break

        return s_def_region

    def _get_f_refresh_auto(self):
        """
        Method to get the automatic refresh rate for the current ROM. The refresh will be obtained from the platform
        settings and the ROM ps_name.

        :return: The automatic refresh rate of the ROM.
        :rtype: Float
        """
        f_def_freq = self.o_platform.lf_freqs[0]
        for f_freq, s_pattern in zip(self.o_platform.lf_freqs, self.o_platform.ls_region_pats):
            if re.search(s_pattern, self.s_name):
                f_def_freq = f_freq
                break

        return f_def_freq

    def _get_s_dcrc32_safe(self):
        """
        Method to obtain a "safe" value for dirty crc32, which uses 'xxxxxxxx' as default when no CRC32 is present. This
        method is accessed through the attribute .s_dcrc32_safe for the times when a text CRC32 is required.

        :return: A CRC32 string that uses 'xxxxxxxx' as default when there is no valid CRC32.
        :rtype: Str
        """
        s_crc32 = 'xxxxxxxx'
        if self.s_dcrc32:
            s_crc32 = self.s_dcrc32
        return s_crc32

    def _get_s_ccrc32_safe(self):
        """
        Method to obtain a "safe" value for clean crc32, which uses 'xxxxxxxx' as default when no CRC32 is present. This
        method is accessed through the attribute .s_ccrc32_safe for the times when a text CRC32 is required.

        :return: A CRC32 string that uses 'xxxxxxxx' as default when there is no valid CRC32.
        :rtype: Str
        """
        s_crc32 = 'xxxxxxxx'
        if self.s_ccrc32:
            s_crc32 = self.s_ccrc32
        return s_crc32

    f_refresh_auto = property(fget=_get_f_refresh_auto, fset=None)
    s_region_auto = property(fget=_get_s_region_auto, fset=None)
    s_dcrc32_safe = property(fget=_get_s_dcrc32_safe, fset=None)
    s_ccrc32_safe = property(fget=_get_s_ccrc32_safe, fset=None)
    ls_linked_roms = property(fget=_get_ls_linked_roms, fset=None)
