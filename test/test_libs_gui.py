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
        Method to read and return test theme_a.
        :return:
        :rtype: gui.Theme
        """
        s_theme_default = os.path.join(cons.s_TEST_DATA_DIR, 'themes', 'theme_a.yaml')
        o_theme = gui.Theme(ps_yaml=s_theme_default)
        return o_theme

    @staticmethod
    def _read_default_theme():
        """
        Method to read and return the default theme.
        :return:
        :rtype: gui.Theme
        """
        s_theme_default = os.path.join(cons.s_SCRIPT_ROOT, 'themes', 'default', 'theme.yaml')
        o_theme = gui.Theme(ps_yaml=s_theme_default)
        return o_theme

    # Progress bar functionalities
    #-----------------------------
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

        dx_actual = vars(o_theme.o_prog_bar_theme)
        dx_expect = {
            # Background attributes
            'i_bg_width': 800,
            'i_bg_height': 600,
            'ti_bg_color': (0, 1, 2, 3),
            # Progress bar itself
            'i_bar_border': 2,
            'ti_bar_color': (40, 41, 42, 43),
            'i_bar_height': 16,
            'i_bar_width': 800,
            'ti_bar_position': (940, 900),
            'ti_bar_anchor': (400, 8),
            # Message attributes
            's_msg_font': 'Arial',
            'i_msg_size': 10,
            'ts_msg_align': ('right', 'bottom'),
            'ti_msg_color': (255, 255, 255, 128),
            'ti_msg_position': (960, 950),
            }
        s_msg = 'Read values from progress bar section don\'t match expected values.'
        self.assertEqual(dx_expect, dx_actual, s_msg)

    #def test_method_build_progress_bar(self):
    #    """
    #    :return: Nothing.
    #    """
    #    o_def_theme = self._read_valid_theme()
    #
    #    # --- test code ---
    #    print()
    #    print(o_def_theme)
    #    # ------ end ------
    #
    #    self.assertEqual(True, False)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
