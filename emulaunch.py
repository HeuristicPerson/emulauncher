"""
Script to launch a ROM from certain platform.
"""

import argparse
import os
import time

import pyglet

import libs.cons as cons
import libs.config as config
import libs.cores as cores
import libs.gui as gui_theme
import libs.paths as paths
import libs.patches as patches
import libs.roms as roms
import libs.romconfig as romconfig


# Classes
#=======================================================================================================================
class _CmdArgs:
    """
    Class to read and store command line arguments.
    """
    def __init__(self):
        self.s_rom = ''     # Path of the ROM to be executed
        self.s_system = ''  # Platform of the ROM to be executed

        o_parser = argparse.ArgumentParser()
        o_parser.add_argument('system',
                              action='store',
                              choices=cons.do_PLATFORMS.keys(),
                              help='Platform of the ROM to be executed.')
        o_parser.add_argument('rom',
                              action='store',
                              help='Full path of the ROM to be executed')

        o_args = o_parser.parse_args()

        # TODO: Add input validation
        self.s_system = o_args.system
        self.s_rom = o_args.rom

    def nice_format(self):
        """
        Method to produce a text representation of the object with a nice format ready to be printed to screen.

        :return: A text representation of the instance.
        :rtype: Str
        """
        s_system_desc = cons.do_PLATFORMS[self.s_system].s_name
        s_out = ''
        s_out += f'┌[Arguments]─────────────\n'
        s_out += f'├      System: {self.s_system} - {s_system_desc}\n'
        s_out += f'├         ROM: {self.s_rom}\n'
        s_out += f'└────────────────────────'
        return s_out


class MainWindow(pyglet.window.Window):
    def __init__(self, po_rom, po_cfg):
        """
        :param po_rom:
        :type po_rom: roms.Rom

        :param po_cfg:
        :type po_cfg: config.ProgramCfg
        """
        s_theme_yaml = os.path.join(cons.s_SCRIPT_ROOT, 'themes', o_main_cfg.s_theme, 'theme.yaml')
        self._o_theme = gui_theme.Theme(s_theme_yaml, po_rom)
        pyglet.window.Window.__init__(self,
                                      width=self._o_theme.i_width,
                                      height=self._o_theme.i_height,
                                      caption=cons.s_PRG,
                                      resizable=True,
                                      vsync=True)

        self.o_cfg = po_cfg
        self.o_rom = po_rom

        # Initialization
        #---------------
        self._to_available_cores = cores.get_cores(self.o_cfg.s_cores_dir, self.o_rom.o_platform.ls_cores)
        self._lo_items = []
        self.s_user = ''
        self._o_menu = None

        # Setting audio volume
        #---------------------
        o_listener = pyglet.media.get_audio_driver().get_listener()
        o_listener.volume = self.o_cfg.f_volume

        # Creation of the background
        #---------------------------
        o_bg_img = self._o_theme.build_background_image(po_rom=po_rom)
        if o_bg_img is not None:
            self._lo_items.append(o_bg_img)

        self.create_menu_users()
        self.o_pbar = None

        self._o_status_block = self._o_theme.build_status_block(po_rom, self._to_available_cores)

        self._lo_items += [self._o_theme.build_title(po_rom.s_name),
                           self._o_theme.build_subtitle(po_rom.o_platform.s_name),
                           self._o_status_block]

    def create_menu_patch(self):
        # Sending kill "signal" to already existing menu
        if self._o_menu is not None:
            self._o_menu.kill()

        # Getting all available patches for selected ROM
        #-----------------------------------------------
        s_patches_dir = self.o_cfg.ds_patch_dirs[self.o_rom.o_platform.s_alias]
        lo_patches = patches.get_patches(s_patches_dir, self.o_rom)

        o_menu = self._o_theme.build_menu()
        o_menu.s_title = 'Choose patch'
        o_menu.add_option(ps_text='None', pc_callback=self.callback_menu_3_choose_patch, pdx_args={'po_patch': None})
        for o_patch in lo_patches:
            o_menu.add_option(ps_text=o_patch.s_name, pc_callback=self.callback_menu_3_choose_patch,
                              pdx_args={'po_patch': o_patch})

        o_menu.add_option(ps_text='Back', pc_callback=self.create_menu_rom_options)
        self._o_menu = o_menu
        self._lo_items.append(o_menu)

    def create_menu_core(self):
        if self._o_menu is not None:
            self._o_menu.kill()

        # Getting all cores for selected ROM and generating the options for them in the menu
        #-----------------------------------------------------------------------------------
        #to_available_cores = cores.get_cores(self.o_cfg.s_cores_dir, self.o_rom.o_platform.ls_cores)

        o_menu = self._o_theme.build_menu()
        o_menu.s_title = 'Choose emulation core'
        for i_core, o_core in enumerate(self._to_available_cores):
            b_default = False
            if i_core == 0:
                b_default = True

            o_menu.add_option(ps_text=o_core.s_name, pc_callback=self.callback_menu_3_choose_core,
                              pdx_args={'po_core': o_core}, pb_default=b_default)
        o_menu.add_option(ps_text='Back', pc_callback=self.create_menu_rom_options)

        self._o_menu = o_menu
        self._lo_items.append(o_menu)

    def create_menu_refresh_rate(self):
        if self._o_menu is not None:
            self._o_menu.kill()

        o_menu = self._o_theme.build_menu()
        o_menu.s_title = 'Screen refresh rate'

        f_refresh_auto = self.o_rom.f_refresh_auto

        for f_freq in set(self.o_rom.o_platform.lf_freqs):
            b_default = False
            if f_freq == f_refresh_auto:
                b_default = True

            o_menu.add_option(ps_text=f'{f_freq} Hz', pc_callback=self.callback_menu_3_choose_frequency,
                              pdx_args={'pf_refresh': f_freq},
                              pb_default=b_default)

        o_menu.add_option(ps_text='Back', pc_callback=self.create_menu_rom_options)
        self._o_menu = o_menu
        self._lo_items.append(o_menu)

    def create_menu_region(self):
        if self._o_menu is not None:
            self._o_menu.kill()

        o_menu = self._o_theme.build_menu()
        o_menu.s_title = 'Console region'

        s_region_auto = self.o_rom.s_region_auto

        for s_region in set(self.o_rom.o_platform.ls_regions):
            b_default = False
            if s_region == s_region_auto:
                b_default = True

            o_menu.add_option(ps_text=f'{s_region}', pc_callback=self.callback_menu_3_choose_region,
                              pdx_args={'ps_region':  s_region},
                              pb_default=b_default)

        o_menu.add_option(ps_text='Back', pc_callback=self.create_menu_rom_options)
        self._o_menu = o_menu
        self._lo_items.append(o_menu)

    def create_menu_users(self):
        """
        Method to create the menu with users
        """
        # TODO: Reset all settings in the StatusBlock, so we reset the status of the program to its initial state

        if self._o_menu is not None:
            self._o_menu.kill()

        o_menu = self._o_theme.build_menu()
        o_menu.s_title = 'Choose player:'

        for i_user, s_user in enumerate(self.o_cfg.ls_users):
            b_default = False
            if i_user == 0:
                b_default = True

            o_menu.add_option(ps_text=s_user, pc_callback=self.callback_menu_1_choose_user,
                              pdx_args={'ps_user': s_user.lower()},
                              pb_default=b_default)

        o_menu.add_option(ps_text='Exit', pc_callback=self.callback_menu_1_exit)

        self._o_menu = o_menu
        self._lo_items.append(o_menu)

    def create_menu_rom_options(self):
        """
        Method to create the menu where the main options for the current ROM are chosen.
        """
        if self._o_menu is not None:
            self._o_menu.kill()

        o_menu = self._o_theme.build_menu()
        o_menu.add_option(ps_text='Play/Install and play', pc_callback=self.callback_menu_1_play)
        # TODO: Create region menu only if the system has several regions
        o_menu.add_option(ps_text='Region', pc_callback=self.create_menu_region)
        # TODO: Create refresh rate menu only if the system has several refresh rates
        o_menu.add_option(ps_text='Refresh rate', pc_callback=self.create_menu_refresh_rate)
        o_menu.add_option(ps_text='Core', pc_callback=self.create_menu_core)
        o_menu.add_option(ps_text='Patch', pc_callback=self.create_menu_patch)
        o_menu.add_option(ps_text='Back', pc_callback=self.create_menu_users)

        self._o_menu = o_menu
        self._lo_items.append(o_menu)

    def update(self):
        # Basically, we will remove items that are not alive
        self._lo_items = [o_item for o_item in self._lo_items if o_item.b_alive]

    def on_draw(self, **px_args):
        self.clear()

        for o_elem in self._lo_items:
            o_elem.draw(**px_args)

    def on_key_press(self, symbol, modifiers):
        # IMPORTANT COMMENT: I need to iterate over all elements by index using the range function because the list of
        # elements will be expanded by the inputs from keyboard (e.g. a menu option will create a new menu). A plain
        # "for element in list" loop would iterate over the newly added elements as well and that would be problematic
        # for menus: You press ENTER in menu A, which generates menu B... and the for loop would send ENTER to the newly
        # created menu B.
        #
        # To avoid that problem, we iterate just over the original list of elements present in the list by the use of
        # range and accessing the elements by their position.
        for i_elem in range(len(self._lo_items)):
            self._lo_items[i_elem].on_key_press(symbol, modifiers)

        # At the moment, the menu will only update every time the user presses a key
        self.update()

    def callback_menu_1_play(self):
        """
        Callback function to launch a game with the current configuration.

        The function should check:

            1. Whether the game is already "installed" or not.
            2. If it's installed, does it have the same configuration required? otherwise it has to be reinstalled.

        :return: Nothing.
        """
        # --- test code ---
        #s_save_file = '/tmp/foo.file'
        #self._o_status_block.o_config.save_to_disk(s_save_file)

        # When the user launches the game, the configuration is saved in the user's directory
        s_user_save_file = paths.build_romconfig_save_file(po_romconfig=self._o_status_block.o_config,
                                                           po_program_config=self.o_cfg)
        #self._o_status_block.o_config.save_to_disk(s_user_save_file)
        # ------ end ------



        # TODO: Replace pseudo-code below with real one.
        if b_game_installed:
            if chosen_config == saved_config:
                pass
                #-> LAUNCH GAME
            else:
                pass
                # -> RE-INSTALL GAME
                # -> LAUNCH GAME

        # --- test code ---
        print('--- LAUNCHING GAME ---')
        # ------ end ------

    @staticmethod
    def callback_menu_1_exit():
        """
        Callback function for 1st menu exit option.
        """
        time.sleep(1)
        quit()

    def callback_menu_1_choose_user(self, ps_user):
        """
        Callback function for 1st menu user selection.
        """
        self._o_status_block.s_user = ps_user
        self.create_menu_rom_options()

        # TODO: Load existing configurations:
        #
        #   0) Default configuration  <= NOT NEEDED, it's loaded when the program is initialised
        #
        #   1) Installed game for the user (when we install, we save the configuration)
        #   2) User saved settings (Even when game is not installed, user has game settings saved
        #   3) Default settings for ROM

    def callback_menu_3_choose_patch(self, po_patch):
        """
        Callback used when a patch is selected in the menu.

        :param po_patch:
        :type po_patch: patches.Patch

        :return: Nothing
        """
        self._o_status_block.o_patch = po_patch
        self.create_menu_rom_options()

    def callback_menu_3_choose_region(self, ps_region):
        """
        Callback used when a region is selected in the menu.

        :param ps_region: Name of the region to be used.
        :type ps_region: Str

        :return: Nothing
        """
        self._o_status_block.s_region = ps_region

    def callback_menu_3_choose_frequency(self, pf_refresh):
        """
        Callback used when a frequency is selected in the menu.

        :param pf_refresh:
        :type pf_refresh: Float

        :return: Nothing
        """
        self._o_status_block.f_refresh = pf_refresh
        self.create_menu_rom_options()

    def callback_menu_3_choose_core(self, po_core):
        """
        Function executed when the user selects a core in the cores menu.

        :param po_core:
        :type po_core: cores.Core

        :return: Nothing.
        """
        self._o_status_block.o_core = po_core


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    s_msg = '%s\n%s' % (cons.s_PRG, '='*len(cons.s_PRG))
    print(s_msg)

    # TODO: Move the main config reading to the constants file
    o_main_cfg = config.ProgramCfg(cons.s_MAIN_CFG_YAML)

    o_cmd_args = _CmdArgs()
    print(o_cmd_args.nice_format())

    s_dat_path = os.path.join(o_main_cfg.s_dats_dir, f'{o_cmd_args.s_system}.dat')

    o_rom = roms.Rom(ps_platform=o_cmd_args.s_system, ps_path=o_cmd_args.s_rom, ps_dat=s_dat_path)
    print(o_rom.nice_format())

    o_window = MainWindow(po_rom=o_rom, po_cfg=o_main_cfg)
    pyglet.app.run()
