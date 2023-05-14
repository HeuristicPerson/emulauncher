import os

from . import platforms
from . import cores

# Common paths and dirs
s_SCRIPT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
s_TEST_DATA_DIR = os.path.join(s_SCRIPT_ROOT, 'test', 'test_data')


# Name and version of the script
s_PRG = 'EmuLaunch v1.0.2023-03-21'

# Main program configuration
s_MAIN_CFG_YAML = os.path.join(s_SCRIPT_ROOT, 'config.yaml')

# to_CORES_AVAILABLE = cores.get_cores(self.o_cfg.s_cores_dir, self.o_rom.o_platform.ls_cores)
#o_CFG = config.ProgramCfg()

# Dictionary with valid platform aliases and names
_s_platforms_file = os.path.join(os.path.join(s_SCRIPT_ROOT, 'data', 'platforms.json'))
do_PLATFORMS = platforms.read_platforms_file(_s_platforms_file)
