#!/usr/bin/env python3

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
import libs.install as install
import libs.paths as paths
import libs.patches as patches
import libs.roms as roms
from libs.parallel import ParallelTask


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
        self._o_pbar = None

        self._o_status_block = self._o_theme.build_status_block(po_rom, self._to_available_cores)

        self._lo_items += [self._o_theme.build_title(po_rom.s_name),
                           self._o_theme.build_subtitle(po_rom.o_platform.s_name),
                           self._o_status_block]

        # List to store tasks to be running in the background. Used, for example to run installation of games.
        self._lo_parallel_tasks = []

        # Defining schedules
        # pyglet.clock.schedule_interval(self.schedule_create_destroy_progress_bar, 1.0)

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

    def on_draw(self, **px_args):
        # First, we remove items that are not alive (we do this on every cycle)
        self._lo_items = [o_item for o_item in self._lo_items if o_item.b_alive]



        # If there is any parallel task running:
        #
        #   1. We launch the task(s)
        #   2. We create a progress bar object
        #   3. We obtain the progress of each task and their status message. With them, we build global progress and msg
        #   4. We make the progress bar to show that information.

        # Finally, we draw everything
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

    def callback_menu_1_play(self):
        """
        Callback function to launch a game with the current configuration.

        The function should check:

            1. Whether the game is already "installed" or not.
            2. If it's installed, does it have the same configuration required? otherwise it has to be reinstalled.

        :return: Nothing.
        """
        _register_action('play')
        o_romconfig = self._o_status_block.o_config

        # Printing the settings to the terminal
        for s_line in o_romconfig.nice_format().splitlines(False):
            print(f'  < {s_line}')

        # When the user launches the game, the configuration is saved in the user's directory. It will overwrite
        # anything already existing with no questions.
        s_user_settings_file = paths.build_user_game_settings(po_rom_config=o_romconfig,
                                                              po_program_config=self.o_cfg)
        self._o_status_block.o_config.save_to_disk(s_user_settings_file)

        # Then we check whether the game is already installed and, in that case, whether it has the same configuration
        b_installed = paths.is_rom_installed(po_rom_config=o_romconfig,
                                             po_program_config=self.o_cfg)

        # TODO: Probably the same applies to running the game but that queue is ran out of the menu system.
        # If the games is not installed, we install it
        if not b_installed:
            print(f'  < Installing...')
            # We killed the active menu (if any, so it'll be removed in the next loop).
            if self._o_menu is not None:
                self._o_menu.kill()

            # --- test code ---
            # We need to create a thread where the actual installation is happening. We can't directly pass the progress
            # object, so the installation can update the progress and message because the progress bar contains some
            # pyglet objects (Label, rectangles, background color...) that are not compatible with threading. Instead,
            # we pass a pure text Status object that will be updated by the installation process.
            o_parallel_task_definition = ParallelTask(po_callback=install.install,
                                                      plx_args=['romconfig_here'])
            self._lo_parallel_tasks.append(o_parallel_task_definition)

            # TODO: Install the game (external function)
            #  --- PSEUDO-CODE ---
            #  1. disable controls
            #  2. install the game
            #  3. activate controls (actually, not needed, because we're just running the game after
            #  ------- end -------

        # If the game is installed including the wanted patch, we simply need to replace the settings file for the user
        # settings
        #s_install_settings_file = paths.build_rom_install_game_settings(po_rom_config=o_romconfig,
        #                                                                po_program_config=self.o_cfg)
        #shutil.copyfile(s_user_settings_file, s_install_settings_file)

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
        _register_action(f'user: {ps_user}')

        self._o_status_block.s_user = ps_user

        # When the user is selected, we check whether it already had a configuration created for the game and load it.
        s_user_saved_settings = paths.build_user_game_settings(po_rom_config=self._o_status_block.o_config,
                                                               po_program_config=self.o_cfg)

        if os.path.isfile(s_user_saved_settings):
            print('  < User config found, loading')
            ls_errors = self._o_status_block.o_config.load_from_disk(ps_file=s_user_saved_settings,
                                                                     po_prog_cfg=self.o_cfg)
            if ls_errors:
                for s_error in ls_errors:
                    print(f'  < {s_error}')

        self.create_menu_rom_options()

    def callback_menu_3_choose_patch(self, po_patch):
        """
        Callback used when a patch is selected in the menu.

        :param po_patch:
        :type po_patch: patches.Patch

        :return: Nothing
        """
        # Registering the action
        #-----------------------
        if po_patch is None:
            s_patch = 'none'
        else:
            s_patch = po_patch.s_title
        _register_action(f'patch: {s_patch}')

        # Storing the selected patch information
        #---------------------------------------
        self._o_status_block.o_patch = po_patch
        self.create_menu_rom_options()

    def callback_menu_3_choose_region(self, ps_region):
        """
        Callback used when a region is selected in the menu.

        :param ps_region: Name of the region to be used.
        :type ps_region: Str

        :return: Nothing
        """
        _register_action(f'region: {ps_region}')
        self._o_status_block.s_region = ps_region

    def callback_menu_3_choose_frequency(self, pf_refresh):
        """
        Callback used when a frequency is selected in the menu.

        :param pf_refresh:
        :type pf_refresh: Float

        :return: Nothing
        """
        _register_action(f'refresh: {pf_refresh}')

        self._o_status_block.f_refresh = pf_refresh
        self.create_menu_rom_options()

    def callback_menu_3_choose_core(self, po_core):
        """
        Function executed when the user selects a core in the cores menu.

        :param po_core:
        :type po_core: cores.Core

        :return: Nothing.
        """
        _register_action(f'core: {po_core.s_name}')
        self._o_status_block.o_core = po_core

    def schedule_updater(self, pf_delta_t):
        """
        Method to run the update of the progress bar.

        :param pf_delta_t: Delta time since last run of the scheduler. Required by pyglet but not used in this program.
        :type pf_delta_t: Float

        :return: Nothing.
        """
        self._update_parallel_tasks()
        self._update_progress_bar()

    def _update_progress_bar(self):
        """
        Method to create/destroy/manage the progress bar.
        :return: Nothing.
        """
        # Creation and destruction of the progress bar
        #---------------------------------------------
        # Progress bar is created when parallel task are defined, or destroyed when there are no parallel tasks.
        if (self._o_pbar is None) and self._lo_parallel_tasks:
            # print('  < Creating progress bar...')
            self._o_pbar = self._o_theme.build_progress_bar()
            self._lo_items.append(self._o_pbar)
        elif (self._o_pbar is not None) and not self._lo_parallel_tasks:
            # print('  < Destroying progress bar...')
            self._o_pbar.kill()
            self._o_pbar = None

        # Updating the progress bar
        #--------------------------
        if (self._o_pbar is not None) and self._lo_parallel_tasks:
            lf_progress = [o_task.f_progress for o_task in self._lo_parallel_tasks]
            ls_messages = [o_task.s_status for o_task in self._lo_parallel_tasks]
            s_message = ', '.join(ls_messages)

            self._o_pbar.s_message = s_message
            self._o_pbar.f_progress = sum(lf_progress) / len(lf_progress)

    def _update_parallel_tasks(self):
        """
        Method to process parallel tasks.

        :return: Nothing.
        """
        # TODO: Add extra parameter to parallel tasks so they can close the window if required
        self._lo_parallel_tasks = [o_task for o_task in self._lo_parallel_tasks if not o_task.b_completed]
        for o_task in self._lo_parallel_tasks:
            if not o_task.b_started:
                o_task.start()

# Helper functions
#=======================================================================================================================
def _register_action(ps_action):
    """
    Function to print info about the selected menu items to the terminal
    :param ps_action:
    :type ps_action: Str

    :return: Nothing, output will be printed.
    """
    s_msg = f'>>> {ps_action}'
    print(s_msg)


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

    # TODO: Add an output object to be updated with the info for the rom to be launched.
    o_window = MainWindow(po_rom=o_rom, po_cfg=o_main_cfg)

    # TODO: Maybe it's better to simply have one update schedule and from it, calling other methods for cleaner code.
    pyglet.clock.schedule_interval(o_window.schedule_updater, 0.2)
    pyglet.app.run(1/30)

    # TODO: Run launching of the installed ROM here.
    print('AFTER CLOSING PYGLET')
