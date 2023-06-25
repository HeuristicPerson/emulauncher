"""
Library with some functions and classes related with the configuration of ROM files.
"""

import codecs
import configparser
import datetime
import os

from . import cons
from . import config
from . import cores
from . import patches
from . import roms
from . import string_helpers


class RomConfig:
    """
    :ivar _o_core: cores.Core
    :ivar o_patch: patches.Patch
    :ivar f_refresh: Float
    :ivar o_rom: roms.Rom
    :ivar s_user: Str
    """
    def __init__(self):
        self.s_region = ''     # Region of the console to be used during emulation
        self._f_refresh = 0.0  # Refresh rate of the screen to be used during emulation
        self._o_core = None    # Retroarch core to be used
        self.o_patch = None    # Patch applied/to be applied
        self.o_rom = None      # ROM object to be launched
        self.s_user = ''       # Name of de user (machine name) launching the ROM

    def __str__(self):
        """
        Function to represent the object as a string.

        :return: A string representing the object.
        :rtype: Str
        """
        s_out = '<RomConfig>\n'
        s_out += f'  .s_user:    {self.s_user}\n'
        s_out += f'  .s_region:  {self.s_region}\n'
        s_out += f'  .f_refresh: {self.f_refresh}\n'

        # core information
        s_out += string_helpers.section_generate('  ._o_core:  ', str(self._o_core).splitlines(False))
        s_out += string_helpers.section_generate('  .o_patch:  ', str(self.o_patch).splitlines(False))
        s_out += string_helpers.section_generate('  .o_rom:    ', str(self.o_rom).splitlines(False))

        return s_out

    def nice_format(self):
        """
        Method to generate a string representation of the instance in a nice human-readable format.

        :return: A "human" formatted text representation of the object in a relatively nice format.
        :rtype: Str
        """
        s_out = ''
        s_out += f'User:    {self.s_user}\n'

        if self.o_rom is None:
            s_out += f'ROM:     [????????] None\n'
        else:
            s_out += f'ROM:     [{self.o_rom.s_ccrc32}] {self.o_rom.s_name}\n'

        s_out += f'Patch:   {self.o_patch}\n'
        s_out += f'Region:  {self.s_region}\n'
        s_out += f'Refresh: {self.f_refresh}\n'

        if self._o_core is None:
            s_out += f'Core:    None'
        else:
            s_out += f'Core:    {self._o_core.s_name}'

        return s_out

    def load_from_disk(self, ps_file, po_prog_cfg):
        """
        Method to load a rom config from disk. It makes sense to pass the program configuration to this method so when
        we load a RomConfig from file, we can search for the patch in the right location. So, for example, we can create
        a RomConfig file in the past when the patches where located in '/patches/original_location', then change the
        configuration, so the patches are located in '/patches/new_location', and the RomConfig saves will still work.

        :param ps_file: Path of the file to be loaded.
        :type ps_file: Str

        :param po_prog_cfg: Program configuration object.
        :type po_prog_cfg: config.ProgramCfg

        :return: Nothing, the object will be populated in place.
        """
        # Interestingly, config parser read doesn't raise an exception when the file doesn't exist, so we have to raise
        # it manually.
        if not os.path.isfile(ps_file):
            s_msg = f'Can\'t read file {ps_file}'
            raise IOError(s_msg)
        else:
            # Reading the "raw" ini
            #----------------------
            o_ini = configparser.ConfigParser()
            o_ini.read(ps_file)

        # Validating that the read configuration is for the current ROM
        #--------------------------------------------------------------
        if self.o_rom is None:
            s_msg = 'Before reading a configuration file, you must have populated self.o_rom first'
            raise ValueError(s_msg)

        else:
            if not _check_rom_and_ini_match(self.o_rom, o_ini):
                s_rom_summary = f'[{self.o_rom.s_ccrc32}] {self.o_rom.s_name}'
                s_ini_summary = f'[%s] %s' % (o_ini.get('rom', 'ccrc32'), o_ini.get('rom', 'name'))
                s_msg = 'Rom (%s) and RomConfig (%s) don\'t match.' % (s_rom_summary, s_ini_summary)
                raise ValueError(s_msg)
            else:
                # Since saved configurations will be shared between users, we won't read the username from them.
                # TODO: add extra parameter to ignore attributes during the loading

                self.s_user = o_ini.get('meta', 'user')

                self.s_region = o_ini.get('settings', 'region')
                self.f_refresh = o_ini.getfloat('settings', 'refresh')

                # To get the patch, we first find all the patches available for the Rom object, and then we identify the
                # one with the right name.
                s_ini_patch = o_ini.get('rom', 'patch')
                if s_ini_patch:
                    s_patches_dir = po_prog_cfg.ds_patch_dirs[self.o_rom.o_platform.s_alias]
                    lo_patches = patches.get_patches(s_patches_dir, self.o_rom)

                    for o_patch in lo_patches:
                        if o_patch.s_title == s_ini_patch:
                            self.o_patch = o_patch
                            break
                    else:
                        # TODO: Rather than printing, add logger object and/or maybe print info to gui
                        print(f'ERROR: patch "{s_ini_patch}" not found')

                # Getting the core object from the core name saved in the file. We will check that a) the core is valid
                # for the current platform, and the core is available in the system.
                s_ini_core = o_ini.get('settings', 'core')
                s_cores_dir = po_prog_cfg.s_cores_dir
                lo_cores = cores.get_cores(ps_dir=s_cores_dir, pls_cores_wanted=[s_ini_core])
                do_cores = {o_core.s_name: o_core for o_core in lo_cores}
                if (s_ini_core in self.o_rom.o_platform.ls_cores) and (s_ini_core in do_cores):
                    self.o_core = do_cores[s_ini_core]
                else:
                    # TODO: Rather than printing, add logger object and/or maybe print info to the gui
                    print(f'ERROR: core "{s_ini_core}" not found')

    def save_to_disk(self, ps_file):
        """
        Method to load a rom config from disk.

        TODO: Maybe pass program config as parameter so we can save the full path of the patch... NOT NEEDED, the
        patch already has the full path.

        :param ps_file: Path of the file to be saved.
        :type ps_file: Str

        :return: Nothing.
        """
        # Core name
        try:
            s_core = self._o_core.s_name
        except AttributeError:
            s_core = ''

        o_config = configparser.ConfigParser()
        o_config.add_section('meta')
        o_config.set('meta', 'builder', cons.s_PRG)
        o_config.set('meta', 'date', str(datetime.datetime.now()))
        o_config.set('meta', 'user', self.s_user)
        o_config.add_section('rom')
        o_config.set('rom', 'name', self.o_rom.s_name)
        o_config.set('rom', 'ccrc32', self.o_rom.s_ccrc32)
        o_config.set('rom', 'platform', self.o_rom.o_platform.s_alias)
        o_config.set('rom', 'patch', 'foo')
        o_config.add_section('settings')
        o_config.set('settings', 'core', s_core)
        o_config.set('settings', 'region', self.s_region)
        o_config.set('settings', 'refresh', str(self.f_refresh))

        with codecs.open(ps_file, 'w') as o_file:
            o_config.write(o_file)

    def _get_f_refresh(self):
        return self._f_refresh

    def _set_f_refresh(self, pf_value):
        """
        Method to set the frequency. If the value is not among the valid frequencies for the platform, a ValueError
        exception will be raised.

        :param pf_value:
        :type pf_value: Float

        :return: Nothing
        """
        if self.o_rom is None:
            s_msg = f'Invalid refresh rate "{pf_value}" for self.o_rom = None'
            raise ValueError(s_msg)
        elif pf_value in self.o_rom.o_platform.lf_freqs:
            self._f_refresh = pf_value
        else:
            s_msg = f'Invalid refresh rate "{pf_value}" for platform "{self.o_rom.o_platform.s_alias}"'
            raise ValueError(s_msg)

    def _get_o_core(self):
        """
        :return:
        :rtype: cores.Core
        """
        return self._o_core

    def _set_o_core(self, po_core):
        """
        :param po_core:
        :type po_core: cores.Core
        :return: Nothing.
        """
        # Before storing the core, we need to validate the core is valid for the current rom/platform
        if po_core.s_name not in self.o_rom.o_platform.ls_cores:
            s_msg = f'Invalid core "{po_core.s_name}" for platform "{self.o_rom.o_platform.s_alias}".'
            raise ValueError(s_msg)
        else:
            self._o_core = po_core

    o_core = property(fget=_get_o_core, fset=_set_o_core)
    f_refresh = property(fget=_get_f_refresh, fset=_set_f_refresh)


def generate_default_cfg(po_rom, pto_cores_available):
    """
    Function to generate the default configuration for a ROM, the default configuration doesn't contain a user, nor
    a patch.

    :param po_rom: Rom object to generate a default configuration for.
    :type po_rom: roms.Rom

    :param pto_cores_available: Tuple with all cores available in the system.
    :type pto_cores_available: Tuple[cores.Core]

    :return: Nothing, the object will be modified in place.
    """
    o_def_cfg = RomConfig()
    o_def_cfg.o_rom = po_rom
    o_def_cfg._o_core = _return_priority_core(po_rom, pto_cores_available)
    o_def_cfg.f_refresh = po_rom.f_refresh_auto
    o_def_cfg.s_region = po_rom.s_region_auto
    return o_def_cfg


# Helper functions
#=======================================================================================================================
def _return_priority_core(po_rom, pto_cores_available):
    """
    Function to return the core with the highest priority (given by the Rom object) between a tuple with multiple core
    objects.

    :param po_rom:
    :type po_rom: roms.Rom

    :param pto_cores_available:
    :type pto_cores_available: Tuple[cores.Core]

    :return: A core object
    :rtype: Union[None, cores.Core]
    """
    for s_core in po_rom.o_platform.ls_cores:
        for o_core in pto_cores_available:
            if s_core == o_core.s_name:
                return o_core

    return None


def _check_rom_and_ini_match(po_rom, po_ini):
    """
    Function to check that a Rom object and a RomConfig object contain information for the same Rom file. When possible,
    the clean CRC32 (CCRC32) of both objects will be compared, otherwise, the rom name will be used.

    :param po_rom: Rom object we want to check.
    :type po_rom: roms.Rom

    :param po_ini: Ini object containing loaded data from RomConfig saved file.
    :type po_ini: configparser.ConfigParser

    :return:
    :rtype: Bool
    """
    # It's not needed to lowercase the CCRC32 because it should be already lowercase, but the ROM name has to in order
    # to add a bit of robustness. I'm not planning to keep non-dated ROMs' saved configs,
    s_rom_ccrc32 = po_rom.s_ccrc32.lower()
    s_ini_ccrc32 = po_ini['rom']['ccrc32'].lower()

    s_rom_name = po_rom.s_name.lower()
    s_ini_name = po_ini['rom']['name'].lower()

    ls_ccrc32 = list({s_rom_ccrc32, s_ini_ccrc32})

    b_match = False

    # If both CCRC32 are the same...
    if len(ls_ccrc32) == 1:
        s_ccrc32 = ls_ccrc32[0]

        # Case 1: Both roms have clean CRC32 defined, and they are the same
        if s_ccrc32 != '':
            b_match = True

        # Case 2: CCRC32s equal, but empty
        else:
            # Just making the matching robust to casing differences
            if s_rom_name == s_ini_name:
                b_match = True

    return b_match
