import unittest

import libs.menu as menu


# Test classes
#=======================================================================================================================
class MyTestCase(unittest.TestCase):
    def test_creation_of_layer_with_no_callbacks(self):
        o_layer = menu.Menu()
        o_layer.add_option('foo')
        o_layer.add_option('bar')
        o_layer.add_option('meh')

        s_actual = o_layer.nice_format()
        s_expected = '[*] foo > None({})\n' \
                     '[ ] bar > None({})\n' \
                     '[ ] meh > None({})'

        s_msg = 'Nice format of a simple layer with no callbacks not what was expected'
        self.assertEqual(s_actual, s_expected, s_msg)

    def test_creation_of_layer_with_callbacks(self):
        def null_callback():
            pass
            
        o_layer = menu.Menu()
        o_layer.add_option(ps_text='foo', pc_callback=null_callback, pdx_args={'a': 1, 'b': 2})
        o_layer.add_option(ps_text='bar', pc_callback=null_callback)

        s_actual = o_layer.nice_format()
        s_expected = '[*] foo > null_callback({\'a\': 1, \'b\': 2})\n' \
                     '[ ] bar > null_callback({})'

        self.assertEqual(s_expected, s_actual)

    def test_callback_with_params(self):
        def say_hello(ps_name):
            return f'Hello, {ps_name}!'

        o_layer = menu.Menu()
        o_layer.add_option(ps_text='rob', pc_callback=say_hello, pdx_args={'ps_name': 'Rob'})
        o_layer.add_option(ps_text='ann', pc_callback=say_hello, pdx_args={'ps_name': 'Ann'})

        lu_results = []
        lu_results.append(o_layer.run_current())
        o_layer.activate_next()
        lu_results.append(o_layer.run_current())

        lu_expected = [u'Hello, Rob!', u'Hello, Ann!']
        self.assertEqual(lu_expected, lu_results)

    def test_activate_next_no_elems(self):
        o_layer = menu.Menu()

        li_active_elems = [o_layer.i_active_elem]
        o_layer.activate_next()
        li_active_elems.append(o_layer.i_active_elem)

        lx_actual = li_active_elems
        lx_expected = [None, None]

        self.assertEqual(lx_expected, lx_actual)

    def test_activate_next_beyond_limit(self):
        """
        Test for the activation of next elements and over-floating when reaching the limit.
        :return:
        """
        o_layer = menu.Menu()
        o_layer.add_option(ps_text='foo')
        o_layer.add_option(ps_text='bar')

        li_active_elems = [o_layer.i_active_elem]
        o_layer.activate_next()
        li_active_elems.append(o_layer.i_active_elem)
        o_layer.activate_next()
        li_active_elems.append(o_layer.i_active_elem)

        li_expected = [0, 1, 1]

        self.assertEqual(li_expected, li_active_elems)

    def test_activate_prev_no_elems(self):
        o_layer = menu.Menu()

        li_active_elems = [o_layer.i_active_elem]
        o_layer.activate_prev()
        li_active_elems.append(o_layer.i_active_elem)

        li_expected = [None, None]

        self.assertEqual(li_expected, li_active_elems)

    def test_activate_prev_below_zero(self):
        """
        Method to test that we can not go below 0 when trying to activate the previous element.
        :return:
        """
        o_layer = menu.Menu()
        o_layer.add_option(ps_text='foo')
        o_layer.add_option(ps_text='bar')

        li_active_elems = [o_layer.i_active_elem]
        o_layer.activate_next()
        li_active_elems.append(o_layer.i_active_elem)
        o_layer.activate_prev()
        li_active_elems.append(o_layer.i_active_elem)
        o_layer.activate_prev()
        li_active_elems.append(o_layer.i_active_elem)

        li_expected = [0, 1, 0, 0]

        self.assertEqual(li_expected, li_active_elems)

    def test_set_and_get_title(self):
        o_menu = menu.Menu()
        o_menu.s_title = 'this is the title'
        s_expected = 'this is the title'
        s_actual = o_menu.s_title

        self.assertEqual(s_expected, s_actual)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
