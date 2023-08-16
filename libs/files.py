"""
Description: Library with file tools.
"""

import codecs
import datetime
import os
import re
import shutil
import subprocess
import zipfile
import zlib

from . import cons


# Classes
# =======================================================================================================================
class BackReader:
    """
    My own class to read a file backwards line by line.
    """
    i_block = 2

    def __init__(self, pu_file):
        self.u_file = pu_file
        self._o_file = None
        self._u_buffer = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        READ THIS: http://stackoverflow.com/questions/22417323/how-do-enter-and-exit-work-in-python-decorator-classes
        :param exc_type:
        :param exc_value:
        :param traceback:
        :return:
        """
        # TODO: Raise exceptions correctly.
        self.close()

    def __iter__(self):
        self.open()
        # Apparently, the last byte of the file (End Of File, EOF), is read as a newline by python when it's actually a
        # different "character". To avoid it, I have to move one byte back (-1) from the end of the file (2) before
        # actually start to read the data.
        self._o_file.seek(-1, 2)
        self._u_buffer = u''
        return self

    def next(self):
        while (self._u_buffer.count('\n') < 2) and (self._o_file.tell() > 0):
            # We aim to fill the buffer, so we try to have two new lines symbols in it:
            self._u_buffer = self._get_chunk_from_end() + self._u_buffer

        if self._u_buffer == '':
            raise StopIteration

        # Remember we WANTED to have at least two '\n' in the buffer, but that's not possible when finishing to
        # read the file backwards and reaching the beginning.

        # The three options to deal with are:
        #
        #   1. Last character is '\n':
        #          |=====[n]===[n]
        #
        #           1a. There are another '\n' in the middle (that's what we are aiming for when filling up the
        #               buffer.
        #                   |====[n]===[n]
        #
        #           1b. The last '\n' is the only one, so we reached the beginning of file:
        #                   BOF|====[n]
        #
        #   2. Last character is not an '\n' (This situation could only happen when starting to read the file
        #      from the end):
        #          |=====[n]======

        # With a little of pre-process (removing and keeping the last '\n' when present)...
        u_end = ''
        if self._u_buffer.endswith(u'\n'):
            u_end = '\n'
            self._u_buffer = self._u_buffer[:-1]

        # We can process cases 1a inside case 2.
        if '\n' in self._u_buffer:
            lu_chunks = self._u_buffer.rpartition(u'\n')
            u_line = '%s%s' % (lu_chunks[2], u_end)
            self._u_buffer = '%s\n' % self._u_buffer.rpartition(u'\n')[0]

        # Now case 1b is the only one that needs to be processed.
        else:
            u_line = '%s%s' % (self._u_buffer, u_end)
            self._u_buffer = ''

        return u_line

    def _get_chunk_from_end(self):
        """
        Function to get a new chunk of data from the end of the file.
        :return:
        """
        i_end = self._o_file.tell()
        i_start = i_end - self.i_block
        i_start = max(i_start, 0)

        # The problem with utf8 (as far as I know) is that some characters use one byte, while others use two. That
        # means that you could split a character in half when getting a chunk of data (resulting in an
        # UnicodeDecodeError). The best way I can imagine to solve this issue is to try to decode and then, if I find an
        # error, move backward an extra byte.
        try:
            self._o_file.seek(i_start, 0)
            u_data = self._o_file.read(i_end - i_start)
        except UnicodeDecodeError:
            if i_start > 0:
                i_start -= 1
                self._o_file.seek(i_start, 0)
                u_data = self._o_file.read(i_end - i_start)
            else:
                raise UnicodeDecodeError

        self._o_file.seek(i_start, 0)

        return u_data

    def close(self):
        """
        Closing method for the BackReader file.

        In a normal usage of the class, you would use "with", avoiding to manually opening and closing the file. But
        in certain cases (like reading some lines and putting them in one list, and reading later some more and putting
        them in a second list) it can be handy to have the manual methods.
        :return:
        """
        if self._o_file:
            self._o_file.close()
        self._o_file = None

    def open(self):
        """
        Opening method for the Backreader file.

        Same comment as close method. Normally you don't need this method but it can be handy in special cases.
        :return:
        """
        self._u_buffer = u''
        self._o_file = codecs.open(self.u_file, 'r', 'utf8')
        self._o_file.seek(0, 2)


class FilePath(object):
    """
    Class to handle file information: FilePath ps_name, root, extension, etc...
    """

    def __init__(self, *u_path):
        self.u_path = os.sep.join(u_path)

    def __eq__(self, po_other):
        b_equal = False
        if self.absfile().u_path == po_other.absfile().s_path:
            b_equal = True
        return b_equal

    def __str__(self):
        # TODO: replace with my str method from class_to_string
        u_out = '<FilePath>\n'
        u_out += '  .s_path: %s\n' % self.u_path
        u_out += '  .u_root: %s\n' % self.u_root
        u_out += '  .o_root: <FilePath> %s\n' % self.o_root.u_path
        u_out += '  .ps_file: %s\n' % self.u_file
        u_out += '  .s_name: %s\n' % self.u_name
        u_out += '  .u_ext:  %s\n' % self.u_ext
        return u_out

    def _get_elems(self):
        """
        Method to get a list with all the elems of the filepath as a list of unicode.
        :return: A list of unicode strings
        :rtype List[Unicode]
        """

        # If the path starts in root u"/", the first element is empty, u"". That's perfectly logical but if you try to
        # build back the FilePath object by doing FilePath(*lu_elements), the first empty element is not understood. So
        # the path is relative.
        return self.u_path.split(os.sep)

    def _get_o_root(self):
        return FilePath(os.path.dirname(self.u_path))

    def _get_u_root(self):
        return os.path.dirname(self.u_path)

    def _get_u_full_file(self):
        """
        Method to get the full file ps_name including extension.
        :return:
        """
        return os.path.basename(self.u_path)

    def _get_u_name(self):
        u_file = self.u_file
        if '.' in u_file:
            u_name = u_file.rpartition('.')[0]
        else:
            u_name = u_file
        return u_name

    def _get_u_ext(self):
        u_file = self.u_file
        if '.' in u_file:
            u_ext = u_file.rpartition('.')[2]
        else:
            u_ext = ''
        return u_ext

    def _get_size(self):
        """
        Method to get the file size in bytes.

        :return: The file size as an integer.
        :rtype int
        """
        # TODO: If the file/dir doesn't exist, return None

        if self.is_file():
            i_size = os.path.getsize(self.u_path)

        else:
            i_size = 0
            for o_elem in self.content(pb_recursive=True, ps_type='all'):
                i_size += o_elem.i_size

        return i_size

    def _get_size_h(self):
        """
        Method to get the file size in human-readable format.
        :return:
        """
        return file_size_format(self.i_size, pi_jump=1024, pu_suffix=u'B')

    def _get_mod_time(self):
        """
        Method to get the modified time
        :return:
        """
        o_mod_time = None
        if self.b_exists:
            f_mod_time = os.path.getmtime(self.u_path)
            o_mod_time = datetime.datetime.fromtimestamp(f_mod_time)

        return o_mod_time

    def absfile(self):
        """
        Method that returns a new FilePath object with the path normalized.
        :return: a FilePath object.
        """
        u_abs_path = os.path.abspath(self.u_path.encode('utf8')).decode('utf8')
        o_abs_file = FilePath(u_abs_path)
        return o_abs_file

    def common_prefix(self, *po_other_fp):
        """
        Method to return the filepath of the common prefix between this object and another one.
        :param po_other_fp:
        :return:
        """

        lu_paths = [self.u_path]
        for o_other_fp in po_other_fp:
            lu_paths.append(o_other_fp.s_path)

        return FilePath(os.path.commonprefix(lu_paths))

    def content(self, pb_recursive=False, ps_type='all', ptu_exts=()):
        """
        Method that returns a list with the contents of the file object. If the file object is a file, the content will
        be always empty since a file doesn't contain other files or directories.

        :param pb_recursive: If True, the content search will be recursive.

        :param ps_type: Content elements to get: 'all' => everything, files and dirs;
                        'files' => just files;
                        'dirs' => just directories.

        :param ptu_exts: Tuple with extension of files you want to keep. e.g. (u'jpg', 'png'). Be careful when using it
                         with directories.

        :type pb_recursive: bool
        :type ps_type: str
        :type ptu_exts: Tuple[unicode]

        :return: A list of FilePath objects
        """

        # [1/3] Getting all the content
        #------------------------------
        lo_elems_fp = []

        if self.is_dir():
            if not pb_recursive:
                for u_element in os.listdir(self.u_path):
                    u_full_path = os.path.join(self.u_path, u_element)
                    o_file_object = FilePath(u_full_path)
                    lo_elems_fp.append(o_file_object)

            else:
                for u_root, lu_dirs, lu_files in os.walk(self.u_path):
                    lu_elements = lu_dirs + lu_files
                    for u_element in lu_elements:
                        u_full_path = os.path.join(u_root, u_element)
                        o_fp = FilePath(u_full_path)
                        lo_elems_fp.append(o_fp)

        # [2/3] Filtering by type (file and/or dir)
        #-------------------------------------------
        lo_type_clean_elems_fp = []
        for o_elem_fp in lo_elems_fp:
            if ps_type == 'all':
                lo_type_clean_elems_fp.append(o_elem_fp)
            elif ps_type == 'files':
                if o_elem_fp.is_file():
                    lo_type_clean_elems_fp.append(o_elem_fp)
            elif ps_type == 'dirs':
                if o_elem_fp.is_dir():
                    lo_type_clean_elems_fp.append(o_elem_fp)

        # [3/3] Filtering by extension
        #------------------------------
        lo_ext_clean_elements_fp = []
        if not ptu_exts:
            lo_ext_clean_elements_fp = lo_type_clean_elems_fp

        else:
            for o_elem_fp in lo_elems_fp:
                if o_elem_fp.has_exts(*ptu_exts):
                    lo_ext_clean_elements_fp.append(o_elem_fp)

        return lo_ext_clean_elements_fp

    def _get_exists(self):
        """
        Method that checks if the path _get_exists or not.
        :return: True/False
        """
        if os.path.exists(self.u_path):
            b_exists = True
        else:
            b_exists = False

        return b_exists

    def root_exists(self):
        """
        Method to check if the root path _get_exists or not.
        :return: True/False
        """
        if os.path.isdir(self.u_root):
            b_exists = True
        else:
            b_exists = False

        return b_exists

    def root_prepend(self, *pu_path):
        """
        Method to add extra elements at the beginning of the root. i.e. cc/dd.jpg -> aa/bb/cc/dd.jpg

        :param pu_path: Elements to prepend. i.e. "aa", "bb"
        :type pu_path: Unicode

        :return: Nothing
        """
        # --- TEST CODE ---
        #print('0: %s' % pu_path)
        #print('1: %s' % self.u_root)
        #print(os.path.join(*pu_path, self.u_root))
        #quit()
        # ------ end ------
        pass

    def has_exts(self, *pu_ext):
        """
        Method to check if the FilePath object has certain extension no matter the casing.

        :param pu_ext: Extension to test. i.e. 'jpg'
        :type pu_ext: Unicode

        :return: True/False, if the file extension matches or not (casi insensitive, jpg and JPG will output the same
                 result).
        """
        b_has_ext = False
        for u_ext in pu_ext:
            if self.u_ext.lower() == u_ext.lower():
                b_has_ext = True
                break
        return b_has_ext

    def is_dir(self):
        """
        Method to check if the file object is a directory.

        :return: True/False
        """

        if self._get_exists() and os.path.isdir(self.u_path):
            b_is_dir = True

        else:
            b_is_dir = False

        return b_is_dir

    def is_file(self):
        """
        Method to check if the file object is a file.

        :return: True/False
        :rtype Bool
        """

        if self._get_exists() and os.path.isfile(self.u_path):
            b_is_file = True

        else:
            b_is_file = False

        return b_is_file

    def is_inside(self, po_parent_dir):
        """
        Method to check whether a filepath is inside another one (which must be a directory).

        NOTE: the method will automatically convert the relative paths to absolute ones. Be careful when passing
              relative paths as parameter.

        :param po_parent_dir:
        :type po_parent_dir FilePath
        :return:
        """
        if not po_parent_dir.is_dir():
            raise ValueError('The parent filepath is not a valid dir "%s"' % po_parent_dir.u_path)
        else:
            b_inside = False
            o_common_prefix = po_parent_dir.absfile().common_prefix(self.absfile())
            if o_common_prefix == po_parent_dir.absfile():
                b_inside = True

            return b_inside

    def get_file_in_subdirs(self, pu_file, *subdirs):
        """
        Method to get the first appearance of a file in certain list of subdirs.

        For example, if we have:

            folder_1
                aaa.png
            folder_2
                aaa.png

        And we call .get_file_in_subdirs('aaa.png', 'folder_1', 'folder_2'). The fp object of folder_1/aaa.png will be
        returned.

        :type pu_file: unicode Name of the file to search for.

        :type subdirs: unicode Name of the directories to search for by the order we want to search.

        :return: The first matched FilePath object if the file _get_exists, None in other case.
        """
        if self.is_file():
            raise ValueError
        else:
            o_matched_fp = None
            for u_subdir in subdirs:
                o_candidate_fp = FilePath(self.u_path, u_subdir, pu_file)
                if o_candidate_fp.is_file():
                    o_matched_fp = o_candidate_fp
                    break

            return o_matched_fp

    # def _get_ctime(self):
    #     """
    #     Method to get the creation time of the file.
    #     :return: A datetime object.
    #     """
    #     o_creation_datetime = None
    #
    #     if self.is_file():
    #         f_seconds_from_epoc = os.path.getctime(self.s_path)
    #         o_creation_datetime = datetime.datetime.fromtimestamp(f_seconds_from_epoc)
    #
    #     return o_creation_datetime
    #
    # o_ctime = property(fget=_get_ctime, fset=None)

    def uncommon_suffix(self, po_other_fp):
        """
        Method to return the uncommon part for different fp objects. i.e.
        :param po_other_fp:
        :return:
        """

        # [1/?] We find the common part between both FilePaths
        # -----------------------------------------------------
        o_common_fp = self.common_prefix(po_other_fp)
        i_suffix_start = len(o_common_fp.u_path)

        # [2/?] Then we get the uncommon parts
        # -------------------------------------
        u_self_suffix = self.u_path[i_suffix_start:]
        u_other_suffix = po_other_fp.s_path[i_suffix_start:]

        # Because we are working with paths, the different parts start always with "/" (or "\" in the case of Windows).
        # So the actual different part needs that to be removed.
        # TODO: Check what happens when the two compared paths are exactly the same
        return FilePath(u_self_suffix[1:]), FilePath(u_other_suffix[1:])

    b_exists = property(fget=_get_exists)
    i_size = property(fget=_get_size)
    lu_elements = property(fget=_get_elems)
    o_mod_time = property(fget=_get_mod_time)
    o_root = property(fget=_get_o_root)
    u_root = property(fget=_get_u_root)
    u_file = property(fget=_get_u_full_file)
    u_name = property(fget=_get_u_name)
    u_ext = property(fget=_get_u_ext)
    u_size = property(fget=_get_size_h)


# Functions
#=======================================================================================================================
def file_size_format(pi_bytes, pi_jump=1024, pu_suffix=u'B'):
    """
    Function to convert integer numbers to human-readable format
    
    :param pi_bytes: Value you want to convert to human-readable format. e.g. 1545167316
    :type pi_bytes: Int

    :param pi_jump: Whether 1K equals to 1000 units or 1024. You could use any other number but... WHY?
    :param pu_suffix: Name of the unit, u'B' stands for Bytes, but you could use any other unit.
    :return:
    """

    # [0/?] Initialization
    # ---------------------
    # For crazy jumps, the units will by KxB, MxB...
    lu_units = ['', 'Kx', 'Mx', 'Gx', 'Tx', 'Px', 'Ex', 'Zx', 'Yx']

    # for standard 1000 jumps KB, MB, GB, TB...
    if pi_jump == 1000:
        lu_units = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']

    # and for standard computer science 1024 jumps, KiB, MiB, GiB...
    elif pi_jump == 1024:
        lu_units = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']

    # [1/?] Finally, we build the output string
    # -----------------------------------------
    for u_unit in lu_units:
        if abs(pi_bytes) < float(pi_jump):
            u_out = u'%3.1f %s%s' % (pi_bytes, u_unit, pu_suffix)
            break

        pi_bytes /= float(pi_jump)

    # If the loop finished, the number is already divided by pi_jump, but we don't have any bigger unit, so...
    else:
        pi_bytes *= float(pi_jump)
        u_out = u'%3.1f %s%s' % (pi_bytes, lu_units[-1], pu_suffix)

    return u_out


def get_cwd():
    """
    Function to get the current working directory.

    :return: A FilePath object.
    """
    u_cwd = os.getcwd().decode('utf8')
    o_cwd = FilePath(u_cwd)
    return o_cwd


def read_nlines(po_file, pi_lines):
    """
    Function to read n lines from a file
    :param po_file:
    :param pi_lines:
    :return:
    """
    i_line = 0
    lu_lines = []

    try:
        for u_line in po_file:
            i_line += 1
            lu_lines.append(u_line.rstrip(u'\n'))
            if i_line == pi_lines:
                break

    except IOError:
        pass

    return lu_lines


def clean_dir(ps_dir):
    """
    Function to clean the contents of a directory.

    :param ps_dir:
    :type ps_dir: Str

    :return: Nothing.
    """
    for s_element in os.listdir(ps_dir):
        file_path = os.path.join(ps_dir, s_element)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def init_dir(ps_dir):
    """
    Function that "initialises" a directory:

        a) if it doesn't exist, the function will create it;
        b) if it exists, the function will remove its content.

    :param ps_dir: Path of the directory to be initialised.
    :type ps_dir: Str

    :return: Nothing.
    """
    if os.path.isdir(ps_dir):
        clean_dir(ps_dir)
    else:
        os.makedirs(ps_dir)


def compute_crc(ps_file):
    """
    Function to compute the CRC32 of a file. This function will be used mostly in unit-tests to validate that created
    files are correct.

    :param ps_file:
    :type ps_file: Str

    :return:
    :rtype: Str
    """
    i_prev = 0

    with open(ps_file, 'rb') as o_file:
        # h_chunk is a byte-string, but I use h for "hexa" since I have no better idea about what to use now.
        for h_chunk in o_file:
            i_prev = zlib.crc32(h_chunk, i_prev)

    s_crc32 = "%X" % (i_prev & 0xFFFFFFFF)
    return s_crc32.lower()


def uncompress(ps_file, ps_dst_dir=''):
    """
    Function to uncompress files.

    :param ps_file: Path of the file we want to decompress.
    :type ps_file: Str

    :param ps_dst_dir: Path of the dir where the uncompressed data will be placed.
    :type ps_dst_dir: Str

    :return: Nothing.
    """
    s_file = os.path.basename(ps_file)
    s_name, _, s_ext = s_file.rpartition('.')

    s_ext = s_ext.lower()
    dsc_decompressors = {'7z': _uncompress_7z, 'rar': _uncompress_rar, 'zip': _uncompress_zip}

    if ps_dst_dir:
        s_dir = ps_dst_dir
    else:
        s_dir = os.path.dirname(ps_file)

    if s_ext in dsc_decompressors:
        c_decompressor = dsc_decompressors[s_ext]
        c_decompressor(ps_file=ps_file, ps_dst_dir=s_dir)


def _uncompress_7z(ps_file, ps_dst_dir=''):
    """
    Function to uncompress 7z files.

    :param ps_file: Path of the file we want to decompress.
    :type ps_file: Str

    :param ps_dst_dir: Path of the dir where the uncompressed data will be placed.
    :type ps_dst_dir: Str

    :return: Nothing.
    """
    ls_cmd = ['7z', 'x', ps_file]

    if ps_dst_dir:
        ls_cmd += [f'-o{ps_dst_dir}']

    o_process = subprocess.Popen(ls_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_stdout, s_stderr = o_process.communicate()

    # TODO: Handle error messages


def _uncompress_rar(ps_file, ps_dst_dir=''):
    """
    Function to uncompress rar files.

    :param ps_file: Path of the file we want to decompress.
    :type ps_file: Str

    :param ps_dst_dir: Path of the dir where the uncompressed data will be placed.
    :type ps_dst_dir: Str

    :return: Nothing.
    """
    ls_cmd = ['unrar', 'x', ps_file]

    if ps_dst_dir:
        ls_cmd += [ps_dst_dir]

    o_process = subprocess.Popen(ls_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_stdout, s_stderr = o_process.communicate()

    # TODO: Handle error messages


def _uncompress_zip(ps_file, ps_dst_dir=''):
    """
    Function to uncompress zip files.

    :param ps_file: Path of the file we want to decompress.
    :type ps_file: Str

    :param ps_dst_dir: Path of the dir where the uncompressed data will be placed.
    :type ps_dst_dir: Str

    :return: Nothing.
    """
    with zipfile.ZipFile(ps_file, 'r') as o_file:
        o_file.extractall(ps_dst_dir)


def patch_file(ps_file, ps_patch):
    """
    Function to patch a file IN PLACE because that's the functionality we require in emulauncher.

    The function will call external tools to perform the patching. When those tools are not compatible with in-place
    patching, an intermediate patched file will be created and then removed.

    :param ps_file: Path of the file to be patched.
    :type ps_file: Str

    :param ps_patch: Path of the patch_file to be applied.
    :type ps_patch: Str

    :return: Nothing.
    """
    # Dictionary with patcher per extension
    dsc_patcher = {'bps':    _patch_flips,
                   'ips':    _patch_flips,
                   'ppf':    _patch_ppf,
                   'xdelta': _patch_xdelta}

    s_ext = os.path.basename(ps_patch).rpartition('.')[2].lower()

    if s_ext not in dsc_patcher:
        s_msg = f'Unknown patch_file extension "{s_ext}"'
        raise ValueError(s_msg)
    else:
        c_patcher = dsc_patcher[s_ext]
        c_patcher(ps_file=ps_file, ps_patch=ps_patch)


def _patch_flips(ps_file, ps_patch):
    """
    Function to patch files using Flips which is compatible with .ips, and .bps patches.

    :param ps_file: Path of the file to be patched.
    :type ps_file: Str

    :param ps_patch: Path of the patch to be applied.
    :type ps_patch: Str

    :return: Nothing.
    """
    # We use a local compiled version of Flips, I don't know what are its dependencies; I hope it easily works in
    # any common Linux machine.
    s_tool_src = os.path.join(cons.s_SCRIPT_ROOT, 'resources', 'tools', 'Flips', 'flips')
    s_tool_dst = os.path.join('/tmp/flips')
    shutil.copyfile(s_tool_src, s_tool_dst)
    os.chmod(s_tool_dst, 0o700)

    ts_cmd = (s_tool_dst, '--apply', '--exact', ps_patch, ps_file)
    o_process = subprocess.Popen(ts_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_stdout, s_stderr = o_process.communicate()


def _patch_ppf(ps_file, ps_patch):
    """
    Function to apply xdelta3 patches.

    :param ps_file: Path of the file to be patched.
    :type ps_file: Str

    :param ps_patch: Path of the patch to be applied.
    :type ps_patch: Str

    :return: Nothing.
    """
    # We use a local compiled version of applyppf, I don't know what are its dependencies; I hope it easily works in
    # any common Linux machine.
    s_tool_src = os.path.join(cons.s_SCRIPT_ROOT, 'resources', 'tools', 'ApplyPPF', 'applyppf')
    s_tool_dst = os.path.join('/tmp/applyppf')
    shutil.copyfile(s_tool_src, s_tool_dst)
    os.chmod(s_tool_dst, 0o700)

    ts_cmd = (s_tool_dst, 'a', ps_file, ps_patch)
    o_process = subprocess.Popen(ts_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_stdout, s_stderr = o_process.communicate()


def _patch_xdelta(ps_file, ps_patch):
    """
    Function to apply xdelta3 patches.

    Xdelta3 doesn't allow to patch_file in place, so we have to create an intermediate file.

    :param ps_file: Path of the file to be patched.
    :type ps_file: Str

    :param ps_patch: Path of the patch to be applied.
    :type ps_patch: Str

    :return: Nothing.
    """
    s_ext = ps_file.rpartition('.')[2]
    #s_temp_file = os.path.join(f'/tmp/xdelta3_intermediate_file.{s_ext}')
    s_temp_file = f'{ps_file}.temp'

    ts_cmd = ('xdelta3', '-d', '-s', ps_file, ps_patch, s_temp_file)
    o_process = subprocess.Popen(ts_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_stdout, s_stderr = o_process.communicate()

    shutil.move(s_temp_file, ps_file)


def index_dir(ps_dir, pdts_index=None, pli_current_level=None, pts_ignore_exts=()):
    """
    Function to alphabetically index the files within a directory, so each file path will be indexed by their relative
    location in the tree structure. Below you can see an example of files within a directory and their index:

        ROOT:
            [0] file_a.txt
            [1] file_b.txt

            DIR_A:
                [0, 0] file_a.txt
                [0, 1] file_b.txt

            DIR_B:
                [1, 0] file_a.txt
                [1, 1] file_b.txt

                DIR_C:
                    [1, 0, 0] file_a.txt
                    [1, 0, 1] file_b.txt

    :param ps_dir: Directory to be indexed.
    :param ps_dir: Str

    :param pdts_index: Index of already indexed files. This parameter should only be used by the function when calling
                       itself recursively.
    :type pdts_index: Dict[Tuple:Str]

    :param pli_current_level: Current level of the directory to be scanned. This parameter should only be used by the
                              function when calling itself recursively.
    :type pli_current_level: List[Int]

    :param pts_ignore_exts: Tuple with extensions to be ignored (case insensitive).
    :type pts_ignore_exts: Tuple[Str]

    :return: Dictionary of indexed files. The key is a tuple indicating the numerical "path" of the file, and the value
             is the actual path of each file.
    :rtype: Dict[Tuple:Str]
    """
    # Initialisation
    #---------------
    if pdts_index is None:
        dts_index = {}
    else:
        # I prefer to make a copy, the performance penalty is small for the size of directories I use, and I think the
        # code is cleaner.
        dts_index = pdts_index.copy()

    if pli_current_level is None:
        li_current_level = []
    else:
        li_current_level = pli_current_level.copy()

    # Traversing the folder structure
    i_file_counter = None
    i_dir_counter = None
    for s_elem in sorted(os.listdir(ps_dir)):
        s_full_path = os.path.join(ps_dir, s_elem)

        if os.path.isfile(s_full_path):
            s_ext = s_elem.rpartition('.')[2].lower()
            if s_ext not in pts_ignore_exts:
                if i_file_counter is None:
                    i_file_counter = 0
                else:
                    i_file_counter += 1

                li_file_index = li_current_level + [i_file_counter]
                dts_index[tuple(li_file_index)] = s_full_path

        elif os.path.isdir(s_full_path):
            if i_dir_counter is None:
                i_dir_counter = 0
            else:
                i_dir_counter += 1

            li_dir_level = li_current_level + [i_dir_counter]
            dts_index = index_dir(ps_dir=s_full_path,
                                  pdts_index=dts_index,
                                  pli_current_level=li_dir_level,
                                  pts_ignore_exts=pts_ignore_exts)

    return dts_index


def index_patch_dir(ps_dir):
    """
    Function to "index" the files of a decompressed patch
    :param ps_dir:
    :return:
    """
    # The patch naming convention is [CRC32]-[INDEX].[EXTENSION] and we need to capture the [INDEX] part of it that can
    # be a single number value for single file ROMS (e.g. "00000000-0.ppf") or two numbers for multi-file ROMs (e.g.
    # "00000000-0-0.ppf"). There is no need to check the CRC32 part, and actually, that can potentially change in the
    # future to include for example the real name (at the time) of the ROM. So, we will only capture the index values.

    # Dictionary with patches where the key is the
    s_pattern = r'(.+?)-(\d+)(-(\d+))?'
    dti_patches = {}
    for s_elem in os.listdir(ps_dir):
        s_full_path = os.path.join(ps_dir, s_elem)
        s_ext = s_elem.rpartition('.')[2].lower()

        if os.path.isfile(s_full_path) and s_ext not in ('txt',):
            o_match = re.search(s_pattern, s_elem, flags=re.IGNORECASE)
            if o_match is not None:
                li_levels = []
                i_index_0 = int(o_match.group(2))
                li_levels.append(i_index_0)

                try:
                    i_index_1 = int(o_match.group(4))
                    li_levels.append(i_index_1)
                except TypeError:
                    pass

                dti_patches[tuple(li_levels)] = s_full_path

    return dti_patches
