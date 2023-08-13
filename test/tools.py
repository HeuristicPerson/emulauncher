import inspect
import os

import libs.cons as cons


def get_test_input_dir(po_test):
    """
    Function to build the path to store output data for an unittest.

    :param po_test:
    :type po_test: unittest.UnitTest

    :return: Path of the directory to write output data.
    :rtype: Str
    """
    # We want to print information about the caller function of this function, which should be an unittest, so it's in
    # the second position of the stack. The content of each frameinfo object, when accessed by position is something
    # like:
    #
    #    [0] <frame at 0x7fcc52fdcba0, file '/mnt/jupiter.lan/pw_david/projects/coding/python/emulauncher/dev/test/
    #        test_libs_files.py', line 107, code test_patch_xdelta3>
    #    [1] /mnt/jupiter.lan/pw_david/projects/coding/python/emulauncher/dev/test/test_libs_files.py
    #    [2] 107
    #    [3] test_patch_xdelta3
    #    [4] ['        tools.get_test_folder(self)\n']
    #    [5] 0

    lo_stack = inspect.stack()
    o_frameinfo = lo_stack[1]

    s_file = os.path.basename(f'{o_frameinfo[1]}').rpartition('.')[0]
    s_class = type(po_test).__name__
    s_test = o_frameinfo[3]

    # I think a per-class directory is enough in general. If I need more granularity, I can manually create extra
    # directories inside.
    s_dir = os.path.join(cons.s_TEST_DATA_DIR, s_file, s_class)
    return s_dir


def get_test_output_dir(po_test):
    """
    Function to build the path to store output data for an unittest.

    :param po_test:
    :type po_test: unittest.UnitTest

    :return: Path of the directory to write output data.
    :rtype: Str
    """
    # We want to print information about the caller function of this function, which should be an unittest, so it's in
    # the second position of the stack. The content of each frameinfo object, when accessed by position is something
    # like:
    #
    #    [0] <frame at 0x7fcc52fdcba0, file '/mnt/jupiter.lan/pw_david/projects/coding/python/emulauncher/dev/test/
    #        test_libs_files.py', line 107, code test_patch_xdelta3>
    #    [1] /mnt/jupiter.lan/pw_david/projects/coding/python/emulauncher/dev/test/test_libs_files.py
    #    [2] 107
    #    [3] test_patch_xdelta3
    #    [4] ['        tools.get_test_folder(self)\n']
    #    [5] 0

    lo_stack = inspect.stack()
    o_frameinfo = lo_stack[1]

    s_file = os.path.basename(f'{o_frameinfo[1]}').rpartition('.')[0]
    s_class = type(po_test).__name__
    s_test = o_frameinfo[3]

    s_dir = os.path.join(cons.s_TEST_DATA_OUT, f'{s_file}_{s_class}_{s_test}')
    return s_dir
