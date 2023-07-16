"""
Library with a class to store information about a ROM file
"""

import os
import re

from . import cons
from . import dat_files
from . import string_helpers


# Initialization
#=======================================================================================================================
#_lo_platforms = platforms.read_platforms_file(cons._s_platforms_file)

# TODO: Read available cores.
# I think this is not needed anymore, functionality added somewhere else


# Classes
#=======================================================================================================================
class Rom:
    """
    :ivar o_platform: platform.PlatformCfg
    """
    def __init__(self, ps_platform, ps_path, ps_dat=''):
        """

        :param ps_platform: Alias of the platform that runs the ROM.
        :type ps_platform: Str

        :param ps_path: Path of the ROM.
        :type ps_path: Str

        :param ps_dat: Path of a dat file to get more information from
        :type ps_dat: Str
        """

        self.s_path = ps_path
        self.s_ccrc32 = ''
        self.s_dcrc32 = ''
        self.s_name = ''
        self.i_csize = 0
        self.i_dsize = 0
        self.s_dat = ''
        self.s_dat_ver = ''

        try:
            self.o_platform = cons.do_PLATFORMS[ps_platform]
        except KeyError as o_exception:
            s_msg = f'Platform with alias "{ps_platform}" not found in {cons._s_platforms_file}'
            raise KeyError(s_msg) from o_exception

        self.populate_from_file(ps_path)

        if ps_dat:
            self.populate_from_dat(ps_dat)

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
        # TODO: replace with my str method from class_to_string
        s_out = '<Rom>\n'
        s_out += f'  .s_name:        {self.s_name}\n'
        s_out += f'  .s_path:        {self.s_path}\n'
        s_out += f'  .s_dat:         {self.s_dat}\n'
        s_out += f'  .s_dat_ver:     {self.s_dat_ver}\n'
        s_out += f'  .i_dsize:       {self.i_dsize}\n'
        s_out += f'  .i_csize:       {self.i_csize}\n'
        s_out += f'  .s_dcrc32:      {self.s_dcrc32}\n'
        s_out += f'  .s_ccrc32:      {self.s_ccrc32}\n'
        s_out += f'  .s_dcrc32_safe: {self.s_dcrc32_safe}\n'  # Safe dirty CRC32 ('xxxxxxxx' when crc32 is empty)
        s_out += f'  .s_ccrc32_safe: {self.s_ccrc32_safe}\n'  # Safe clean CRC32 ('xxxxxxxx' when crc32 is empty)

        s_out += string_helpers.section_generate('  .o_platform:', str(self.o_platform).splitlines(False))
        return s_out

    def nice_format(self):
        """
        Method to generate a nice human-readable summary of ROM information.

        :Return: A text summary with ROM information.
        :rtype: Str
        """
        s_out = ''
        s_out += f'┌[ROM Information]───────\n'
        s_out += f'├ From file \n'
        s_out += f'│   Name:        {self.s_name}\n'
        s_out += f'│   System:      {self.o_platform.s_name}\n'
        s_out += f'├ From .dat\n'
        s_out += f'│   Dat:         {self.s_dat} - {self.s_dat_ver}\n'
        s_out += f'│   Size:        dirty={self.i_dsize}, clean={self.i_csize}\n'
        s_out += f'│   CRC32:       dirty={self.s_dcrc32}, clean={self.s_ccrc32}\n'
        s_out += f'├ From platform\n'
        s_out += f'│   Cores:       %s\n' % ', '.join(self.o_platform.ls_cores)
        s_out += f'│   Aspect:      {self.o_platform.f_aspect:.3f}\n'
        s_out += f'│   Regions:     %s\n' % ', '.join([str(s_region) for s_region in self.o_platform.ls_regions])
        s_out += f'│   Refresh:     %s\n' % ', '.join([str(f_freq) for f_freq in self.o_platform.lf_freqs])
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
        o_dat = dat_files.Dat(ps_file=ps_dat)
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

    def _get_s_region_auto(self):
        """
        Method to get the automatic region for the current ROM. The region will be obtained from the platform settings
        and the ROM name.

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
        settings and the ROM name.

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