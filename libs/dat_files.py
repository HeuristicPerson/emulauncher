"""
Library to load data from .dat files (ClrMamePro and XML format only) for ROMsets.

--- This library is part of the "common_libs" package. Never modify it outside it. ---

Version: Python 3 - 2022-12-03

Link with information about different .dat file formats:

    https://github.com/SabreTools/SabreTools/wiki/DatFile-Formats#mame-list-xml-format
"""

import codecs
import configparser
import xml.etree.cElementTree
import os
import re


# Constants
#=======================================================================================================================
# List of ROM extensions to ignore when obtaining "clean" values (size, and hashes)
_ts_IGNORE_EXTS = ('cue',)

# Text values than will be considered as True
ss_TRUE_VALUES = ('1', 'yes', 'true')


# Classes
#=======================================================================================================================
class Filter:
    """
    Class to store information about a filter that will be applied later to Dat.
    """

    def __init__(self, s_attribute, s_method, *x_values):
        self.s_attribute = s_attribute
        self.s_method = s_method
        self.lx_values = x_values

        for x_value in x_values:
            if not isinstance(x_value, (str, int, float)):
                raise Exception('ERROR, type "%s" is not valid value for a filter' % type(x_value))

        # TODO: Check for valid values for s_method. So far 'equals' is the only one implemented.
        # TODO: Create a check for x_values to avoid the case when you create a wrong filter with a tuple (123, 145)

    def __str__(self):
        s_out = ''
        s_out += '<Filter>\n'
        s_out += '  .s_attribute: %s\n' % self.s_attribute
        s_out += '  .s_method:    %s\n' % self.s_method
        s_out += '  .lx_values:   %s' % str(self.lx_values)

        return s_out.encode('utf8', 'strict')


class Field:
    """
    Class to store configuration data for CSV import method for Dat.
    """
    def __init__(self, pi_src_column, ps_dst_field):
        self.i_src_column = pi_src_column
        self.s_dst_field = ps_dst_field


class Dat(object):
    """
    Class to store a list of games, each game can contain different ROM files data. The information can be read/write to
    disk ROM file objects.

    :ivar _do_romsets: Dict[Str:RomSet]

    """

    def __init__(self, ps_file=''):

        # TODO: Dat should contain an internal registry with all the manipulations suffered by the object so
        #       when you export the file to disk you know the information is not coming directly from the RAW dat file.
        # I think that some "MODIFIED" flags would be enough like .db_flags{'added_sets': True, 'removed_sets': True...}

        # TODO: Add missing properties as attributes of the class
        # List of fields that DatUtil allows in the header of a .dat. All of them should be included in the class. It
        # has been obtained from: https://forum.recalbox.com/topic/4537/tutorial-datutil
        #
        #   -A author                                   <- s_author
        #   -V version                                  <- s_version
        #   -C category
        #   -R ref name                                 <- s_name
        #   -F full name (i.e. description)             <- s_description
        #   -T date
        #   -E e-mail
        #   -H homepage                                 <- s_homepage
        #   -U url
        #   -O comment                                  <- s_comment
        #   -M merging (none, split or full)
        #   -P packing (zip or unzip)
        #   -N nodump (obsolete, required or ignore)

        self.s_name = ''         # internal name of the dat file.
        self.s_description = ''  # description of the dat file.
        self.s_version = ''      # version of the dat file (usually a date).
        self.s_comment = ''      # extra comment for the dat file.
        self.s_type = ''         # type of DAT file the data comes from.
        self.s_author = ''       # Author of the dat.
        self.s_homepage = ''     # Homepage of the author of the DAT.

        self._do_romsets = {}    # list of game objects inside the dat file

        self._db_flags = {'from_dat': False,
                          'sets_added': False,
                          'sets_deleted': False,
                          'data_imported': False}       # Modification flags

        self._ts_valid_search_fields = ('_i_year',
                                        's_ccrc32', 's_dcrc32',
                                        's_cmd5', 's_dmd5',
                                        's_csha1', 's_dsha1',
                                        's_desc', 's_name', 's_auth')

        if ps_file:
            self.read_from_dat(ps_file)

    def __str__(self):
        s_out = '<Dat>\n'
        s_out += '  ._db_flags:  %s\n' % str(self._db_flags)
        s_out += '  .s_name:     %s\n' % self.s_name
        s_out += '  .s_desc:     %s\n' % self.s_description
        s_out += '  .s_version:  %s\n' % self.s_version
        s_out += '  .s_homepage: %s\n' % self.s_homepage
        s_out += '  .s_comment:  %s\n' % self.s_comment
        s_out += '  .s_type:     %s\n' % self.s_type
        s_out += '  .s_author:   %s\n' % self.s_author
        s_out += '  .i_romsets:  %s\n' % self.i_romsets
        s_out += '  .i_baddumps: %s\n' % self.i_baddumps
        s_out += '  .i_devices:  %s\n' % self.i_devices
        s_out += '  .i_nodumps:  %s\n' % self.i_nodumps
        return s_out

    def __iter__(self):
        """

        :return:
        :rtype Iterator[RomSet]
        """
        return iter(sorted(self._do_romsets.values(), key=lambda o_romset: o_romset.s_desc.lower()))

    def __len__(self):
        return self.i_romsets

    def add_romset(self, po_romset):
        """
        Internal method to add games to the container WITHOUT any kind of duplicity or other kind of check.

        :param po_romset:
        :type po_romset: RomSet
        """
        if po_romset.s_name in self._do_romsets:
            raise ValueError('ERROR: ROMset already exists in the Dat.')

        self._do_romsets[po_romset.s_name] = po_romset

    def del_romset(self, ps_name):
        """
        Method to remove a ROMset from the container.

        :param ps_name: The name of the romset to be deleted.
        :type ps_name: Str
        
        :return: True if a matching ROMset was found and deleted.
        :rtype Bool
        """

        b_found = False
        if ps_name in self._do_romsets:
            b_found = True
            del self._do_romsets[ps_name]

        return b_found

    def get_duplicated_crc32(self):
        """
        Method to return ROMsets with duplicated CRC32

        :return: a list of ROMsets
        :rtype: List[RomSet]
        """

        # [1/3] We count how many times each CRC32 appears in the Dat
        #------------------------------------------------------------------------
        di_romsets = {}
        for o_romset in self:
            s_ccrc32 = o_romset.s_ccrc32
            if s_ccrc32 not in di_romsets:
                di_romsets[s_ccrc32] = 1
            else:
                di_romsets[s_ccrc32] += 1

        # [2/3] Then we keep only those that appear more than once
        #---------------------------------------------------------
        ls_repeated_ccrc32 = []
        for s_ccrc32, i_times in di_romsets.items():
            if i_times > 1:
                ls_repeated_ccrc32.append(s_ccrc32)

        # [3/3] For each repeated CRC32, we get all the ROMsets with that CRC32
        #----------------------------------------------------------------------
        do_romset_collisions = {}
        for s_ccrc32 in ls_repeated_ccrc32:
            do_romset_collisions[s_ccrc32] = self.get_romsets_by_field('s_ccrc32', False, s_ccrc32)

        return do_romset_collisions

    def _show_duplicates(self):
        """
        Method to quick show duplicates, so you can fix the problems using other tools or manually.

        WARNING! This method can be really slow.

        :return: A list of lists.
        """

        # 1st we group the ROMsets with equal MD5 in a dictionary, so for each MD5 (key), we have a list o ROMset names
        dls_duplicated_romsets = {}
        for o_romset in self:
            if o_romset.s_dmd5 not in dls_duplicated_romsets:
                dls_duplicated_romsets[o_romset.s_dmd5] = []

            dls_duplicated_romsets[o_romset.s_dmd5].append(o_romset.s_name)

        # Then we filter out those "families" of ROMsets with only one member so we actually have a dictionary of
        # ROMsets with duplicated MD5
        dls_clean_duplicated_romsets = {}
        for s_key, ls_values in dls_duplicated_romsets.iteritems():
            if len(ls_values) > 1:
                dls_clean_duplicated_romsets[s_key] = set(ls_values)

        return dls_clean_duplicated_romsets

    def empty(self):
        """
        Method to clean all the games of the container but keeping the meta-data.

        :return: Nothing
        """
        self._do_romsets = {}

    def copy_metadata_from(self, po_game_container):
        """
        Method to copy meta-data information (everything but the list of games itself and the number of games) from
        other Dat object.

        :param po_game_container: External Dat object.
        """

        # Modification of data
        self.s_name = po_game_container.s_name
        self.s_description = po_game_container.s_description
        self.s_version = po_game_container.s_version
        self.s_homepage = po_game_container.s_homepage
        self.s_comment = po_game_container.s_comment
        self.s_type = po_game_container.s_type
        self.s_author = po_game_container.s_author

        s_log_msg = ''
        s_log_msg += 'Metadata copied: '
        s_log_msg += 's_name="%s" ' % self.s_name
        s_log_msg += 's_desc="%s" ' % self.s_description
        s_log_msg += 's_version="%s" ' % self.s_version
        s_log_msg += 's_comment="%s" ' % self.s_comment
        s_log_msg += 's_type="%s" ' % self.s_type
        s_log_msg += 's_author="%s" ' % self.s_author

    def filter(self, o_filter):
        """
        Method to filter in/out games depending on a field name and allowed/disallowed values for that field.

        :param o_filter: Filter object.
        :type o_filter Filter

        :return: A list of games that match or don't match your filter criteria.
        """

        # Two Dat objects are created to store the games that matched the filter and the games that didn't match it.
        o_matched_container = Dat()
        o_matched_container.copy_metadata_from(self)
        o_unmatched_container = Dat()
        o_unmatched_container.copy_metadata_from(self)

        for o_game in self:

            # The first thing to do is (to try) to obtain o_dat_game.<s_attribute>
            try:
                x_value = getattr(o_game, o_filter.s_attribute)

            except AttributeError:
                raise Exception('ERROR: You are trying to access the unknown attribute "%s"' % o_filter.s_attribute)

            # Then we can filter. Since we are filtering already unique games present in our container, we don't need
            # to perform any uniqueness test while adding the games to the matched/unmatched containers. So, we use the
            # method add_romset which doesn't perform that test and is much faster than the equivalent one with test
            # add_romset.
            if o_filter.s_method == 'equals':
                if x_value in o_filter.lx_values:
                    o_matched_container.add_romset(o_game)

                else:
                    o_unmatched_container.add_romset(o_game)

        return o_matched_container, o_unmatched_container

    def get_romset_by_name(self, ps_name):
        """
        Method to find and return a ROMset by its name. This method will be much quicker than using get_romsets_by_field
        since it doesn't go through all the ROMsets contained in self._do_romsets.

        :param ps_name:
        :type ps_name: Unicode

        :return: The found ROMset or None if no ROMset is found
        :rtype: Union[RomSet, None]
        """
        try: 
            o_romset = self._do_romsets[ps_name]
        except KeyError:
            o_romset = None

        return o_romset

    def get_romsets_by_field(self, ps_field, pb_first=False, ptx_search_values=()):
        """
        Method to get a list of MULTIPLE GAMES with certain content in a field.

        :param ps_field: Name of the field to use for the matching. i.e. '_i_year'
        :type ps_field unicode

        :param pb_first: Whether the function will just return the first result or all of them.
        :type pb_first bool

        :param ptx_search_values: Content of the field to search for. i.e. 1985, 1986

        :return: A list with the found romsets.
        """

        # This search function doesn't correctly if the search field is text and the ptx_search_values is incorrectly
        # given as a string. Notice below that the "search" is done with an "in". So, so AAA would match AA. For that
        # reason I check the type of the parameter.
        if not isinstance(ptx_search_values, tuple):
            raise ValueError('ERROR: ptx_search_values must be a tuple. %s given instead' % type(ptx_search_values))

        lo_romsets = []

        if ps_field not in self._ts_valid_search_fields:
            raise ValueError('Error: ps_field must be one of %s' % str(self._ts_valid_search_fields))

        else:
            for o_romset in self:
                if getattr(o_romset, ps_field) in ptx_search_values:
                    lo_romsets.append(o_romset)
                    if pb_first:
                        break

        return lo_romsets

    def read_from_dat(self, ps_file):
        """
        Method to load Dat data from a file on disk.

        :param ps_file: File containing the data. i.e. '/home/john/mame.dat'
        :type ps_file: Unicode

        :return: Nothing.
        """

        # If the file is not present, we raise an error
        if not os.path.isfile(ps_file):
            raise ValueError('Can\'t find dat file "%s"' % ps_file)

        o_file = codecs.open(ps_file, 'rb', 'utf8', 'ignore')

        # We try to automatically identify it reading the beginning of the file.
        s_first_line = o_file.readline()
        o_file.close()

        # Identifying ClrMamePro mode
        if (s_first_line.find('clrmamepro') != -1) or (s_first_line.find('emulator') != -1):
            s_format = 'cmp'

        # Identifying Xml mode
        elif s_first_line.find('<?xml') != -1:
            s_format = 'xml'

        # Unknown format error raise
        else:
            raise IOError('Unknown DAT format')

        # Loading the file using the different readers depending on the format parameter
        if s_format == 'cmp':
            self._read_from_cmp(ps_file)
        elif s_format == 'xml':
            s_xml_type = self._identify_xml_format(ps_file)
            if s_xml_type == 'mame':
                self._read_from_xml_mame(ps_file)
            else:
                self._read_from_xml_generic(ps_file)

        # We alter the proper flag
        self._db_flags['from_dat'] = True

    def save_to_dat(self, ps_file, ps_format):
        """
        Method to save the contents of the Dat to a .dat file

        :param ps_file: Path of the file to be saved. e.g. '/home/john/my_new_dat.dat'
        :type ps_file: Unicode

        :param ps_format: Format of the dat to be generated. So far, the only format available is 'cmp' for ClrMamePro
                          format.
        :type ps_format: Unicode

        :return: Nothing
        """
        if ps_format == 'cmp':
            s_data = self._to_clrmamepro()
        else:
            raise ValueError

        with codecs.open(ps_file, 'w', 'utf8') as o_file:
            o_file.write(s_data)

    def to_dict(self, ps_property):
        """
        Method to return a dictionary with all the romsets keyed by the desired property "ps_property". No checks will
        be performed so if the values of ps_property are not unique for all the RomSets, the later occurrences will
        overwrite the older ones.

        :param ps_property:
        :type ps_property: Str

        :return:
        """
        do_output = {}
        for o_romset in self._do_romsets:
            do_output[getattr(o_romset, ps_property)] = o_romset

        return do_output

    def _read_from_cmp(self, ps_file):
        """
        Method to process ClrMamePro DATs.
        """
        self.s_type = 'ClrMamePro'

        o_file = codecs.open(ps_file, 'rb', 'utf8', 'ignore')

        b_head_mode = False
        b_game_mode = False

        ls_head_strings = []    # List that will contain the multiple lines with data from the heading.
        ls_game_strings = []    # List that will contain the multiple lines with data for a game.

        for s_line in o_file:

            # Detection of the start of the heading of the file
            if (s_line.find('clrmamepro (') == 0) or (s_line.find('emulator (') == 0):
                b_head_mode = True
                continue

            # If we are in "head-mode" and the first character of the line is ")", it means we have reached the end of
            # the heading (so we have all its lines) and we can parse them.
            if b_head_mode and s_line.find(')') == 0:
                self.s_name = _dat_vertical_parse(ls_head_strings, 'name')
                self.s_description = _dat_vertical_parse(ls_head_strings, 'description')
                self.s_version = _dat_vertical_parse(ls_head_strings, 'version')
                self.s_comment = _dat_vertical_parse(ls_head_strings, 'comment')

                ls_head_strings = []
                b_head_mode = False
                continue

            # If we are in "head-mode", we add the found lines to a list that will be parsed later (look the code just
            # above).
            if b_head_mode:
                ls_head_strings.append(s_line)
                continue

            # RomSet data
            if s_line.find('game (') == 0:
                b_game_mode = True
                continue

            if b_game_mode and s_line.find(')') == 0:
                s_romset_name = _dat_vertical_parse(ls_game_strings, 'name')
                s_romset_description = _dat_vertical_parse(ls_game_strings, 'description')
                s_romset_author = _dat_vertical_parse(ls_game_strings, 'manufacturer')
                s_game_year = _dat_vertical_parse(ls_game_strings, 'year')
                if s_game_year == '':
                    s_game_year = '0'

                ls_game_roms = _dat_vertical_parse(ls_game_strings, 'rom', 'multi')

                o_dat_romset = RomSet(s_romset_name, s_romset_description)
                o_dat_romset.s_year = s_game_year
                o_dat_romset.s_auth = s_romset_author

                for s_game_rom in ls_game_roms:
                    # sometimes name has quotes " around and sometimes not, so it's safer to use size as end.
                    s_rom_name = _dat_horizontal_parse(s_game_rom, 'name ', 'size')

                    s_rom_size = _dat_horizontal_parse(s_game_rom, 'size ', ' ')
                    s_rom_crc = _dat_horizontal_parse(s_game_rom, 'crc ', ' ')
                    s_rom_md5 = _dat_horizontal_parse(s_game_rom, 'md5 ', ' ')
                    s_rom_sha1 = _dat_horizontal_parse(s_game_rom, 'sha1 ', ' ')

                    # So far, MAME is the only dat providing flags, and it's only one.
                    s_rom_flags = _dat_horizontal_parse(s_game_rom, 'flags ', ' ')
                    b_baddump = False
                    if s_rom_flags == 'baddump':
                        b_baddump = True

                    b_nodump = False
                    if s_rom_flags == 'nodump':
                        b_nodump = True

                    # create a rom object
                    o_rom = Rom()
                    o_rom.b_baddump = b_baddump
                    o_rom.b_nodump = b_nodump
                    o_rom.s_name = s_rom_name
                    o_rom.i_size = int(s_rom_size)
                    o_rom.s_crc32 = s_rom_crc.lower()
                    o_rom.s_md5 = s_rom_md5.lower()
                    o_rom.s_sha1 = s_rom_sha1.lower()

                    # add the rom object to the list
                    o_dat_romset.add_rom(o_rom)

                # We add the game to the container without any kind of check, we will do it later.
                self.add_romset(o_dat_romset)

                ls_game_strings = []
                b_game_mode = False
                continue

            # RomSet mode actions
            if b_game_mode:
                ls_game_strings.append(s_line)
                pass

    def _read_from_xml_generic(self, ps_file):
        """
        Method to populate the container from a generic .xml file. This format is compatible, for example, with No-Intro
        dats.

        :param ps_file: The path of the file to be read.
        :type ps_file: Unicode

        :return: Nothing, the object will be populated in place.
        """
        self.s_type = 'xml'

        o_xml_tree = xml.etree.cElementTree.parse(ps_file)
        o_xml_root = o_xml_tree.getroot()

        # Header information
        #-------------------
        # "<header>" section is optional in generic xml, so we need to take that in consideration.
        o_header = o_xml_root.find('header')
        if o_header is not None:
            self.s_name = o_header.find('name').text
            self.s_description = o_header.find('description').text
            self.s_version = o_header.find('version').text

            o_xelem_homepage = o_header.find('homepage')
            if o_xelem_homepage:
                self.s_homepage = o_xelem_homepage.text

            if o_header.find('author'):
                self.s_author = o_header.find('author').text
            else:
                self.s_author = 'None'

        # ROMsets information
        #--------------------
        for o_xelem_game in o_xml_root.findall('game'):
            s_game_name = o_xelem_game.attrib['name']
            s_game_description = o_xelem_game.find('description').text

            o_dat_game = RomSet(s_game_name, s_game_description)

            for o_xelem_rom in o_xelem_game.findall('rom'):
                    o_rom = Rom()
                    try:
                        o_rom.s_name = o_xelem_rom.attrib['name']
                    except KeyError:
                        pass

                    # TODO: Not sure about this code. Maybe I should only trust specifically indicated nodumps
                    try:
                        o_rom.i_size = int(o_xelem_rom.attrib['size'])
                    except KeyError:
                        o_rom.b_nodump = True

                    # TODO: Not sure about this code. Maybe I should only trust specifically indicated nodumps
                    try:
                        o_rom.s_crc32 = o_xelem_rom.attrib['crc'].lower()
                    except KeyError:
                        o_rom.b_nodump = True

                    try:
                        o_rom.s_md5 = o_xelem_rom.attrib['md5'].lower()
                    except KeyError:
                        o_rom.s_md5 = None

                    try:
                        o_rom.s_sha1 = o_xelem_rom.attrib['sha1'].lower()
                    except KeyError:
                        o_rom.s_sha1 = None

                    # MAME generated XML (later converted generic format (AFAIK) includes a status field which can
                    # contain "baddump" and "nodump" status information
                    try:
                        s_status = o_xelem_rom.attrib['status'].lower()
                        if s_status == 'baddump':
                            o_rom.b_baddump = True
                        if s_status == 'nodump':
                            o_rom.b_nodump = True
                    except KeyError:
                        pass

                    try:
                        o_rom.s_merge = o_xelem_rom.attrib['merge']
                    except KeyError:
                        pass

                    # Adding the rom object to the list
                    o_dat_game._lo_roms.append(o_rom)

            self.add_romset(o_dat_game)

    def _read_from_xml_mame(self, ps_file):
        """
        Method to import data from a MAME xml which has some differences with respect to a standard format one.

        A sample xml would be something like:

            <mame build="0.238 (mame0238)" debug="no" mameconfig="10">
              <machine name="005" sourcefile="segag80r.cpp" sampleof="005">
                <description>005</description>
                <year>1981</year>
                <manufacturer>Sega</manufacturer>
                <rom name="1346b.cpu-u25" size="2048" crc="8e68533e" sha1="a257c..." region="maincpu" offset="0"/>
                <rom name="5092.prom-u1" size="2048" crc="29e10a81" sha1="c4b4e6..." region="maincpu" offset="800"/>
                <rom name="5093.prom-u2" size="2048" crc="e1edc3df" sha1="4f5935..." region="maincpu" offset="1000"/>
                <rom name="5094.prom-u3" size="2048" crc="995773bb" sha1="98dd82..." region="maincpu" offset="1800"/>
              </machine>
            </mame>

        :param ps_file: Path of the xml file to be imported
        :type ps_file: Str
        :return:
        """

        self.s_type = 'xml'

        o_xml_tree = xml.etree.cElementTree.parse(ps_file)
        o_xml_root = o_xml_tree.getroot()

        # Header information
        #-------------------
        self.s_name = 'MAME'
        self.s_version = o_xml_root.get('build')

        # ROMsets information
        #--------------------
        for o_xmachine in o_xml_root.findall('machine'):
            s_name = o_xmachine.get('name')
            s_desc = o_xmachine.find('description').text

            b_device = False
            try:
                s_device = o_xmachine.get('isdevice')
                if s_device.lower() in ss_TRUE_VALUES:
                    b_device = True
            except AttributeError:
                pass

            o_romset = RomSet(ps_name=s_name, ps_description=s_desc, pb_device=b_device)

            for o_xrom in o_xmachine.findall('rom'):
                o_rom = Rom()
                o_rom.s_name = o_xrom.get('name')
                o_rom.i_size = int(o_xrom.get('size'))

                try:
                    o_rom.s_crc32 = o_xrom.get('crc').lower()
                except AttributeError:
                    o_rom.s_crc32 = None

                try:
                    o_rom.s_md5 = o_xrom.get('md5').lower()
                except AttributeError:
                    o_rom.s_md5 = None

                try:
                    o_rom.s_sha1 = o_xrom.get('sha1').lower()
                except AttributeError:
                    o_rom.s_sha1 = None

                if 'bios' in o_xrom.attrib:
                    o_rom.b_bios = True

                if 'status' in o_xrom.attrib:
                    if o_xrom.get('status').lower() == 'baddump':
                        o_rom.b_baddump = True
                    if o_xrom.get('status').lower() == 'nodump':
                        o_rom.b_nodump = True

                o_romset.add_rom(o_rom)

            self.add_romset(o_romset)

    def _to_clrmamepro(self):
        """
        Function to export the ROMset Container as a ClrMamePro dat file.

        :return: A string.
        :rtype Unicode
        """
        ls_chunks = []

        # Header
        #-------
        s_header = ''
        s_header += 'clrmamepro (\n'
        s_header += '\tname "%s"\n' % self.s_name
        s_header += '\tdescription "%s"\n' % self.s_description
        s_header += '\tversion "%s"\n' % self.s_version
        s_header += '\tcomment "%s"\n' % self.s_comment
        s_header += ')\n\n'
        ls_chunks.append(s_header)

        # ROMset data
        #------------
        for o_romset in self:
            # Output generation
            #------------------
            s_romset = 'game (\n'
            s_romset += '\tname "%s"\n' % o_romset.s_name
            s_romset += '\tdescription "%s"\n' % o_romset.s_desc
            for o_rom in o_romset:
                ls_rom_data = ['name "%s"' % o_rom.s_name]

                i_size = 0
                if o_rom.i_size:
                    i_size = o_rom.i_size
                ls_rom_data.append('size "%s"' % i_size)

                s_crc32 = ''
                if o_rom.s_crc32:
                    s_crc32 = o_rom.s_crc32
                if s_crc32:
                    ls_rom_data.append('crc "%s"' % s_crc32)

                s_md5 = ''
                if o_rom.s_md5:
                    s_md5 = o_rom.s_md5
                if s_md5:
                    ls_rom_data.append('md5 "%s"' % s_md5)

                s_sha1 = ''
                if o_rom.s_sha1:
                    s_sha1 = o_rom.s_sha1
                if s_sha1:
                    ls_rom_data.append('sha1 "%s"' % s_sha1)

                ls_flags = []
                if o_rom.b_baddump:
                    ls_flags.append('baddump')
                if o_rom.b_nodump:
                    ls_flags.append('nodump')
                if ls_flags:
                    ls_rom_data.append('flags "%s"' % ' '.join(ls_flags))

                s_romset += '\trom ( %s )\n' % (' '.join(ls_rom_data))

            s_romset += ')\n\n'
            ls_chunks.append(s_romset)

        return ''.join(ls_chunks)

    def _get_i_baddumps(self):
        i_baddumps = 0
        for o_romset in self:
            if o_romset.b_baddump:
                i_baddumps += 1
        return i_baddumps

    def _get_i_devices(self):
        i_devices = 0
        for o_romset in self:
            if o_romset.b_device:
                i_devices += 1
        return i_devices

    def _get_i_nodumps(self):
        i_nodumps = 0
        for o_romset in self:
            if o_romset.b_nodump:
                i_nodumps += 1
        return i_nodumps

    def _get_i_romsets(self):
        return len(self._do_romsets)

    @staticmethod
    def _identify_xml_format(ps_file):
        """
        Method to identify the format of a .xml dat file. So far I've identified two formats: MAME and generic xml used
        by No-Intro (and maybe others).

        :param ps_file:
        :type ps_file: Unicode

        :return: The format of the xml file
        :rtype Unicode
        """
        with codecs.open(ps_file, 'r', 'utf8') as o_file:
            s_data = o_file.read(size=8192)

        s_type = 'generic'
        if '<!DOCTYPE mame' in s_data:
            s_type = 'mame'

        return s_type

    i_baddumps = property(fget=_get_i_baddumps, fset=None)
    i_nodumps = property(fget=_get_i_nodumps, fset=None)
    i_romsets = property(fget=_get_i_romsets, fset=None)
    i_devices = property(fget=_get_i_devices, fset=None)


class RomSet(object):
    """
    Class to store information about a RomSet.

    :ivar ._lo_roms = List[Rom]
    """
    def __init__(self, ps_name, ps_description, pb_device=False):
        """

        :param ps_name:
        :type ps_name: Str

        :param ps_description:
        :type ps_description: Str

        :param pb_device:
        :type pb_device: Bool
        """
        # Properties: Basic ones
        self.s_name = ps_name         # Usually, the file name for the game. MAME uses a short 8 char or fewer name here.
        self.s_desc = ps_description  # Usually, the full and long name of the game i.e. 'Super Mario World (Europe)'.
        self.b_device = pb_device     # MAME .dat includes ROMsets for devices (which some times don't contain any ROM).
                                      # An example of this are DACs (digital to analog converters) which are emulated
                                      # using pure code (so no ROMs involved) and are incorporated or referenced by
                                      # some videogames.

        # Properties: The rest
        self._lo_roms = []            # Somehow, ROMsets *CAN* have "duplicated" ROMs with the same name, so a list.
        self.s_auth = ''              # Author, company that programmed the game (MAME dat support only, AFAIK).

    def __iter__(self):
        """
        :return:
        :rtype Iterator[Rom]
        """
        return iter(self._lo_roms)

    def __str__(self):
        s_output = ''
        s_output += '<RomSet>\n'
        s_output += '  .b_baddump: %s\n' % self.b_baddump
        s_output += '  .b_device:  %s\n' % self.b_device
        s_output += '  .b_nodump:  %s\n' % self.b_nodump
        s_output += '  .i_croms:   %s\n' % self.i_croms
        s_output += '  .i_csize:   %s\n' % self.i_csize
        s_output += '  .i_droms:   %s\n' % self.i_droms
        s_output += '  .i_dsize:   %s\n' % self.i_dsize
        s_output += '  .s_ccrc32:  %s\n' % self.s_ccrc32
        s_output += '  .s_cmd5:    %s\n' % self.s_cmd5
        s_output += '  .s_csha1:   %s\n' % self.s_csha1
        s_output += '  .s_dcrc32:  %s\n' % self.s_dcrc32
        s_output += '  .s_desc:    %s\n' % self.s_desc
        s_output += '  .s_dmd5:    %s\n' % self.s_dmd5
        s_output += '  .s_dsha1:   %s\n' % self.s_dsha1
        s_output += '  .s_auth:    %s\n' % self.s_auth
        s_output += '  .s_name:    %s\n' % self.s_name
        s_output += '  ._lo_roms:\n'

        for i_rom, o_rom in enumerate(self):
            s_rom_text = str(o_rom)

            # Modification of s_rom_text to show the rom number
            s_rom_text = s_rom_text.replace('<Rom>', '<Rom> #%i' % (i_rom + 1))

            ls_rom_raw_lines = s_rom_text.splitlines()
            ls_rom_clean_lines = []

            for s_line in ls_rom_raw_lines:
                s_extra_spaces = ' ' * 13
                ls_rom_clean_lines.append('%s%s' % (s_extra_spaces, s_line))

            s_output += '%s\n\n' % ('\n'.join(ls_rom_clean_lines))

        return s_output

    def add_rom(self, po_rom):
        """
        Method to add a ROM

        :param po_rom:
        :type po_rom: Rom

        :return: Nothing
        """
        self._lo_roms.append(po_rom)

    def _get_so_relevant_roms(self, pb_clean=False):
        """
        Auxiliary method to build a set of relevant ROMs form a ROMset. Depending on whether we want all ROMs or just
        clean ROMs (no bad-dumps, no bios, no .cue files...), the set will be different. This method will be called by
        any other method that requires working with all ROMs or just "clean" ROMs.

        :param pb_clean:
        :type pb_clean: Bool

        :return:
        :rtype Set[Rom]
        """
        # The first step is to create a list with the desired ROMs
        #---------------------------------------------------------
        # This set will be used to identify whether a ROM already has been already taken into account. For the clean
        # hash, we only take duplicated ROMs into account once. Yes, it's possible that some games contain the same ROM
        # twice.
        ss_relevant_roms = set()
        lo_relevant_roms = []

        for o_rom in self._lo_roms:
            # By default, every ROM will be taken into account...
            b_include = True
            s_rom_ext = o_rom.s_name.rpartition('.')[2].lower()
            # o_rom_fp = files.FilePath(o_rom.s_name)

            # ...unless we're in "clean mode" where we'll discard ROMs for different reasons
            if pb_clean:
                # ...for having an unwanted extension (like .cue)
                #if o_rom_fp.has_exts(*_ts_IGNORE_EXTS):
                if s_rom_ext in _ts_IGNORE_EXTS:
                    b_include = False

                # ...to be actually a bios ROM.
                if o_rom.b_bios:
                    b_include = False

                # ...to be already taken into account (there are MAME boards with duplicated chips => duplicated
                # ROM files)
                if o_rom.s_name in ss_relevant_roms:
                    b_include = False

            # Finally, we store the ROMs that passed the checks
            if b_include:
                ss_relevant_roms.update((o_rom.s_name,))
                lo_relevant_roms.append(o_rom)

        return set(lo_relevant_roms)

    def _get_s_hash(self, ps_type='crc32', pb_clean=False):
        """
        Method to obtain the COMPOUND hash of the game. It means the hash of *all* the ROMs included in the game will be
        summed. For example, if the game contains two ROMs:

            - RomSet A
                - ROM a1: CRC32 = 01020304
                - ROM a2: CRC32 = 0a0b0c0d

        The output of this function will be 01020304 + 0a0b0c0d (remember that hash values are hex representations of
        numbers).

        Two comments about the behavior of the function:

            1. Different hashing methods are used: crc32, md5, sha1

            #TODO: Explain pb_clean parameter

            2. Only *relevant* ROMs are considered. For example, meta-data information is typically included in the form
               of .cue files for optical disc images. That information is not really included in the original media and
               its content would modify the hash result of the real data. Imagine two .cue files containing:

                   Track 1: Street Fighter.bin

                   Track 1: Street fighter.bin

               Although the content of the .bin file is the same, the .cue files are different (notice the
               capital-lowercase initial of "fighter"). In consequence, the hash of the .cue file is different and the
               global hash of the whole game will be different. SO, TO AVOID THIS ISSUE, .CUE FILES AND OTHER META-DATA
               FILES ARE NOT CONSIDERED WHEN CALCULATING THE HASH OF THE GAME.

        :return: A keyed dictionary with 'crc32', 'md5', and 'sha1' hashes in hex-string format
        :rtype: Dict[Str:Str]
        """

        so_relevant_roms = self._get_so_relevant_roms(pb_clean=pb_clean)

        # Calculation ROMset "compound" hash (which is the sum of all the relevant ROMs hashes
        #-------------------------------------------------------------------------------------
        ls_hexs = []
        for o_rom in so_relevant_roms:
            if ps_type == 'crc32':
                ls_hexs.append(o_rom.s_crc32)
            elif ps_type == 'md5':
                ls_hexs.append(o_rom.s_md5)
            elif ps_type == 'sha1':
                ls_hexs.append(o_rom.s_sha1)
            else:
                raise Exception('Invalid hash type "%s"' % ps_type)

        s_hash = _compound_hash(ls_hexs)

        # Setting the proper length for each type of hash: crc32 = 8 chars, md5 = 32 chars, sha1 = 40 chars
        #--------------------------------------------------------------------------------------------------
        if s_hash:
            i_hash_length = 0
            if ps_type == 'crc32':
                i_hash_length = 8
            elif ps_type == 'md5':
                i_hash_length = 32
            elif ps_type == 'sha1':
                i_hash_length = 40

            s_hash = s_hash[-i_hash_length:]
            s_hash = s_hash.rjust(i_hash_length, '0')

        else:
            pass

        return s_hash

    def _get_i_size(self, pb_clean=False):
        """
        Method to get the size of a ROMset taking into account all the files (dirty mode) or just relevant files (clean
        mode).

        :param pb_clean: True for clean mode, False for dirty mode
        :type pb_clean Bool
        """
        so_relevant_roms = self._get_so_relevant_roms(pb_clean=pb_clean)

        # Then we can compute the total size of the ROMs
        #-----------------------------------------------
        i_global_size = 0
        for o_rom in so_relevant_roms:
            i_global_size += o_rom.i_size

        return i_global_size

    def _get_i_roms(self, pb_clean=False):
        """
        Method to get the number of ROMs in the ROMset taking into account all the files (dirty mode) or just relevant
        files (clean mode).

        :param pb_clean: True for clean mode, False for dirty mode
        :type pb_clean: Bool

        :return The number of ROMs
        :rtype Int
        """
        so_relevant_roms = self._get_so_relevant_roms(pb_clean=pb_clean)
        return len(so_relevant_roms)

    def _get_b_baddump(self):
        """
        Method to indicate if the ROMset contains any bad ROM (either a bad-dump or a no-dump, MAME dat is the only one
        that I know containing this information.

        :return:
        :rtype Bool
        """
        b_baddump = False
        for o_rom in self:
            if o_rom.b_baddump:
                b_baddump = True
                break
        return b_baddump

    def _get_b_nodump(self):
        """
        Method to indicate if the ROMset contains any bad ROM (either a bad-dump or a no-dump, MAME dat is the only one
        that I know containing this information.

        :return:
        :rtype Bool
        """
        b_nodump = False
        for o_rom in self:
            if o_rom.b_nodump:
                b_nodump = True
                break
        return b_nodump

    def _get_ccrc32(self):
        return self._get_s_hash(ps_type='crc32', pb_clean=True)

    def _get_dcrc32(self):
        return self._get_s_hash(ps_type='crc32', pb_clean=False)

    def _get_cmd5(self):
        return self._get_s_hash(ps_type='md5', pb_clean=True)

    def _get_dmd5(self):
        return self._get_s_hash(ps_type='md5', pb_clean=False)

    def _get_s_csha1(self):
        """
        :return: The clean SHA-1 of the ROMset.
        :rtype Unicode
        """
        return self._get_s_hash(ps_type='sha1', pb_clean=True)

    def _get_s_dsha1(self):
        """
        :return The dirty SHA-1 of the ROMset.
        :rtype Unicode
        """
        return self._get_s_hash(ps_type='sha1', pb_clean=False)

    def _get_i_csize(self):
        return self._get_i_size(pb_clean=True)

    def _get_i_dsize(self):
        return self._get_i_size(pb_clean=False)

    def _get_i_croms(self):
        return self._get_i_roms(pb_clean=True)

    def _get_i_droms(self):
        return self._get_i_roms(pb_clean=False)

    b_baddump = property(fget=_get_b_baddump, fset=None)
    b_nodump = property(fget=_get_b_nodump, fset=None)
    s_ccrc32 = property(fget=_get_ccrc32, fset=None)
    s_dcrc32 = property(fget=_get_dcrc32, fset=None)
    s_cmd5 = property(fget=_get_cmd5, fset=None)
    s_dmd5 = property(fget=_get_dmd5, fset=None)
    s_csha1 = property(fget=_get_s_csha1, fset=None)
    s_dsha1 = property(fget=_get_s_dsha1, fset=None)
    i_csize = property(fget=_get_i_csize, fset=None)
    i_dsize = property(fget=_get_i_dsize, fset=None)
    i_croms = property(fget=_get_i_croms, fset=None)
    i_droms = property(fget=_get_i_droms, fset=None)


class Rom:
    """
    Class to store all the information for a ROM file contained in a DAT file. Typically, that information is the name
    of the ROM, the description, CRC-MD5-SHA1 check-sums...

    NOTE ABOUT self.b_bios: In each "game", mame .xml includes all the files (ROMs) that are part of the bios of the
    system running the game. I think that's a terrible approach because they include the same file over and over as many
    times as games running on the system. Imagine the case of Neo-Geo with dozens (hundreds) of games and the multiple
    versions of the BIOs... I've found, for example, that the archive "uni-bios_1_2o.rom", part of the unibios appears
    280! times in MAME v238 .xml, INSANE! Well, anyway, after the long introduction: the idea behind including whether a
    file belongs to the bios is being to filter them when getting the clean CRC32 of a ROMset.

    :ivar b_bios Bool
    """

    def __init__(self):
        self.b_baddump = False  # Whether it's a bad-dump. So far, MAME is the only one to indicate it.
        self.b_nodump = False   # Whether it's a no-dump. So far, MAME is the only dats that cover this information.
        self.b_bios = False     # Whether it's actually part of the bios. So far, MAME is the only one to indicate it.
        self.s_name = ''        # name of the ROM. i.e. 'Super Mario World.sfc'
        self.s_crc32 = ''       # crc32 checksum of the file data i.e. 'a209fe80'
        self.s_md5 = ''         # md5 checksum of the file data
        self.s_sha1 = ''        # sha1 checksum of the file data
        self.i_size = 0         # file size in bytes
        self.s_merge = ''       # In some formats, a ROM file is used in different ROMsets and the .dat file adds extra
                                # information under "merge" field. Not sure how it's exactly used to locate the ROM
                                # since so far I've always seen the value of "merge" field is exactly the name of the
                                # ROM file.

    def __str__(self):
        s_out = '<Rom>\n'
        s_out += '  .b_baddump: %s\n' % self.b_baddump
        s_out += '  .b_nodump:  %s\n' % self.b_nodump
        s_out += '  .b_bios:    %s\n' % self.b_bios
        s_out += '  .i_size:    %i\n' % self.i_size
        s_out += '  .s_crc32:   %s\n' % self.s_crc32
        s_out += '  .s_md5:     %s\n' % self.s_md5
        s_out += '  .s_name:    %s\n' % self.s_name
        s_out += '  .s_merge:   %s\n' % self.s_merge
        s_out += '  .s_sha1:    %s\n' % self.s_sha1
        return s_out


class CatVer:
    """
    Class to store the Category and Version information stored in catver.ini files for Mame. The category is the genre
    of each of the ROMsets of MAME, while the version is the version number where a particular ROMset was included into
    MAME.

    :ivar _do_entries: Dict[Unicode:_CatVerEntry]
    """
    def __init__(self, ps_file=''):
        self.s_version = ''    # Version of the catver.ini
        self.s_date = ''       # Date of the catver.ini
        self.s_mame = ''       # MAME version for the catver.ini (typically the same as the version of catver.ini)
        self._do_entries = {}  # Dictionary with all CatVer entries. Key is ROMset name.

        if ps_file:
            self.read_from_file(ps_file)

    def __iter__(self):
        """

        :return:
        :rtype Iterator[_CatVerEntry]
        """
        return iter(self._do_entries.values())

    def __str__(self):
        s_out = '<CatVer>\n'
        s_out += '  .s_version: %s\n' % self.s_version
        s_out += '  .s_date:    %s\n' % self.s_date
        s_out += '  .s_mame:    %s\n' % self.s_mame
        s_out += '  .i_entries: %s\n' % self.i_entries
        return s_out

    def get_entry(self, ps_rom):
        """
        Method to get the entry for a given ROMset name.

        :param ps_rom:
        :type ps_rom: Unicode

        :return:
        :rtype _CatVerEntry
        """
        return self._do_entries[ps_rom]

    def read_from_file(self, ps_file):
        """
        Method to populate the object from a catver.ini file.

        :param ps_file:
        :type ps_file: Unicode

        :return: Nothing, the object will be populated in place.
        """

        # Reading the heading information
        #--------------------------------
        with codecs.open(ps_file, 'r', 'utf8') as o_file:
            s_heading = o_file.read(8192)

        for s_line in s_heading.splitlines():
            if s_line.startswith(';;'):
                s_line = s_line.strip(';')
                s_line = s_line.strip()
                ls_chunks = s_line.split('/')
                self.s_version = ls_chunks[0].strip()
                self.s_date = ls_chunks[1].strip()
                self.s_mame = ls_chunks[2].strip()

        # Reading the ROMsets information
        #--------------------------------
        with codecs.open(ps_file, 'r', 'utf8') as o_file:
            # We need to skip the first lines because they don't follow the ini standard
            ls_data = o_file.readlines()[8:]
            o_ini = configparser.ConfigParser()
            o_ini.read_string(''.join(ls_data))

            # Reading the categories
            for s_romset in o_ini.options('Category'):
                s_categories = o_ini.get('Category', s_romset).lower()
                s_cat_main, _, s_cat_second = s_categories.partition('/')
                s_cat_main = s_cat_main.strip()
                s_cat_second = s_cat_second.strip()

                if s_romset not in self._do_entries:
                    o_entry = _CatVerEntry(ps_romset=s_romset)
                    self._do_entries[s_romset] = o_entry

                self._do_entries[s_romset].s_cat_1st = s_cat_main
                self._do_entries[s_romset].s_cat_2nd = s_cat_second

            # Reading the MAME version when the ROMset was introduced
            for s_romset in o_ini.options('VerAdded'):
                s_version = o_ini.get('VerAdded', s_romset)
                # At this point, the CatVerEntry should already exist, but I'll check it, just in case so the code is
                # more robust.
                if s_romset not in self._do_entries:
                    o_entry = _CatVerEntry(ps_romset=s_romset)
                    self._do_entries[s_romset] = o_entry

                self._do_entries[s_romset].s_version = s_version

    def _get_i_entries(self):
        return len(self._do_entries)

    i_entries = property(fget=_get_i_entries, fset=None)


class _CatVerEntry:
    """
    Class to store information about each of the catver.ini file entries.
    """
    def __init__(self, ps_romset='', ps_cat_1st='', ps_cat_2nd='', ps_version=''):
        self.s_romset = ps_romset    # ROMset name.
        self.s_version = ps_version  # MAME version when the ROMset was first introduced.
        self.s_cat_1st = ps_cat_1st  # Main category of the ROMset.
        self.s_cat_2nd = ps_cat_2nd  # Secondary category of the ROMset.

    def __str__(self):
        s_out = '<_CatVerEntry>\n'
        s_out += '  .s_romset:  %s\n' % self.s_romset
        s_out += '  .s_version: %s\n' % self.s_version
        s_out += '  .s_cat_1st: %s\n' % self.s_cat_1st
        s_out += '  .s_cat_2nd: %s' % self.s_cat_2nd
        return s_out

    def has_category(self, *pxs_category):
        """
        Method to check whether a CatVerEntry has certain category. Category matching is NOT case sensitive.

        :param pxs_category: "list" of categories to be checked.
        :type pxs_category: Union[Tuple[Str], List[Str], Set[Str]]

        :return: True if the entry has any of the categories, False otherwise.
        :rtype Bool
        """
        # First we remove unwanted spaces, lowercase and convert to a set the input categories
        ss_inputs = set()
        for s_elem in pxs_category:
            ss_inputs.add(s_elem.strip().lower())

        b_match = False
        for s_cat in ss_inputs:
            if s_cat in (self.s_cat_1st, self.s_cat_2nd):
                b_match = True
                break

        return b_match


# Functions
#=======================================================================================================================
# TODO: This function doesn't belong in here. It should be in another library called rom_tools or something like that.
def get_rom_header(ps_rom_file):
    """
    Function to return the year(s) found in a rom file.

    Only the first bytes of the ROM are scanned and only years 19xx and 20xx are searched for.

    :param ps_rom_file: Name of the file to search in.
    :type ps_rom_file: Str

    :return: A list with the found years as integers.
    :rtype: List[Int]
    """

    i_bytes = 2048
    i_min_year = 1970
    i_max_year = 2020

    li_years = []
    li_years_clean = []

    o_file = open(ps_rom_file, mode='rb')
    s_data_chunk = o_file.read(i_bytes)
    o_file.close()

    o_match = re.search(r'(\d{4})', s_data_chunk)

    if o_match:
        for s_year in o_match.groups():
            li_years.append(int(s_year))

    for i_year in li_years:
        if i_min_year <= i_year <= i_max_year:
            li_years_clean.append(i_year)

    return li_years_clean


# Helper Functions
#=======================================================================================================================
def _dat_vertical_parse(ls_lines, s_section, s_mode='single'):
    """Function to parse a group of lines which contains different information about the same item.

    So, the information follows a pattern similar to:

        field_1 data_a
        field_1 data_b
        field_2 data_c
        ...

        ls_lines: a list containing the individual lines as strings.

        s_section: name of the section (in the above example s_section = field_1, for example).

        s_mode: 'single', each field exists once and the function returns its data as a string.
                'multi', each field exists several times and the function returns its data as a list of strings.

        @rtype : string or list of strings
    """

    ls_data = []
    s_data = ''

    # Adding a space to the section because it has to exist a space between the section and the data.
    s_section += ' '

    for s_line in ls_lines:
        s_line = s_line.strip()

        if s_line.find(s_section) == 0:
            i_start_pos = len(s_section)
            s_data = s_line[i_start_pos:]
            s_data = s_data.strip()
            s_data = s_data.strip('"')
            ls_data.append(s_data)

    if s_mode == 'single':
        x_output = s_data
    elif s_mode == 'multi':
        x_output = ls_data
    else:
        raise Exception('Error: %s mode for _dat_vertical_parse() NOT known.' % s_mode)

    return x_output


def _dat_horizontal_parse(s_line, s_start, s_end):
    """
    Function to parse a SINGLE line containing information about a particular item.

    So, the information follows a pattern similar to:

        a_start DATA_A a_end b_start DATA_B b_end...

    :param s_line: string containing the line to be parsed.

    :param s_start: leading string for data. In the above example: "a_start", "b_start"...

    :param s_end: ending string for data. In the above example: "a_end", "b_end"...

    Comment: Typically, all the items inside the line are unique, so there is no need to 'multi' parameter like in
    _dat_vertical_parse() function.

        @rtype: string

    """

    s_output = ''

    if s_line.find(s_start) != -1:
        i_start_pos = s_line.find(s_start) + len(s_start)
        i_end_pos = s_line.find(s_end, i_start_pos)

        if i_end_pos != -1:
            s_output = s_line[i_start_pos:i_end_pos]

    # It shouldn't appear extra spaces around the real data but just in case...
    s_output = s_output.strip()
    s_output = s_output.strip('"')
    s_output = s_output.strip()

    return s_output


def _hex_add(ps_hex_a, ps_hex_b):
    """
    Function to add two hex digits
    :param ps_hex_a:
    :param ps_hex_b:
    :return:
    """

    s_hex_a = str(ps_hex_a)
    s_hex_b = str(ps_hex_b)

    # Padding the strings, so they are LONGEST + 1 (the +1 is to keep the carryover)
    i_length = max(len(s_hex_a), len(s_hex_b)) + 1

    s_hex_a = s_hex_a.rjust(i_length, '0')
    s_hex_b = s_hex_b.rjust(i_length, '0')

    # We start the addition process
    #------------------------------
    s_hex_result = ''

    i_carry_over = 0

    for s_digit_a, s_digit_b in zip(s_hex_a[::-1], s_hex_b[::-1]):
        i_digit_c = int(s_digit_a, 16) + int(s_digit_b, 16) + i_carry_over
        s_digits_c = hex(i_digit_c).partition('x')[2]

        if len(s_digits_c) == 2:
            i_carry_over = int(s_digits_c[0])
            s_hex_result += s_digits_c[1]
        else:
            i_carry_over = 0
            s_hex_result += s_digits_c[0]

    s_hex_result = s_hex_result[::-1].lstrip('0')

    return s_hex_result


def _compound_hash(pls_hexs):
    """
    Function to return the compound hex of a list of hexs
    :param pls_hexs:
    :return:
    """
    if None not in pls_hexs:
        s_result = '0'
        for s_hex in pls_hexs:
            s_result = _hex_add(s_result, s_hex)
    else:
        s_result = None

    return s_result


def _split_string_to_set(ps_string, ps_split, pb_lowercase=False):
    """
    Function to split and clean list (removing unwanted spaces around the words.

    :param ps_string:
    :param ps_split:
    :return:
    """
    ls_words = ps_string.split(ps_split)

    ls_clean_words = []
    for s_word in ls_words:
        s_word = s_word.strip()
        if pb_lowercase:
            s_word = s_word.lower()
        ls_clean_words.append(s_word)

    return set(ls_clean_words)
