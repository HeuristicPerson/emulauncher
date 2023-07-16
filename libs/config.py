import configparser
import os.path

import yaml

from . import cons
from . import string_helpers


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
        self.ls_users = []        # List of users
        self.f_volume = 1.0       # Sound volume

        self.s_cores_dir = ''     # Retroarch's cores dir

        if ps_file:
            self.read_yaml(ps_file)

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        s_out = '<ProgramCfg>\n'

        s_out += f'  .s_cache_dir:   {self.s_cache_dir}\n'
        s_out += f'  .i_cache_size:  {self.i_cache_size}\n'

        # ROM directories
        s_section = '  .ds_rom_dirs:  '
        ls_values = [f'{s_system} => {self.ds_rom_dirs[s_system]}' for s_system in sorted(self.ds_rom_dirs.keys())]
        s_out += string_helpers.section_generate(s_section, ls_values)

        # Patch directories
        s_section = '  .ds_patch_dirs:'
        ls_values = [f'{s_system} => {self.ds_patch_dirs[s_system]}' for s_system in sorted(self.ds_patch_dirs.keys())]
        s_out += string_helpers.section_generate(s_section, ls_values)

        # Users
        s_section = '  .ls_users:     '
        ls_values = sorted(self.ls_users)
        s_out += string_helpers.section_generate(s_section, ls_values)

        # Cores dir
        s_out += f'  .s_cores_dir:   {self.s_cores_dir}\n'

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
        self.i_width = o_yaml['window']['width']
        self.i_height = o_yaml['window']['height']
        self.f_volume = o_yaml['window']['volume']
        self.s_theme = o_yaml['window']['theme']

        # Cache
        self.s_cache_dir = o_yaml['cache']['dir']
        self.i_cache_size = int(o_yaml['cache']['size'])

        # Data dirs
        self.s_dats_dir = o_yaml['data']['dats_dir']

        self.ds_patch_dirs = _absolutise_dict_of_paths(s_cfg_dir, o_yaml['patches'])
        self.ds_rom_dirs = _absolutise_dict_of_paths(s_cfg_dir, o_yaml['roms'])

        # Users
        self.ls_users = [str(x_value) for x_value in o_yaml['users']]

        # Retroarch options
        s_cores_dir_yaml = o_yaml['retroarch']['cores_dir']
        if s_cores_dir_yaml.startswith('~'):
            s_cores_dir = os.path.expanduser(s_cores_dir_yaml)
        else:
            s_cores_dir = _absolutise_relative_path(s_cfg_dir, s_cores_dir_yaml)

        self.s_cores_dir = s_cores_dir


# Helper functions
#=======================================================================================================================
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
        ds_abs_dict[s_key] = _absolutise_relative_path(ps_root, pds_paths[s_key])

    return ds_abs_dict


def _absolutise_relative_path(ps_root, ps_path):
    """
    Function to convert relative paths from config file into absolute paths.

    :param ps_root:
    :param ps_path:
    :return:
    """
    return os.path.abspath(os.path.join(ps_root, ps_path))
