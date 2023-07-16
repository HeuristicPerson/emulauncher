"""
This library is just a test I'm making to print classes as strings in a user friendly way.
"""

import re


# Classes
#=======================================================================================================================
class AttributeName:
    def __init__(self, ps_name):
        self.s_prefix = ''
        self.s_type = ''
        self.s_name = ''
        self._decompose(ps_name)

    def _decompose(self, ps_string):
        """
        Method to extract the three different parts of each attribute name: prefix, type, and name.

        :param ps_string:
        :type ps_string: Str

        :return: Nothing, the object will be modified in place.
        """
        s_type_name_pattern = r'(_+)?([a-zA-Z\d]+(_)?)(.*)'
        o_result = re.search(s_type_name_pattern, ps_string, flags=re.IGNORECASE)

        if o_result.group(1) is not None:
            self.s_prefix = o_result.group(1)

        if o_result.group(4) and o_result.group(2):
            self.s_type = o_result.group(2)
            self.s_name = o_result.group(4)
        else:
            self.s_name = o_result.group(2)

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        s_out = ''.join((self.s_prefix, self.s_type, self.s_name))
        return s_out


def class_to_string(po_instance, pb_privates=False):
    """

    My final goal is that the output will look something like:

      <MyClass>
          .i_foo_size:  23
         .ls_foo_names: ['john', 'charles']
        .dsi_foo_years: {'aaa': 2023, 'bbb': 1997}
        .bar:           'andrew'
        .foo:           157

    Notice how:

        1. The type indication in the attribute name is indented two positions at least.
        2. The variable names are vertically align (foo_size, foo_names, foo_years).
        3. Attributes without type indication (foo, bar) appear after the attributes with type.
        4. Attributes appear alphabetically sorted.

    :param po_instance:

    :param pb_privates: Whether private attributes should be included in the representation or not. False by default.
    :type pb_privates: Bool

    :return: The string representation of the instance.
    :rtype: Str
    """
    # Header
    s_out = '<%s>\n' % type(po_instance).__name__
    lo_attributes_and_values = [(AttributeName(s_key), x_value) for s_key, x_value in vars(po_instance).items()]

    li_prefix_lengths = [len(o_entry[0].s_prefix) for o_entry in lo_attributes_and_values]
    li_type_lengths = [len(o_entry[0].s_type) for o_entry in lo_attributes_and_values]
    li_name_lengths = [len(o_entry[0].s_name) for o_entry in lo_attributes_and_values]

    i_prefix_max_length = max(li_prefix_lengths)
    i_type_max_length = max(li_type_lengths)
    i_name_max_length = max(li_name_lengths)

    ls_attributes = []
    for o_attribute, x_value in sorted(lo_attributes_and_values, key=lambda tx_entry: (tx_entry[0].s_prefix,
                                                                                       tx_entry[0].s_name,
                                                                                       tx_entry[0].s_type)):
        s_attr_name = '.%s:' % o_attribute

        # First, we left pad the attribute name so the variable names are vertically aligned
        i_left_pad = (i_prefix_max_length + i_type_max_length) - (len(o_attribute.s_prefix) + len(o_attribute.s_type))
        s_attr_name = '%s%s' % (' ' * i_left_pad, s_attr_name)

        # Then, we pad the attribute name to the right so the values will be vertically aligned
        i_max_length = 2 + i_prefix_max_length + i_type_max_length + i_name_max_length
        s_attr_name = s_attr_name.ljust(i_max_length, ' ')

        s_attr_value = str(x_value)

        s_attribute_repr = f'  {s_attr_name} {s_attr_value}'
        ls_attributes.append(s_attribute_repr)

    s_out += '\n'.join(ls_attributes)

    return s_out


def _my_compare(ps_item_a, ps_item_b):
    """
    The sorting function has to return -1, 0, +1 depending on which of the items should go first.

    I typically call my attributes .type_name, or ._type_name for private attributes. So, the first thing is to get the
    type of variable, and the name separately because I want to alphabetically sort by the variable name, not the type.

    :param ps_item_a:
    :param ps_item_b:
    :return:
    :rtype: Int
    """
