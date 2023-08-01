"""
Library to handle retroarch cores information.
"""

import os


# Classes
#=======================================================================================================================
class Core:
    """
    :ivar s_path: Str
    """
    def __init__(self, ps_path):
        """
        :param ps_path: Path of the libretro core to be used to create our object.
        :type ps_path: Str

        :return: Nothing.
        """

        if not ps_path.endswith('_libretro.so'):
            raise ValueError
        else:
            self.s_path = ps_path  # Full path of the core

    def __eq__(self, po_other):
        """
        Equality comparison method.

        :param po_other: Other instance of the class.
        :type po_other: Core

        :return: Whether the two instances are the same or not.
        :rtype: Bool
        """
        return self.s_path == po_other.s_path

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        s_out = '<Core>\n'
        s_out += f'  .s_path: {self.s_path}\n'
        s_out += f'  .s_name: {self.s_name}\n'
        return s_out

    def _get_s_name(self):
        """
        Method to get the name of the core without all the extra text added to the core files. e.g. for core file
        "genesis_plus_gx_libretro.so", the name of the core name should be "genesis_plus_gx".

        :return:
        :rtype: Str
        """
        s_file = os.path.basename(self.s_path)
        return s_file.rpartition('_libretro.so')[0]

    s_name = property(fget=_get_s_name, fset=None)


# Functions
#=======================================================================================================================
def _get_cores_all(ps_dir):
    """
    Function to build a dictionary with all the cores available in a directory.

    :param ps_dir: Path of the directory with RetroArch cores.
    :type ps_dir: Str

    :return: A dictionary with all the cores where key = core name, and value = core object.
    :rtype: Dict[Str:Core]
    """
    do_cores_available = {}
    for s_elem in os.listdir(ps_dir):
        s_elem_name, _, s_elem_ext = s_elem.rpartition('.')
        s_full_path = os.path.join(ps_dir, s_elem)
        if os.path.isfile(s_full_path) and (s_elem_ext == 'so'):
            o_core = Core(s_full_path)
            do_cores_available[o_core.s_name] = o_core

    return do_cores_available


def get_cores(ps_dir, pls_cores_wanted):
    """
    Function to return a list of core objects for the cores found in a folder and wanted by the user.

    :param ps_dir: Directory where Retroarch core files are located.
    :type ps_dir: Str

    :param pls_cores_wanted: List of cores wanted, just the file names, without the extension.
    :type pls_cores_wanted: List[Str]

    :return:
    :rtype: Tuple[Core]
    """
    # First we get all the cores
    do_cores_available = _get_cores_all(ps_dir)

    # ...then we get the ones we want in the order required
    lo_cores_wanted = []
    for s_core_wanted in pls_cores_wanted:
        try:
            o_core = do_cores_available[s_core_wanted]
            lo_cores_wanted.append(o_core)
        except KeyError:
            pass

    return tuple(lo_cores_wanted)
