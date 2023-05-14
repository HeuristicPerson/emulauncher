"""
Library with some string related functions of general use.
"""

import re


def section_generate(ps_header, pls_elems):
    """
    Function to generate a text similar to:

        Header intro text: Value 1
                           Value 2
                           Value 3
                           ...

    If the pls_elems list is empty, the output will be:

        Header intro text:

    This function will be useful when creating visually organised text output for objects "represented as strings".

    :param ps_header: Text that will work as the header.
    :type ps_header: Str

    :param pls_elems:
    :type pls_elems: List[Str]

    :return: A piece of text.
    :rtype: Str
    """
    s_out = ''
    if not pls_elems:
        s_out += f'{ps_header}\n'
    else:
        for i_elem, s_elem in enumerate(pls_elems):
            if i_elem == 0:
                s_out += f'{ps_header} {s_elem}\n'
            else:
                s_out += f'%s {s_elem}\n' % (' '*len(ps_header))

    return s_out


def is_crc32(ps_text):
    """
    Function to check a piece of text is a crc32 representation or not.

    :param ps_text:
    :type ps_text: Str

    :return:
    :rtype: Bool
    """
    s_pattern = r'^[0-9a-f]{8}$'
    b_is_crc32 = False
    if re.match(s_pattern, ps_text) is not None:
        b_is_crc32 = True

    return b_is_crc32
