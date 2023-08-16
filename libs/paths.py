"""
Library to create and manipulate emulauncher paths.
"""

import os
import zlib

from . import config
from . import romconfig


# Main functions
#=======================================================================================================================
def build_rom_install_dir_path(po_rom_config, po_program_config):
    """
    Function to build the installation dir path  for a romconfig.

    The path will be something along "X - Y - Z" where:

      X: Safe clean CRC32 of the ROM, "xxxxxxxx" if unknown.
      Y: CRC32 of the patch_file ps_name, "xxxxxxxx" if no patch_file is applied.
      Z: Name of the ROM lower-cased.

    :param po_rom_config:
    :type po_rom_config: romconfig.RomConfig

    :param po_program_config:
    :type po_program_config: config.ProgramConfig

    :return: The full absolute path of romconfig installation.
    :rtype: Str
    """
    s_dir = _build_romconfig_dir(po_rom_config)
    s_full_path = os.path.join(po_program_config.s_cache_dir, 'games', s_dir)
    return s_full_path


def build_user_game_dir_path(po_rom_config, po_program_config):
    """
    Function to build the user data directory to store data. The path will be something along "X - Y - Z" where:

      X: Clean CRC32 of the ROM, "xxxxxxxx" if unknown.
      Y: CRC32 of the patch_file ps_name, "xxxxxxxx" if no patch_file is applied.
      Z: Name of the ROM lower-cased.

    :param po_rom_config:
    :type po_rom_config: romconfig.RomConfig

    :param po_program_config:
    :type po_program_config: config.ProgramConfig

    :return: The full absolute path of user data dir
    :rtype: Str
    """
    s_full_path = os.path.join(po_program_config.s_cache_dir,
                               'users',
                               po_rom_config.s_user,
                               po_rom_config.o_rom.o_platform.s_alias)
    return s_full_path


def build_user_game_settings_path(po_rom_config, po_program_config):
    """
    Function to build the settings file path for a user.

    :param po_rom_config:
    :type po_rom_config: romconfig.RomConfig

    :param po_program_config:
    :type po_program_config: config.Config

    :return:
    :rtype: Str
    """
    s_dir = build_user_game_dir_path(po_rom_config=po_rom_config, po_program_config=po_program_config)
    o_rom = po_rom_config.o_rom
    s_file = f'{o_rom.s_ccrc32_safe} - {o_rom.s_name.lower()}.ini'
    return os.path.join(s_dir, s_file)


def build_rom_install_game_settings(po_rom_config, po_program_config):
    """
    Function to build the settings file path for an installed game.

    :param po_rom_config:
    :type po_rom_config: romconfig.RomConfig

    :param po_program_config:
    :type po_program_config: config.Config

    :return:
    :rtype: Str
    """
    s_dir = build_rom_install_dir_path(po_rom_config=po_rom_config, po_program_config=po_program_config)
    s_file = 'settings.ini'
    return os.path.join(s_dir, s_file)


def build_rom_installed_flag_file_path(po_rom_config, po_program_config):
    """
    Empty text file created in the installation directory of ROM+Patch indicating the installation was successful.

    :param po_rom_config:
    :type po_rom_config: romconfig.RomConfig

    :param po_program_config:
    :type po_program_config: config.Config

    :return:
    :rtype: Str
    """
    s_dir = build_rom_install_dir_path(po_rom_config=po_rom_config, po_program_config=po_program_config)
    s_file = 'installed.txt'
    return os.path.join(s_dir, s_file)


def is_rom_installed(po_rom_config, po_program_config):
    """
    Function to check whether a ROM+Patch is installed or not.

    Two tests are performed: a) whether the installation directory of the ROM exists, b) whether a game
    :param po_rom_config:
    :param po_program_config:
    :return:
    """
    s_install_flag_file = build_rom_installed_flag_file_path(po_rom_config=po_rom_config,
                                                             po_program_config=po_program_config)
    return os.path.isfile(s_install_flag_file)


# Helper functions
#=======================================================================================================================
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
    # TODO: Add method to patches to produce a safe crc32 of their title
    o_patch = po_rom_config.o_patch
    s_patch_code = 'xxxxxxxx'
    if o_patch is not None:
        # In order to obtain the CRC32 of the patch_file title, we need to obtain a chain of bytes, which means we first
        # have to encode the text into a string of bytes.
        #s_patch_code = hex(zlib.crc32(o_patch.s_title.encode('utf8').lower()) & 0xffffffff)[-8:]
        s_patch_code = o_patch.s_code

    s_dir = '%s - %s+%s - %s' % (o_rom.o_platform.s_alias,
                                 o_rom.s_ccrc32_safe,
                                 s_patch_code,
                                 po_rom_config.o_rom.s_name.lower())

    return s_dir
