"""
Library to work or interface with common command line tools of the system.
"""

from shutil import which


# Main functions
#=======================================================================================================================
def is_tool_installed(ps_name):
    """
    Check whether `ps_name` is on PATH and marked as executable.

    :param ps_name:
    :type ps_name: Str

    :return:
    :rtype: Bool
    """

    return which(ps_name) is not None

# TODO: Move uncompress to files library


