import configparser
import os.path

import yaml

from . import class_to_string


# Classes
#=======================================================================================================================
class ProgramCfg:
    """
    Class to read and store program configuration data.

    :ivar f_volume: Float
    :ivar s_cores_dir: Str
    """
    def __init__(self, ps_file=''):
        """
        :param ps_file: Path of an .ini file to populate the configuration object.
        :type ps_file: Str

        :return: Nothing, the object will be populated in place.
        """
        self.s_cache_dir = ''     # Directory for the cached data (ROMs, savegames...)
        self.i_cache_size = 0     # Size in bytes of the cache dir (0 means unlimited)
        self.ds_rom_dirs = {}     # Directories with source ROMs (that will be copied to the cache dir)
        self.ds_patch_dirs = {}   # Directories with patches (that will be copied to the cache dir)

        self.i_width = 640        # Window width
        self.i_height = 480       # Window height
        self.s_theme = 'default'  # Name of the theme to be used

        self.s_dats_dir = ''      # Directory for .dat files
        self.s_users_dir = ''     # Directory for user data (save games, save states, screenshots...)

        self.ls_users = []        # List of users
        self.f_volume = 1.0       # Sound volume

        self.s_cores_dir = ''     # Retroarch's cores dir

        if ps_file:
            self.read_yaml(ps_file)

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        # s_out = '<ProgramCfg>\n'
        # s_out += f'  .s_cache_dir:   {self.s_cache_dir}\n'
        # s_out += f'  .i_cache_size:  {self.i_cache_size}\n'
        # ROM directories
        # s_section = '  .ds_rom_dirs:  '
        # ls_values = [f'{s_system} => {self.ds_rom_dirs[s_system]}' for s_system in sorted(self.ds_rom_dirs.keys())]
        # s_out += string_helpers.section_generate(s_section, ls_values)
        # Patch directories
        #s_section = '  .ds_patch_dirs:'
        #ls_values = [f'{s_system} => {self.ds_patch_dirs[s_system]}' for s_system in sorted(self.ds_patch_dirs.keys())]
        #s_out += string_helpers.section_generate(s_section, ls_values)
        # Users
        #s_section = '  .ls_users:     '
        #ls_values = sorted(self.ls_users)
        #s_out += string_helpers.section_generate(s_section, ls_values)
        # Cores dir
        #s_out += f'  .s_cores_dir:   {self.s_cores_dir}\n'

        s_out = class_to_string.class_to_string(self)
        return s_out

    def read_yaml(self, ps_file):
        """
        Method to populate the object from an .ini file.

        :param ps_file: Path of the .ini file to be read.
        :type ps_file: Str

        :return: Nothing, the object will be populated in place.
        """

        with open(ps_file, 'r') as o_file:
            try:
                o_yaml = yaml.safe_load(o_file)
            except yaml.YAMLError as o_exception:
                print(o_exception)
                quit()

        s_cfg_dir = os.path.abspath(os.path.dirname(ps_file))

        # Window settings
        try:
            self.i_width = o_yaml['window']['width']
            self.i_height = o_yaml['window']['height']
            self.f_volume = o_yaml['window']['volume']
            self.s_theme = o_yaml['window']['theme']
        except KeyError:
            pass

        # Cache
        try:
            self.s_cache_dir = o_yaml['cache']['dir']
            self.i_cache_size = int(o_yaml['cache']['size'])
        except KeyError:
            pass

        # Data dirs
        try:
            self.s_dats_dir = o_yaml['data']['dats_dir']
            self.s_users_dir = o_yaml['data']['user_dir']
        except KeyError:
            pass

        # Patches
        try:
            ds_patch_dirs = o_yaml['patches']
            self.ds_patch_dirs = _absolutise_dict_of_paths(s_cfg_dir, ds_patch_dirs)
        except KeyError:
            pass

        # ROMs
        try:
            ds_rom_dirs = o_yaml['roms']
            self.ds_rom_dirs = _absolutise_dict_of_paths(s_cfg_dir, ds_rom_dirs)
        except KeyError:
            pass

        # Users
        try:
            ls_users = o_yaml['users']
            self.ls_users = [str(x_value) for x_value in ls_users]
        except KeyError:
            pass

        # Retroarch options
        try:
            s_cores_dir_yaml = o_yaml['retroarch']['cores_dir']
            self.s_cores_dir = _process_path(ps_root=s_cfg_dir, ps_path=s_cores_dir_yaml)
        except KeyError:
            pass

    def build_user_game_dir_path(self, po_rom_config):
        """
        Function to build the user data directory to store data. The path will be something along "X - Y - Z" where:

          X: Clean CRC32 of the ROM, "xxxxxxxx" if unknown.
          Y: CRC32 of the patch_file ps_name, "xxxxxxxx" if no patch_file is applied.
          Z: Name of the ROM lower-cased.

        :param po_rom_config:
        :type po_rom_config: romconfig.RomConfig

        :return: The full absolute path of user data dir
        :rtype: Str
        """
        s_full_path = os.path.join(self.s_cache_dir,
                                   'users',
                                   po_rom_config.s_user,
                                   po_rom_config.o_rom.o_platform.s_alias)
        return s_full_path

    def build_user_game_settings_path(self, po_rom_config):
        """
        Function to build the settings file path for a user.

        :param po_rom_config:
        :type po_rom_config: romconfig.RomConfig

        :param po_program_config:
        :type po_program_config: config.Config

        :return:
        :rtype: Str
        """
        s_dir = self.build_user_game_dir_path(po_rom_config=po_rom_config)
        o_rom = po_rom_config.o_rom
        s_file = f'{o_rom.s_ccrc32_safe} - {o_rom.s_name.lower()}.ini'
        return os.path.join(s_dir, s_file)

    def build_rom_install_dir_path(self, po_rom_config):
        """
        Function to build the installation dir path  for a romconfig.

        The path will be something along "X - Y - Z" where:

          X: Safe clean CRC32 of the ROM, "xxxxxxxx" if unknown.
          Y: CRC32 of the patch_file ps_name, "xxxxxxxx" if no patch_file is applied.
          Z: Name of the ROM lower-cased.

        :param po_rom_config:
        :type po_rom_config: romconfig.RomConfig

        :return: The full absolute path of romconfig installation.
        :rtype: Str
        """
        s_dir = self._build_romconfig_dir(po_rom_config)
        s_full_path = os.path.join(self.s_cache_dir, 'games', s_dir)
        return s_full_path

    def build_rom_install_game_settings(self, po_rom_config):
        """
        Function to build the settings file path for an installed game.

        :param po_rom_config:
        :type po_rom_config: romconfig.RomConfig

        :return:
        :rtype: Str
        """
        s_dir = self.build_rom_install_dir_path(po_rom_config=po_rom_config)
        s_file = 'settings.ini'
        return os.path.join(s_dir, s_file)

    @staticmethod
    def _build_romconfig_dir(po_rom_config):
        """
        Function to build the relative installation dir path for a romconfig.

        The path will be something along "X - Y - Z" where:

          X: Clean CRC32 of the ROM, "xxxxxxxx" if unknown.
          Y: CRC32 of the patch_file ps_name, "xxxxxxxx" if no patch_file is applied.
          Z: Name of the ROM lower-cased.

        :param po_rom_config:
        :type po_rom_config: romconfig.RomConfig

        :return: The full absolute path of romconfig installation.
        :rtype: Str
        """
        # Rom text
        #---------
        o_rom = po_rom_config.o_rom

        # Patch text
        #-----------
        o_patch = po_rom_config.o_patch
        s_patch_code = 'xxxxxxxx'
        if o_patch is not None:
            # In order to obtain the CRC32 of the patch_file title, we need to obtain a chain of bytes, which means we
            # first have to encode the text into a string of bytes.
            s_patch_code = o_patch.s_code

        s_dir = '%s - %s+%s - %s' % (o_rom.o_platform.s_alias,
                                     o_rom.s_ccrc32_safe,
                                     s_patch_code,
                                     po_rom_config.o_rom.s_name.lower())

        return s_dir


# Helper functions
#=======================================================================================================================
def _process_path(ps_root, ps_path):
    """
    Function to process a path by a) trying to expand "~", and b) convert relative paths to absolute.

    :param ps_root: Root to be prefixed to the path if it's not absolute.
    :type ps_root: Str

    :param ps_path: Path to be processed.
    :type ps_path: Str

    :return: The processed path.
    :rtype: Str
    """

    if ps_path.startswith('~'):
        s_result = os.path.expanduser(ps_path)
    else:
        s_result = os.path.abspath(os.path.join(ps_root, ps_path))

    return s_result


def _absolutise_dict_of_paths(ps_root, pds_paths):
    """
    Function to convert a dictionary of relative paths to a dictionary of absolute paths.

    :param ps_root:
    :type ps_root: Str

    :param pds_paths:
    :type pds_paths: Dict[Str:Str]

    :return:
    :rtype: Dict[Str:Str]
    """
    ds_abs_dict = {}
    for s_key in pds_paths.keys():
        ds_abs_dict[s_key] = _process_path(ps_root, pds_paths[s_key])

    return ds_abs_dict
