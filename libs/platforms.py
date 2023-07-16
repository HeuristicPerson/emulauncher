import codecs
import json
import os.path
import re

from . import string_helpers


# Classes
#=======================================================================================================================
class PlatformCfg:
    """
    Class to store information about a platform.

    :ivar ls_cores: List[Str]
    """
    def __init__(self, pdx_json={}):
        self.s_alias = ''         # Alias of the platform
        self.s_name = ''          # Full name of the platform
        self.f_aspect = 0.0       # Visual aspect ratio of the platform
        self.ls_region_pats = []  # ROM name patters that will trigger each of the console regions
        self.ls_regions = []      # List of available regions for the console
        self.lf_freqs = []        # List of available screen frequencies for the platform
        self.ls_cores = []        # Name of compatible cores
        self.ls_regions = []      # Regions of the console, typically with different bios and/or frequencies.

        if pdx_json:
            self._from_json_chunk(pdx_json)

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        s_out = '<_PlatformCfg>\n'
        s_out += f'  .s_alias:        {self.s_alias}\n'
        s_out += f'  .s_name:         {self.s_name}\n'
        s_out += f'  .f_aspect:       {self.f_aspect}\n'
        s_out += string_helpers.section_generate('  .ls_regions:    ', self.ls_regions)
        s_out += string_helpers.section_generate('  .lf_freqs:      ', self.lf_freqs)
        s_out += string_helpers.section_generate('  .ls_region_pats:', self.ls_region_pats)
        s_out += string_helpers.section_generate('  .ls_cores:      ', self.ls_cores)
        return s_out

    def _from_json_chunk(self, pdx_json):
        """
        Method to populate the object from a chunk of json data.

        :param pdx_json:
        :type pdx_json: Dict[Str:Union[Str,List,Int,Float]]

        :return: Nothing, the object will be populated in place.
        """
        self.s_alias = pdx_json['alias']
        self.s_name = pdx_json['name']
        self.f_aspect = pdx_json['aspect_ratio']
        self.lf_freqs = pdx_json['frequencies']
        self.ls_regions = pdx_json['regions']
        self.ls_region_pats = pdx_json['frequency_patterns']
        self.ls_cores = pdx_json['cores']

        # Some quick checks about the validity of the data
        #-------------------------------------------------
        i_regions = len(self.ls_regions)
        i_freqs = len(self.lf_freqs)
        i_pats = len(self.ls_region_pats)
        ti_set_lengths = (i_regions, i_freqs, i_pats)

        # The number of regions/frequencies/patterns is different
        if len(set(ti_set_lengths)) > 1:
            s_error = f'Different number of regions ({i_regions}), frequencies ({i_freqs}), and patterns ({i_pats})' \
                      f' for {self.s_alias}.'
            raise ValueError(s_error)

        # The number of regions is zero or negative
        if ti_set_lengths[0] < 1:
            s_error = f'The number of regions/frequencies/patterns must be at least 1'
            raise ValueError(s_error)

    def get_frequency_for_rom(self, ps_path):
        """
        Method to get the right frequency to be applied to certain ROM.
        :param ps_path: Path of the ROM.
        :type ps_path: Str

        :return: Screen refresh frequency to be used during the ROM emulation.
        :rtype: Float
        """
        s_rom_file = os.path.basename(ps_path)
        s_rom_name, _, s_rom_ext = s_rom_file.rpartition('.')

        # By default, the first frequency will be returned
        f_result = self.lf_freqs[0]

        # Then we start the process of trying to get a better frequency
        for f_freq, s_pattern in zip(self.lf_freqs, self.ls_region_pats):
            if re.search(s_pattern, s_rom_name, flags=re.IGNORECASE) is not None:
                f_result = f_freq
                break

        return f_result

    def get_region_form_rom(self, pu_path):
        """
        Function to get the default region to apply to certain ROM.
        :param pu_path:
        :return:
        """
        # TODO: Write region detection code (maybe it should be exactly the same as the frequency
        pass


# Functions
#=======================================================================================================================
def read_platforms_file(pu_file):
    """
    Function to read a platforms .json file and return a dictionary where the key is the platform alias, and the value
    is a platform object.

    :param pu_file: Path of the .json file to be read.
    :type pu_file: Str

    :return: A dictionary of platform objects where the key is the platform alias.
    :rtype: Dict[Str:PlatformCfg]
    """
    do_result = {}

    with codecs.open(pu_file, 'r', 'utf8') as o_file:
        ldx_data = json.load(o_file)

    for dx_data in ldx_data:
        o_platform = PlatformCfg(dx_data)
        do_result[o_platform.s_alias] = o_platform

    return do_result
    
