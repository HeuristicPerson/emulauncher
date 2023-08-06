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
        Method to extract the three different parts of each attribute ps_name: prefix, type, and ps_name.

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

        1. The type indication in the attribute ps_name is indented two positions at least.
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
    ls_out = ['<%s>' % type(po_instance).__name__]
    lo_attributes_and_values = [(AttributeName(s_key), getattr(po_instance, s_key)) for s_key in dir(po_instance)]

    # Pre-filtering of __X__ attributes and methods
    #----------------------------------------------
    lo_attributes_and_values = [(o_attr, x_value) for o_attr, x_value in lo_attributes_and_values
                                if (o_attr.s_prefix != '__' and not callable(x_value))]

    li_prefix_lengths = []
    li_type_lengths = []
    li_name_lengths = []
    for o_attribute, _ in lo_attributes_and_values:
        b_keep = (not o_attribute.s_prefix.startswith('_')) or pb_privates

        if b_keep:
            li_prefix_lengths.append(len(o_attribute.s_prefix))
            li_type_lengths.append(len(o_attribute.s_type))
            li_name_lengths.append(len(o_attribute.s_name))

    try:
        i_prefix_max_length = max(li_prefix_lengths)
    except ValueError:
        i_prefix_max_length = 0

    try:
        i_type_max_length = max(li_type_lengths)
    except ValueError:
        i_type_max_length = 0

    try:
        i_name_max_length = max(li_name_lengths)
    except ValueError:
        i_name_max_length = 0

    ls_attributes = []
    for o_attribute, x_value in sorted(lo_attributes_and_values, key=lambda tx_entry: (tx_entry[0].s_prefix,
                                                                                       tx_entry[0].s_name,
                                                                                       tx_entry[0].s_type)):
        b_keep = (not o_attribute.s_prefix.startswith('_')) or pb_privates
        if b_keep:
            s_attr_name = '.%s:' % o_attribute

            # First, we left pad the attribute ps_name so the variable names are vertically aligned
            i_left_pad = i_prefix_max_length + i_type_max_length - len(o_attribute.s_prefix) - len(o_attribute.s_type)
            s_attr_name = '%s%s' % (' ' * i_left_pad, s_attr_name)

            # Then, we pad the attribute ps_name to the right so the values will be vertically aligned
            i_max_length = 2 + i_prefix_max_length + i_type_max_length + i_name_max_length
            s_attr_name = s_attr_name.ljust(i_max_length, ' ')

            # Finally, we create the text representation of the value, splitting into multiple lines when required.
            s_attr_value = str(x_value)
            s_attr_value_padding = ' ' * len(s_attr_name)

            # an empty string doesn't contain lines, so we have to process it separately
            if not s_attr_value:
                s_new_line = f'  {s_attr_name} {s_attr_value}'
                ls_attributes.append(s_new_line)
            else:
                for i_line, s_line in enumerate(s_attr_value.splitlines(False)):
                    if i_line == 0:
                        s_new_line = f'  {s_attr_name} {s_line}'
                    else:
                        s_new_line = f'  {s_attr_value_padding} {s_line}'
                    ls_attributes.append(s_new_line)

    ls_out += ls_attributes

    return '\n'.join(ls_out)

