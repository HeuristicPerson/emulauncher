import os
import unittest

import libs.cons as cons

# The library to be tested
import libs.gui as gui


# Unit tests
#=======================================================================================================================
class ClassTheme(unittest.TestCase):
    @staticmethod
    def _read_valid_theme():
        """
        Method to read and return the default theme.
        :return:
        :rtype: gui.Theme
        """
        s_theme_default = os.path.join(cons.s_TEST_DATA_DIR, 'themes', 'theme_a.yaml')
        o_theme = gui.Theme(ps_yaml=s_theme_default)
        return o_theme

    def test_read_yaml_section_progress_bar(self):
        """
        A generic unit test for the progress bar section when passing correct information.
        :return:
        """
        # Loading a progress bar theme
        s_theme = os.path.join(cons.s_TEST_DATA_DIR, 'themes', 'theme_progress_bar_valid.yaml')
        o_theme = gui.Theme(ps_yaml=s_theme)
        o_theme_prog_bar = o_theme.o_prog_bar_theme

        # We need to manually apply the width/height in this test case because we don't have a full theme definition
        # in the .yaml file read. In the regular flow of the program, the progress bar background size is obtained from
        # the main section within the file.
        o_theme_prog_bar.i_bg_width = 800
        o_theme_prog_bar.i_bg_height = 600

        # --- test code ---
        print()
        print(o_theme_prog_bar)
        # ------ end ------

        dx_actual = vars(o_theme.o_prog_bar_theme)
        dx_expect = {
            # Background attributes
            'i_bg_width': 800,
            'i_bg_height': 600,
            'ti_bg_color': (0, 1, 2, 3),
            # Message attributes
            's_msg_font': 'Arial',
            'i_msg_size': 10,
            'ts_msg_align': ('right', 'bottom'),
            'ti_msg_color': (255, 255, 255, 128),
            'ti_msg_position': (960, 950),
            # Progress bar itself
            'i_bar_border': 2,
            'ti_bar_color': (40, 41, 42, 43),
            'i_bar_height': 16,
            'i_bar_width': 800,
            'ti_bar_position': (940, 900),
            'ts_bar_align': ('left', 'top')
            }
        s_msg = 'Read values from progress bar section don\'t match expected values.'
        self.assertEqual(dx_expect, dx_actual, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
