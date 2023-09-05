import codecs
import os
import yaml
import sys

import pyglet

from . import class_to_string
from . import menu
from . import romconfig
from . import roms


# Classes
#=======================================================================================================================
class Theme:
    def __init__(self, ps_yaml, po_rom=None):
        """
        :param ps_yaml:
        :type ps_yaml: Str

        :param po_rom: Rom object with all the information about the ROM to be launched.
        :type po_rom: roms.Rom
        """
        self._s_root_dir = os.path.dirname(ps_yaml)
        self.i_width = 640
        self.i_height = 480

        self.o_menu_theme = _MenuTheme()
        self.o_header_theme = _HeaderTheme()
        self.o_prog_bar_theme = _ProgBarTheme()
        self.o_status_block_theme = _StatusBlockTheme()

        if ps_yaml:
            self.read_yaml(ps_yaml)

        # Loading of fonts included with the theme
        pyglet.font.add_directory(self._s_root_dir)

        # Loading of theme sounds
        self._o_sound_bank = _SoundBank(self._s_root_dir)

    def __str__(self):
        """
        :return: A text representation of the theme object.
        :rtype: Str
        """

        s_out = class_to_string.class_to_string(self)
        return s_out

    def read_yaml(self, ps_file):
        """
        Method to populate the theme from a .yaml file.

        :param ps_file: Path of the file containing the configuration of the theme.
        :type ps_file: Str

        :return: Nothing
        """
        with codecs.open(ps_file, 'r', 'utf8') as o_file:
            try:
                dx_yaml = yaml.safe_load(o_file)
            except yaml.YAMLError as o_exception:
                print(o_exception)
                sys.exit(1)

        # TODO: Move this reading of global options to a different function with a try/except so we can code easy testunits
        # TODO: Improve these try/excepts below so I'm able to catpure errors, but also being able to ignore them for
        # debugging reasons and unit tests.
        try:
            self.i_width = dx_yaml['window']['width']
            self.i_height = dx_yaml['window']['height']
        except KeyError:
            pass

        try:
            self.o_header_theme.read_yaml(dx_yaml['header'])
        except KeyError:
            pass

        try:
            self.o_menu_theme.read_yaml(dx_yaml['menu'])
        except KeyError:
            pass

        try:
            self.o_prog_bar_theme.read_yaml(dx_yaml['progress_bar'])
            self.o_prog_bar_theme.i_bg_width = self.i_width
            self.o_prog_bar_theme.i_bg_height = self.i_height

        except KeyError:
            pass

        try:
            self.o_status_block_theme.read_yaml(dx_yaml['status_block'])
        except KeyError:
            pass

    def build_background_image(self, po_rom=''):
        """
        Method to get the path of the background image for the menu.

        :param po_rom: Rom object containing all the information about the ROM to be launched.
        :type po_rom: roms.Rom

        :return: The path of the background image to be used in the menu system.
        :rtype: Str
        """
        s_bg_file = ''
        ts_bg_candidates = (f'background_{po_rom.o_platform.s_alias}_{po_rom.s_ccrc32}.jpg',
                            f'background_{po_rom.o_platform.s_alias}.jpg',
                            'background.jpg')

        for s_candidate in ts_bg_candidates:
            s_full_path = os.path.join(self._s_root_dir, s_candidate)
            if os.path.isfile(s_full_path):
                s_bg_file = s_full_path

        o_img = None
        if s_bg_file:
            o_img = _Image(s_bg_file, pi_x=0, pi_y=0)

        return o_img

    def build_title(self, ps_text):
        """
        Method to build the main title.
        """
        o_label = _Label(text=ps_text,
                         font_name=self.o_header_theme.s_title_font,
                         font_size=self.o_header_theme.i_title_font_size,
                         color=(255, 255, 255, 255),
                         x=self.o_header_theme.ti_title_pos[0],
                         y=self.o_header_theme.ti_title_pos[1],
                         anchor_x=self.o_header_theme.ts_title_align[0],
                         anchor_y=self.o_header_theme.ts_title_align[1],
                         width=self.o_header_theme.i_title_width, multiline=True)
        return o_label

    def build_subtitle(self, ps_text):
        """
        Method to build the subtitle.
        """
        o_label = _Label(text=ps_text,
                         font_name=self.o_header_theme.s_subtitle_font,
                         font_size=self.o_header_theme.i_subtitle_font_size,
                         color=self.o_header_theme.ti_subtitle_color,
                         x=self.o_header_theme.ti_subtitle_pos[0],
                         y=self.o_header_theme.ti_subtitle_pos[1],
                         anchor_x=self.o_header_theme.ts_subtitle_align[0],
                         anchor_y=self.o_header_theme.ts_subtitle_align[1],
                         width=self.o_header_theme.i_subtitle_width, multiline=True)
        return o_label

    def build_menu(self):
        o_menu = _Menu(self.o_menu_theme, po_sound_bank=self._o_sound_bank)
        return o_menu

    def build_progress_bar(self):
        """
        Method to build and return a progress bar object.
        :return:
        """
        o_progress_bar = _ProgressBar(po_theme=self.o_prog_bar_theme)
        return o_progress_bar

    def build_status_block(self, po_rom=None, pto_cores=()):
        """
        Method to build the status block.

        :param po_rom: Rom object including all the information about the ROM selected.
        :type po_rom: roms.Rom

        :param pto_cores: Tuple with cores found in the system
        :type pto_cores: Tuple[cores.Core]
        """
        o_status_block = _StatusBlock(self.o_status_block_theme)

        o_status_block.o_rom = po_rom
        o_status_block.o_patch = None
        o_status_block.o_config_default = romconfig.generate_default_cfg(po_rom, pto_cores)

        # We reset the configuration so every value will be set as the default config.
        o_status_block.reset_config()

        return o_status_block


class _MenuTheme:
    """
    Class to store information about theming a menu. The only method for the class will be the one to read information
    from a .yaml data chunk.
    """
    def __init__(self, po_navigate_sound=None):
        # Menu title
        self.ti_title_pos = (300, 250)
        self.i_vert_spacing = 24
        self.i_title_size = 24
        self.s_title_font = 'Arial'
        self.ti_title_color = (255, 255, 255, 255)
        self.ts_title_align = ('center', 'center')

        # Menu options
        self.ti_option_pos = (300, 220)  # Position of the first menu option
        self.i_option_size = 14
        self.s_option_font = 'Arial'
        self.ti_option_color = (180, 255, 180, 255)
        self.ti_option_color_default = (0, 255, 0)
        self.ti_option_color_active = (255, 0, 0, 255)
        self.ts_option_align = ('center', 'center')

        # --- test code ---
        self.o_navigate_sound = po_navigate_sound
        # ------ end ------

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        s_out = '<_MenuTheme>\n'
        s_out += f'  .ti_title_pos:           {self.ti_title_pos}\n'
        s_out += f'  .ti_title_size:          {self.i_title_size}\n'
        s_out += f'  .s_title_font:           {self.s_title_font}\n'
        s_out += f'  .s_title_align:          {self.ts_title_align}\n'
        s_out += f'  .ti_title_color:         {self.ti_title_color}\n'
        s_out += f'  .ti_option_pos:          {self.ti_option_pos}\n'
        s_out += f'  .i_option_size:          {self.i_option_size}\n'
        s_out += f'  .s_option_font:          {self.s_option_font}\n'
        s_out += f'  .ti_option_color:        {self.ti_option_color}\n'
        s_out += f'  .ti_option_color_active: {self.ti_option_color_active}\n'
        s_out += f'  .ts_option_align:        {self.ts_option_align}\n'
        s_out += f'  .f_vert_spacing:         {self.i_vert_spacing}'
        return s_out

    def read_yaml(self, pdx_yaml):
        """
        Method to populate the instance from a chunk of yaml data.

        :param pdx_yaml:
        :type pdx_yaml: Dict

        :return: Nothing
        """
        # Title theme
        self.ti_title_pos = _int_tuple(_add_tuples(pdx_yaml['position'], pdx_yaml['title']['position']))
        self.s_title_font = pdx_yaml['title']['font']
        self.i_title_size = pdx_yaml['title']['size']
        self.ts_title_align = pdx_yaml['title']['align']
        self.ti_title_color = _int_tuple(pdx_yaml['title']['color'])

        # Options theme
        self.ts_option_align = pdx_yaml['option']['align']
        self.ti_option_pos = _int_tuple(_add_tuples(pdx_yaml['position'], pdx_yaml['option']['position']))
        self.ti_option_color = _int_tuple(pdx_yaml['option']['color'])
        self.ti_option_color_active = _int_tuple(pdx_yaml['option']['color_active'])
        self.ti_option_color_default = _int_tuple(pdx_yaml['option']['color'])
        self.i_vert_spacing = pdx_yaml['option']['vert_spacing']
        self.s_option_font = pdx_yaml['option']['font']
        self.i_option_size = pdx_yaml['option']['size']


class _FieldAndValueTheme:
    """
    Class to store information about a FieldAndValue theme.

    :ivar ti_field_position: Tuple[Int, Int]
    :ivar s_field_font: Str
    :ivar i_field_size: Int
    :ivar ti_field_color: Tuple[Int, Int, Int, Int]
    :ivar ts_field_align: Tuple[Str, Str]

    :ivar ti_value_position: Tuple[Int, Int]
    :ivar s_value_font: Str
    :ivar i_value_size: Int
    :ivar ti_value_color: Tuple[Int, Int, Int, Int]
    :ivar ts_value_align: Tuple[Str, Str]
    """
    def __init__(self):
        self.ti_field_position = (100, 100)
        self.s_field_font = 'Arial'
        self.i_field_size = 16
        self.ti_field_color = (255, 255, 255, 255)
        self.ts_field_align = ('center', 'center')

        self.ti_value_position = (140, 100)
        self.s_value_font = 'Arial'
        self.i_value_size = 16
        self.ti_value_color = (255, 255, 255, 255)
        self.ti_value_color_alt = (255, 0, 0, 0)
        self.ts_value_align = ('center', 'center')


class _HeaderTheme:
    def __init__(self):
        # Title settings
        self.ti_title_pos = (300, 300)
        self.i_title_font_size = 32
        self.s_title_font = 'Arial'
        self.ti_title_color = (255, 255, 255, 255)
        self.ts_title_align = ('left', 'bottom')
        self.i_title_width = 640

        # Sup title settings
        self.ti_subtitle_pos = (300, 300)
        self.i_subtitle_font_size = 32
        self.s_subtitle_font = 'Arial'
        self.ti_subtitle_color = (255, 255, 255, 255)
        self.ts_subtitle_align = ('left', 'bottom')
        self.i_subtitle_width = 640

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        s_out = '<_HeaderTheme>\n'
        s_out += f'  .ti_title_pos:         {self.ti_title_pos}\n'
        s_out += f'  .ts_title_align:       {self.ts_title_align}\n'
        s_out += f'  .s_title_font:         {self.s_title_font}\n'
        s_out += f'  .i_title_font_size:    {self.i_title_font_size}\n'
        s_out += f'  .ti_title_color:       {self.ti_title_color}\n'
        s_out += f'  .i_title_width:        {self.i_title_width}\n'
        s_out += f'  .ti_subtitle_pos:      {self.ti_subtitle_pos}\n'
        s_out += f'  .ts_subtitle_align:    {self.ts_subtitle_align}\n'
        s_out += f'  .i_subtitle_font_size: {self.i_subtitle_font_size}\n'
        s_out += f'  .s_subtitle_font:      {self.s_subtitle_font}\n'
        s_out += f'  .ti_subtitle_color:    {self.ti_subtitle_color}\n'
        s_out += f'  .i_subtitle_width:     {self.i_subtitle_width}\n'
        return s_out

    def read_yaml(self, pdx_yaml):
        """
        :param pdx_yaml:
        :type pdx_yaml: Dict
        :return: Nothing
        """
        self.ti_title_pos = _int_tuple(pdx_yaml['title']['position'])
        self.ts_title_align = tuple(pdx_yaml['title']['align'])
        self.i_title_font_size = pdx_yaml['title']['size']
        self.s_title_font = pdx_yaml['title']['font']
        self.ti_title_color = _int_tuple(pdx_yaml['title']['color'])
        self.i_title_width = pdx_yaml['title']['width']

        self.ti_subtitle_pos = _int_tuple(pdx_yaml['subtitle']['position'])
        self.ts_subtitle_align = tuple(pdx_yaml['subtitle']['align'])
        self.i_subtitle_font_size = pdx_yaml['subtitle']['size']
        self.s_subtitle_font = pdx_yaml['subtitle']['font']
        self.ti_subtitle_color = _int_tuple(pdx_yaml['subtitle']['color'])
        self.i_title_width = pdx_yaml['subtitle']['width']


class _ProgBarTheme:
    """
    :ivar ti_bar_position: Tuple[Int]
    :ivar ti_bar_anchor: Tuple[Int]
    """
    def __init__(self):
        self.i_bg_width = 0                     # Width of the background (same as the screen width)
        self.i_bg_height = 0                    # Height of the background (same as the screen height)
        self.ti_bg_color = (0, 0, 0, 0)         # Background color

        # Bar parameters
        self.ti_bar_color = (255, 255, 0, 200)  # Color of the progress bar
        self.i_bar_width = 400
        self.i_bar_height = 20
        self.ti_bar_position = (100, 100)
        self.ti_bar_anchor = (200, 10)          # Grab position of the progress bar
        self.i_bar_border = 2

        # Label parameters
        self.s_msg_font = 'arial'
        self.i_msg_size = 12
        self.ts_msg_align = ['center', 'center']
        self.ti_msg_color = (255, 255, 255, 255)
        self.ti_msg_position = (0, 0)

    def __str__(self):
        """
        :return: Method to represent the instances as strings.
        :rtype: Str
        """
        return class_to_string.class_to_string(self)

    def read_yaml(self, pdx_yaml):
        """
        Method to populate the object from a piece of yaml information.

        :param pdx_yaml:
        :type pdx_yaml: Dict[Str:]

        :return: Nothing, the object will be populated in place.
        """
        # General properties
        self.ti_bg_color = _int_tuple(pdx_yaml['background'])

        # Message attributes
        self.s_msg_font = pdx_yaml['message']['font']
        self.i_msg_size = pdx_yaml['message']['size']
        self.ts_msg_align = tuple(pdx_yaml['message']['align'])
        self.ti_msg_color = _int_tuple(pdx_yaml['message']['color'])
        self.ti_msg_position = _int_tuple(pdx_yaml['message']['position'])

        # Progress bar itself attributes
        self.ti_bar_color = _int_tuple(pdx_yaml['bar']['color'])
        self.ti_bar_position = _int_tuple(pdx_yaml['bar']['position'])
        self.i_bar_width = int(pdx_yaml['bar']['width'])
        self.i_bar_height = int(pdx_yaml['bar']['height'])
        self.i_bar_border = int(pdx_yaml['bar']['border_width'])
        self.ti_bar_anchor = _int_tuple(pdx_yaml['bar']['anchor'])


class _StatusBlockTheme:
    def __init__(self):
        self.ti_position = (0, 300)  # x,y coordinates of the status block
        self.i_vert_spacing = 20     # y spacing when creating multiple field/value fields

        # Field properties
        self.ti_field_color = (255, 0, 0, 255)
        self.s_field_font = 'Arial'
        self.i_field_size = 24
        self.ti_field_position = (0, 260)
        self.ts_field_align = ('right', 'center')

        # Value
        self.ti_value_color = (255, 0, 0, 255)
        self.ti_value_color_alt = (255, 0, 255, 255)
        self.s_value_font = 'Arial'
        self.i_value_size = 24
        self.ti_value_position = (0, 260)
        self.ts_value_align = ('left', 'center')

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        s_out = '<_StatusBlockTheme>\n'
        s_out += f'  .ti_position:     {self.ti_position}\n'
        s_out += f'  .i_vert_spacing:  {self.i_vert_spacing}\n'

        s_out += f'  .ti_tag_color:    {self.ti_field_color}\n'
        s_out += f'  .s_tag_font:      {self.s_field_font}\n'
        s_out += f'  .i_tag_size:      {self.i_field_size}\n'
        s_out += f'  .ti_tag_position: {self.ti_field_position}\n'
        s_out += f'  .ts_tag_align :   {self.ts_field_align}\n'

        s_out += f'  .ti_val_color:    {self.ti_value_color}\n'
        s_out += f'  .s_val_font:      {self.s_value_font}\n'
        s_out += f'  .i_val_size:      {self.i_value_size}\n'
        s_out += f'  .ti_val_position: {self.ti_value_position}\n'
        s_out += f'  .ts_val_align:    {self.ts_value_align}\n'
        return s_out

    def read_yaml(self, pdx_yaml):
        # General properties
        self.i_vert_spacing = pdx_yaml['vert_spacing']
        self.ti_position = tuple(pdx_yaml['position'])

        # Value properties
        self.ti_field_color = _int_tuple(pdx_yaml['field']['color'])
        self.s_field_font = pdx_yaml['field']['font']
        self.i_field_size = pdx_yaml['field']['size']
        self.ti_field_position = pdx_yaml['field']['position']
        self.ts_field_align = pdx_yaml['field']['align']

        # Value properties
        self.ti_value_color = _int_tuple(pdx_yaml['value']['color'])
        self.ti_value_color_alt = _int_tuple(pdx_yaml['value']['color_alt'])
        self.s_value_font = pdx_yaml['value']['font']
        self.i_value_size = pdx_yaml['value']['size']
        self.ti_value_position = pdx_yaml['value']['position']
        self.ts_value_align = pdx_yaml['value']['align']

    def generate_field_and_value_theme(self, pi_index=0):
        """
        Method to generate the theme for each of the FieldAndValueTheme included in the StatusBlock

        :param pi_index: Number of the field , so we can generate proper coordinates for each of them.
        :type pi_index: Int

        :return: A FieldAndValueTheme object.
        :type: _FieldAndValueTheme
        """
        o_fv_theme = _FieldAndValueTheme()

        # Field attributes
        o_fv_theme.i_field_size = self.i_field_size
        o_fv_theme.s_field_font = self.s_field_font
        o_fv_theme.ti_field_position = (
            self.ti_position[0] + self.ti_field_position[0],
            self.ti_position[1] - self.ti_field_position[1] - pi_index * self.i_vert_spacing)
        o_fv_theme.ts_field_align = self.ts_field_align
        o_fv_theme.ti_field_color = self.ti_field_color

        # Value attributes
        o_fv_theme.i_value_size = self.i_value_size
        o_fv_theme.s_value_font = self.s_value_font
        o_fv_theme.ti_value_position = (
            self.ti_position[0] + self.ti_value_position[0],
            self.ti_position[1] - self.ti_value_position[1] - pi_index * self.i_vert_spacing)
        o_fv_theme.ts_value_align = self.ts_value_align
        o_fv_theme.ti_value_color = self.ti_value_color
        o_fv_theme.ti_value_color_alt = self.ti_value_color_alt

        return o_fv_theme


# GUI Elements
#=======================================================================================================================
class _GuiElement:
    def __init__(self):
        self.b_alive = True
        self._lo_pyglet_elems = []

    def kill(self):
        """
        Method to make the element inactive. It'll be
        """
        self.b_alive = False

    def draw(self):
        if self.b_alive:
            for o_elem in self._lo_pyglet_elems:
                o_elem.draw()

    def on_key_press(self, symbol, modifiers):
        pass


class _Image(_GuiElement):
    """
    Method to show an image element.
    """
    def __init__(self, ps_file, pi_x=0, pi_y=0):
        """
        :param ps_file: Path of the image file to be read.
        :type ps_file: Str

        :return: An instance of the _Image class
        :rtype: _Image
        """
        _GuiElement.__init__(self)
        self._i_x = pi_x
        self._i_y = pi_y
        self._lo_pyglet_elems = [pyglet.image.load(ps_file)]

    def draw(self):
        if self.b_alive:
            for o_elem in self._lo_pyglet_elems:
                o_elem.blit(self._i_x, self._i_x)


class _Label(_GuiElement):
    def __init__(self, **px_args):
        _GuiElement.__init__(self)
        self._o_label = pyglet.text.Label(**px_args)
        self._lo_pyglet_elems.append(self._o_label)

        # I'm experiencing a bug with multiline centering that causes centered text to be actually left aligned. I'll
        # apply a manual offset trying to fix it.
        try:
            if px_args['anchor_x'] == 'center':
                i_offset = int((px_args['width'] - self._o_label.content_width) / 2)
                self._o_label.x += i_offset
        except KeyError:
            pass

    def set_text(self, ps_text):
        self._o_label.text = ps_text


class _FieldAndValue(_GuiElement):
    """
    Class to show Field and Value information. Useful, for example, when showing the current configuration which
    contains fields as "User" with an example value as "John" which should be show in screen as "User: John" and
    probably we want to apply different styles to both parts.
    """
    def __init__(self, po_theme, ps_field, ps_value):
        """

        :param po_theme: Theme to be applied to the FieldAndValue object.
        :type po_theme: _FieldAndValueTheme

        :param ps_field: Text of the field label. This value cannot be updated after the created of the instance.
        :type ps_field: Str

        :param ps_value: Text of the value label.
        :type ps_value: Str
        """
        _GuiElement.__init__(self)

        self._o_theme = po_theme

        self._o_field = pyglet.text.Label(text=ps_field,
                                          font_name=self._o_theme.s_field_font,
                                          font_size=self._o_theme.i_field_size,
                                          color=self._o_theme.ti_field_color,
                                          x=self._o_theme.ti_field_position[0],
                                          y=self._o_theme.ti_field_position[1],
                                          anchor_x=self._o_theme.ts_field_align[0],
                                          anchor_y=self._o_theme.ts_field_align[1])
        self._o_value = pyglet.text.Label(text=ps_value,
                                          font_name=self._o_theme.s_value_font,
                                          font_size=self._o_theme.i_value_size,
                                          color=self._o_theme.ti_value_color,
                                          x=self._o_theme.ti_value_position[0],
                                          y=self._o_theme.ti_value_position[1],
                                          anchor_x=self._o_theme.ts_value_align[0],
                                          anchor_y=self._o_theme.ts_value_align[1])

        self._lo_pyglet_elems = [self._o_field, self._o_value]

    def set_value(self, ps_value):
        self._o_value.text = ps_value

    def set_alt(self):
        """
        Method to set the field in default mode (so a special color will be used).
        :return: Nothing.
        """
        self._o_value.color = self._o_theme.ti_value_color_alt

    def set_norm(self):
        self._o_value.color = self._o_theme.ti_value_color


class _Menu(_GuiElement, menu.Menu):
    """
    :ivar: _o_title = _Label
    """
    def __init__(self, po_theme, po_sound_bank=None):
        """
        :param po_theme: Theme information to create new options in the menu.
        :type po_theme: _MenuTheme

        :param po_sound_bank: Bank of sounds that will be played under certain events.
        :type po_sound_bank: _SoundBank
        """
        _GuiElement.__init__(self)
        menu.Menu.__init__(self)
        self._o_theme = po_theme
        self._o_title = None
        self._o_sound_bank = po_sound_bank

    def activate_next(self):
        if self.i_active_elem < (self.i_elems - 1):
            self._o_sound_bank.play('navigate')
        else:
            self._o_sound_bank.play('limit_reached')

        # When there is no menu title, the first gui element will be at position 0, and the first "logical" list element
        # will also be at position 0. When adding a title to the list, the first gui list element will be at zero.
        i_offset = 0
        if self._o_title is not None:
            i_offset += 1

        # We put to normal color the currently active label
        self._lo_pyglet_elems[self.i_active_elem + i_offset].color = self._o_theme.ti_option_color
        # Then we activate the new one
        menu.Menu.activate_next(self)

        # And finally we change the color of the new active label
        self._lo_pyglet_elems[self.i_active_elem + i_offset].color = self._o_theme.ti_option_color_active

    def activate_prev(self):
        if self.i_active_elem > 0:
            self._o_sound_bank.play('navigate')
        else:
            self._o_sound_bank.play('limit_reached')

        # When there is no menu title, the first gui element will be at position 0, and the first "logical" list element
        # will also be at position 0. When adding a title to the list, the first gui list element will be at zero.
        i_offset = 0
        if self._o_title is not None:
            i_offset += 1

        # We put to normal color the currently active label, then we activate the new one, and finally we change the
        # color of the new active label
        self._lo_pyglet_elems[self.i_active_elem + i_offset].color = self._o_theme.ti_option_color
        menu.Menu.activate_prev(self)
        self._lo_pyglet_elems[self.i_active_elem + i_offset].color = self._o_theme.ti_option_color_active

    def add_option(self, ps_text, pc_callback=None, pdx_args={}, pb_default=False):
        menu.Menu.add_option(self, ps_text, pc_callback=pc_callback, pdx_args=pdx_args)

        ti_color = self._o_theme.ti_option_color_active
        if self.i_elems > 1:
            ti_color = self._o_theme.ti_option_color

        s_text = ps_text
        if pb_default:
            s_text = f'> {ps_text} <'

        o_gui_option = pyglet.text.Label(s_text,
                                         x=self._o_theme.ti_option_pos[0],
                                         y=self._o_theme.ti_option_pos[1] - self._o_theme.i_vert_spacing * self.i_elems,
                                         color=ti_color,
                                         font_name=self._o_theme.s_option_font,
                                         font_size=self._o_theme.i_option_size,
                                         anchor_x=self._o_theme.ts_option_align[0],
                                         anchor_y=self._o_theme.ts_option_align[1])
        self._lo_pyglet_elems.append(o_gui_option)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.activate_prev()
        elif symbol == pyglet.window.key.DOWN:
            self.activate_next()
        elif symbol == pyglet.window.key.ENTER:
            self.run_current()

    def run_current(self):
        # TODO: Find a way to run special sound for back option
        self._o_sound_bank.play('select')
        menu.Menu.run_current(self)

    def _set_s_title(self, ps_title):
        menu.Menu._set_s_title(self, ps_title)

        if self._o_title is None:
            # TODO: Add rest of the theme options
            self._o_title = _Label(text=ps_title,
                                   x=self._o_theme.ti_title_pos[0],
                                   y=self._o_theme.ti_title_pos[1],
                                   font_name=self._o_theme.s_title_font,
                                   font_size=self._o_theme.i_title_size,
                                   anchor_x=self._o_theme.ts_title_align[0],
                                   anchor_y=self._o_theme.ts_title_align[1],
                                   color=self._o_theme.ti_title_color,
                                   )
            self._lo_pyglet_elems.append(self._o_title)
        else:
            self._o_title.text = ps_title

        # TODO: Update title label

    def _get_s_title(self):
        return menu.Menu._get_s_title(self)

    s_title = property(fget=_get_s_title, fset=_set_s_title)


class _StatusBlock(_GuiElement):
    """
    Class to store and show in the GUI the options selected by the user for the current ROM.

    :ivar o_config: romconfig.RomConfig
    :ivar o_config_default: romconfig.RomConfig
    :ivar _o_theme: _StatusBlockTheme
    :ivar _o_field_rom: _FieldAndValue
    :ivar _o_field_user: _FieldAndValue
    :ivar _o_field_patch: _FieldAndValue
    :ivar _o_field_refresh: _FieldAndValue
    :ivar _o_field_core: _FieldAndValue
    """
    def __init__(self, po_theme):
        """
        :param po_theme:
        :type po_theme: _StatusBlockTheme
        """
        # Parent classes initialization
        #------------------------------
        _GuiElement.__init__(self)

        self._o_theme = po_theme

        # TODO: Fix comments below, because the actual strategy is almost the opposite.
        # We have wrapper methods to change the actual configuration, so we make the configuration private to avoid
        # confusion. The default configuration shouldn't be modified during the use of the program, so for convenience I
        # leave it as a public attribute.
        self.o_config = romconfig.RomConfig()           # Rom configuration
        self.o_config_default = romconfig.RomConfig()   # Default configuration for the ROM, used to initialize the
                                                        # configuration and to show user changes with a different color.

        # Generation of base FieldAndTag theme from StatusBlockTheme
        #-----------------------------------------------------------
        self._o_field_rom = _FieldAndValue(self._o_theme.generate_field_and_value_theme(pi_index=0), 'CRC32:', '')
        self._o_field_user = _FieldAndValue(self._o_theme.generate_field_and_value_theme(pi_index=1), 'User:', '')
        self._o_field_region = _FieldAndValue(self._o_theme.generate_field_and_value_theme(pi_index=2), 'Region:', '')
        self._o_field_refresh = _FieldAndValue(self._o_theme.generate_field_and_value_theme(pi_index=3), 'Refresh:', '')
        self._o_field_core = _FieldAndValue(self._o_theme.generate_field_and_value_theme(pi_index=4), 'Core:', '')
        self._o_field_patch = _FieldAndValue(self._o_theme.generate_field_and_value_theme(pi_index=5), 'Patch:', '')

        # Adding all elements to pyglet drawing queue
        self._lo_pyglet_elems = [self._o_field_rom,
                                 self._o_field_user,
                                 self._o_field_region,
                                 self._o_field_refresh,
                                 self._o_field_core,
                                 self._o_field_patch,
                                 ]

    def _get_f_refresh(self):
        """
        Method to get the refresh rate to be used by the emulator when launching the ROM.

        :return: The refresh rate in Hz
        :rtype: Float
        """
        return self.o_config.f_refresh(self)

    def _set_f_refresh(self, pf_refresh):
        """
        Method to set the refresh rate to be used by the emulator.

        :param pf_refresh: Frequency in Hz to be used by the emulator.
        :type pf_refresh: Float

        :return: Nothing
        """
        self.o_config.f_refresh = pf_refresh
        self._o_field_refresh.set_value(f'{pf_refresh:.1f} Hz')

        if self.o_config.f_refresh == self.o_config_default.f_refresh:
            self._o_field_refresh.set_alt()
        else:
            self._o_field_refresh.set_norm()

    def _get_o_core(self):
        return self.o_config._o_core(self)

    def _set_o_core(self, po_core):
        """
        Method to set the core to be used by Retroarch.

        :param po_core:
        :type po_core: cores.Core

        :return: Nothing
        """
        self.o_config._o_core = po_core
        self._o_field_core.set_value(po_core.s_name)

        if self.o_config._o_core == self.o_config_default._o_core:
            self._o_field_core.set_alt()
        else:
            self._o_field_core.set_norm()

    def _get_o_patch(self):
        return self.o_config.o_patch

    def _set_o_patch(self, po_patch):
        """
        Method to set the patch_file of the StatusBlock.

        :param po_patch:
        :type po_patch: patches.Patch

        :return: Nothing
        """
        self.o_config.o_patch = po_patch

        # Preparing the text to appear in the status block about the selected patch
        s_patch = 'None'
        if po_patch is not None:
            s_patch = po_patch.s_title

        self._o_field_patch.set_value(s_patch)

        if self.o_config.o_patch == self.o_config_default.o_patch:
            self._o_field_patch.set_alt()
        else:
            self._o_field_patch.set_norm()

    def _get_o_rom(self):
        return self.o_config.o_rom

    def _set_o_rom(self, po_rom):
        self.o_config.o_rom = po_rom

        # Preparing the text to appear in the status block about the selected ROM
        s_ccrc32 = '????????'
        if po_rom.s_ccrc32:
            s_ccrc32 = po_rom.s_ccrc32

        s_text = f'{s_ccrc32}'  # {po_rom.s_name}'
        self._o_field_rom.set_value(s_text)

        self._o_field_rom.set_alt()

    def _get_s_user(self):
        return self.o_config.s_user

    def _set_s_user(self, ps_value):
        """
        Method to set the user who's about to run the ROM.

        :param ps_value: Name of the user.
        :type ps_value: Str

        :return: Nothing
        """
        self.o_config.s_user = ps_value
        self._o_field_user.set_value(ps_value)

    def _get_s_region(self):
        return self.o_config.s_region

    def _set_s_region(self, ps_value):
        self.o_config.s_region = ps_value
        self._o_field_region.set_value(ps_value)

        if self.o_config.s_region == self.o_config_default.s_region:
            self._o_field_region.set_alt()
        else:
            self._o_field_region.set_norm()

    def reset_config(self):
        """
        Method to reset the configuration to the default one.

        :return: Nothing, the object will be modified in place.
        """
        self.o_patch = self.o_config_default.o_patch
        self.s_region = self.o_config_default.s_region
        self.s_user = self.o_config_default.s_user
        self.f_refresh = self.o_config_default.f_refresh
        self.o_core = self.o_config_default.o_core
        self.o_rom = self.o_config_default.o_rom

    f_refresh = property(fset=_set_f_refresh, fget=_get_f_refresh)
    o_core = property(fset=_set_o_core, fget=_get_o_core)
    o_patch = property(fset=_set_o_patch, fget=_get_o_patch)
    o_rom = property(fset=_set_o_rom, fget=_get_o_rom)
    s_region = property(fset=_set_s_region, fget=_get_s_region)
    s_user = property(fset=_set_s_user, fget=_get_s_user)


class _ProgressBar(_GuiElement):
    """
    Class to define a progress bar with messages.
    """
    def __init__(self, po_theme):
        """
        :param po_theme:
        :type po_theme: _ProgBarTheme
        """
        # Parent classes initialization
        #------------------------------
        _GuiElement.__init__(self)
        self._o_theme = po_theme
        self._f_progress = 0.0

        # Progres bar itself
        #-------------------
        # Due to a limitation in pyglet, it's not possible to create a bordered rectangle. So, to create a frame around
        # the actual progress bar with some separation, I have to create two solid rectangles, one on top of another.

        # Progress bar background
        self._o_bar_frame_bg = pyglet.shapes.Rectangle(x=self._o_theme.ti_bar_position[0],
                                                       y=self._o_theme.ti_bar_position[1],
                                                       width=self._o_theme.i_bar_width,
                                                       height=self._o_theme.i_bar_height,
                                                       color=self._o_theme.ti_bar_color)
        self._o_bar_frame_bg.anchor_position = self._o_theme.ti_bar_anchor
        self._lo_pyglet_elems.append(self._o_bar_frame_bg)

        # Progress bar foreground
        self._o_bar_frame_fg = pyglet.shapes.Rectangle(x=self._o_theme.ti_bar_position[0] + self._o_theme.i_bar_border,
                                                       y=self._o_theme.ti_bar_position[1]+self._o_theme.i_bar_border,
                                                       width=self._o_theme.i_bar_width-2*self._o_theme.i_bar_border,
                                                       height=self._o_theme.i_bar_height-2*self._o_theme.i_bar_border,
                                                       color=self._o_theme.ti_bg_color)
        self._o_bar_frame_fg.anchor_position = self._o_theme.ti_bar_anchor
        self._lo_pyglet_elems.append(self._o_bar_frame_fg)

        # Actual progress bar
        i_bar_x = self._o_theme.ti_bar_position[0] + 2 * self._o_theme.i_bar_border - self._o_theme.ti_bar_anchor[0]
        i_bar_y = self._o_theme.ti_bar_position[1] + 2 * self._o_theme.i_bar_border - self._o_theme.ti_bar_anchor[1]
        self._o_bar = pyglet.shapes.Rectangle(x=i_bar_x,
                                              y=i_bar_y,
                                              width=128,
                                              height=self._o_theme.i_bar_height-4*self._o_theme.i_bar_border,
                                              color=self._o_theme.ti_bar_color)
        self._lo_pyglet_elems.append(self._o_bar)

        # Message
        #--------
        self._o_message = _Label(text='16% decrunching trocola gasket',
                                 font_name=self._o_theme.s_msg_font,
                                 font_size=12,
                                 color=self._o_theme.ti_msg_color,
                                 x=960,
                                 y=340,
                                 anchor_x='center',
                                 anchor_y='center')
        self._lo_pyglet_elems.append(self._o_message)

    def __str__(self):
        """
        :return: A text representation of the object.
        :rtype: Str
        """
        s_out = class_to_string.class_to_string(self)
        return s_out

    def _set_s_message(self, ps_value):
        """
        Method to set the message value.

        :param ps_value:
        :type ps_value: Str
        :return: Nothing.
        """
        self._o_message.set_text(ps_value)

    def _set_f_progress(self, pf_value):
        """
        Method to set the progress value.

        :param pf_value:
        :type pf_value: Float

        :return: Nothing.
        """
        self._f_progress = pf_value
        self._o_bar.width = pf_value * (self._o_theme.i_bar_width - 4 * self._o_theme.i_bar_border)

    f_progress = property(fset=_set_f_progress, fget=None)
    s_message = property(fset=_set_s_message, fget=None)


class _SoundBank:
    """
    Class to store and play sounds.
    :ivar _do_sounds: Union[None, pyglet.media.Source
    """
    def __init__(self, ps_dir):
        """
        Method to initialise the _SoundBank, loading all the sounds in the directory indicated.

        :param ps_dir: Directory to read the sounds from
        :type ps_dir: Str
        """
        # Initialization
        self._do_sounds = {'navigate': None,
                           'select': None,
                           'reset': None,
                           'limit_reached': None}

        # Reading the sounds
        for s_sound_name in ('navigate', 'select', 'reset', 'limit_reached'):
            for s_ext in ('wav', 'mp3'):
                s_sound_path = os.path.join(ps_dir, f'{s_sound_name}.{s_ext}')
                if os.path.isfile(s_sound_path):
                    o_sound = pyglet.media.load(s_sound_path, streaming=False)
                    self._do_sounds[s_sound_name] = o_sound
                    break

    def play(self, ps_sound_name):
        """
        Method to play a sound.

        :param ps_sound_name: Internal ps_name of the sound to be played.
        :type ps_sound_name: Str

        :return: Nothing
        """
        if self._do_sounds[ps_sound_name] is not None:
            self._do_sounds[ps_sound_name].play()


# Helper functions
#=======================================================================================================================
def _int_tuple(ptx_input):
    """

    """
    li_out = [int(x_value) for x_value in ptx_input]
    return tuple(li_out)


def _add_tuples(ptx_a, ptx_b):
    """
    Function to add tuples of integers or floats
    """
    lf_values = []
    for x_a, x_b in zip(ptx_a, ptx_b):
        lf_values.append(x_a + x_b)

    return tuple(lf_values)
