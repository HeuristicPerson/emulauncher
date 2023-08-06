import os

from . import platforms


# Common paths and dirs
s_SCRIPT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
s_TEST_DATA_DIR = os.path.join(s_SCRIPT_ROOT, 'test', 'test_data')

# Output directory for tests that need to write data
s_TEST_DATA_OUT = '/tmp/emulauncher_tests'

# Name and version of the script
s_PRG = 'EmuLaunch v1.0.2023-03-21'


# Main program configuration
s_MAIN_CFG_YAML = os.path.join(s_SCRIPT_ROOT, 'config.yaml')


# Dictionary with valid platform aliases and names
_s_PLATFORMS_FILE = os.path.join(os.path.join(s_SCRIPT_ROOT, 'data', 'platforms.json'))
do_PLATFORMS = platforms.read_platforms_file(_s_PLATFORMS_FILE)
