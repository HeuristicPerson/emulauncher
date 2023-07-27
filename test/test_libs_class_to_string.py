import unittest

import libs.class_to_string as class_to_string


class FunctionDecompose(unittest.TestCase):
    def test_public_attribute_with_type(self):
        s_name = 'ti_position'
        o_attr_name = class_to_string.AttributeName(s_name)
        ls_expect = ['', 'ti_', 'position']
        ls_actual = [o_attr_name.s_prefix, o_attr_name.s_type, o_attr_name.s_name]
        s_msg = 'Read attributes don\'t match expectation.'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_private_attribute_with_type(self):
        s_name = '_ti_position'
        o_attr_name = class_to_string.AttributeName(s_name)
        ls_expect = ['_', 'ti_', 'position']
        ls_actual = [o_attr_name.s_prefix, o_attr_name.s_type, o_attr_name.s_name]
        s_msg = 'Read attributes don\'t match expectation.'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_double_private_attribute_with_type(self):
        s_name = '__ti_position'
        o_attr_name = class_to_string.AttributeName(s_name)
        ls_expect = ['__', 'ti_', 'position']
        ls_actual = [o_attr_name.s_prefix, o_attr_name.s_type, o_attr_name.s_name]
        s_msg = 'Read attributes don\'t match expectation.'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_public_attribute_no_type(self):
        s_name = 'position'
        o_attr_name = class_to_string.AttributeName(s_name)
        ls_expect = ['', '', 'position']
        ls_actual = [o_attr_name.s_prefix, o_attr_name.s_type, o_attr_name.s_name]
        s_msg = 'Read attributes don\'t match expectation.'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_private_attribute_no_type(self):
        s_name = '_position'
        o_attr_name = class_to_string.AttributeName(s_name)
        ls_expect = ['_', '', 'position']
        ls_actual = [o_attr_name.s_prefix, o_attr_name.s_type, o_attr_name.s_name]
        s_msg = 'Read attributes don\'t match expectation.'
        self.assertEqual(ls_expect, ls_actual, s_msg)

    def test_double_private_attribute_no_type(self):
        s_name = '__position'
        o_attr_name = class_to_string.AttributeName(s_name)
        ls_expect = ['__', '', 'position']
        ls_actual = [o_attr_name.s_prefix, o_attr_name.s_type, o_attr_name.s_name]
        s_msg = 'Read attributes don\'t match expectation.'
        self.assertEqual(ls_expect, ls_actual, s_msg)


class FunctionClassToString(unittest.TestCase):
    def test_class_only_public_attributes_no_type(self):
        class Foo:
            def __init__(self):
                self.year = 2020
                self.month = 10
                self.day = 27

        o_instance = Foo()
        s_expect = '<Foo>\n' \
                   '  .day:   27\n' \
                   '  .month: 10\n' \
                   '  .year:  2020'
        s_actual = class_to_string.class_to_string(o_instance)

        s_msg = 'String representation of class with "untyped" attributes is wrong.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_class_only_private_attributes_no_type_privates_shown(self):
        class Foo:
            def __init__(self):
                self._year = 2020
                self._month = 10
                self._day = 27

        o_instance = Foo()

        s_expect = '<Foo>\n' \
                   '  ._day:   27\n' \
                   '  ._month: 10\n' \
                   '  ._year:  2020'
        s_actual = class_to_string.class_to_string(o_instance, pb_privates=True)
        s_msg = 'String representation of class with "untyped" attributes is wrong.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_class_only_private_attributes_no_type_privates_hidden(self):
        class Foo:
            def __init__(self):
                self._year = 2020
                self._month = 10
                self._day = 27

        o_instance = Foo()

        s_expect = '<Foo>' \

        s_actual = class_to_string.class_to_string(o_instance, pb_privates=False)
        s_msg = 'String representation of class with "untyped" attributes is wrong.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_class_only_public_attributes_with_type_1(self):
        class Foo:
            def __init__(self):
                self.i_year = 2020
                self.i_month = 10
                self.i_day = 27

        o_instance = Foo()

        s_expect = '<Foo>\n' \
                   '  .i_day:   27\n' \
                   '  .i_month: 10\n' \
                   '  .i_year:  2020'
        s_actual = class_to_string.class_to_string(o_instance)
        s_msg = 'String representation of class with "untyped" attributes is wrong.'
        self.assertEqual(s_expect, s_actual, s_msg)

    def test_class_only_public_attributes_with_type_2(self):
        """
        Similar to test_class_only_public_attributes_with_type_1 but one of the parameters has a longer type.
        :return:
        """
        class Foo:
            def __init__(self):
                self.i_year = 2020
                self.ti_months = (10, 11)
                self.i_day = 27

        o_instance = Foo()

        s_expect = '<Foo>\n' \
                   '   .i_day:    27\n' \
                   '  .ti_months: (10, 11)\n' \
                   '   .i_year:   2020'
        s_actual = class_to_string.class_to_string(o_instance)

        s_msg = 'String representation of class with "untyped" attributes is wrong.'
        self.assertEqual(s_expect, s_actual, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
