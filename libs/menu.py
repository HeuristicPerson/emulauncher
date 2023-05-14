class Menu:
    """
    :ivar _s_title: Str
    :ivar _i_active_elem: Union[None, Int]
    :ivar _ls_options: List[Str]
    :ivar _lc_actions: List[Callable]
    :ivar _ldx_args: List[Dict]
    """
    def __init__(self):
        """
        Initialization method for the class.
        """
        self._s_title = ''          # Title of the menu that will appear above it
        self._i_active_elem = None  # Active element of the layer
        self._ls_options = []       # Text of each option
        self._lc_actions = []       # Action (callback?) of each option
        self._ldx_args = []         # Arguments for the callbacks

    def add_option(self, ps_text, pc_callback=None, pdx_args={}):
        """
        Function to add an option to the layer.

        :param ps_text: Test we want to appear in the menu entry.
        :type ps_text: Str

        :param pc_callback:
        :type pc_callback: Callable

        :param pdx_args:
        :type pdx_args: Dict

        :return: Nothing, the object will be modified in place.
        """
        self._ls_options.append(ps_text)
        self._lc_actions.append(pc_callback)
        self._ldx_args.append(pdx_args)

        if self._i_active_elem is None:
            self._i_active_elem = 0

    def nice_format(self):
        """
        Method to generate a string representation of the layer in a nice human-readable format; this is useful just for
        debugging

        :return: A text representation of the layer.
        :rtype: Str
        """
        ls_lines = []

        for i_pos, (s_text, c_callback, dx_args) in enumerate(zip(self._ls_options, self._lc_actions, self._ldx_args)):
            s_intro = '[ ]'
            if i_pos == self._i_active_elem:
                s_intro = '[*]'

            if c_callback is None:
                s_callback = 'None'
            else:
                s_callback = c_callback.__name__

            s_line = f'{s_intro} {s_text} > {s_callback}({dx_args})'
            ls_lines.append(s_line)

        return '\n'.join(ls_lines)

    def activate_next(self):
        """
        Method to activate next item of the layer.
        :return:
        """
        if self.i_elems:
            self._i_active_elem = min(self.i_elems - 1, self.i_active_elem + 1)

    def activate_prev(self):
        """
        Method to activate previous item of the layer.
        """
        if self.i_elems:
            self._i_active_elem = max(0, self.i_active_elem - 1)

    def run_current(self):
        """
        Method to run the callback of the currently selected menu option.
        :return:
        """
        if self._lc_actions[self.i_active_elem] is not None:
            return self._lc_actions[self.i_active_elem](**self._ldx_args[self.i_active_elem])
            
    def _get_i_elems(self):
        """
        Method to return the number of options in the layer object.
        :return:
        :rtype: Int
        """
        return len(self._ls_options)

    def _get_i_active_elem(self):
        """
        Method to get the active element
        :return:
        :rtype: Int
        """
        return self._i_active_elem

    def _get_s_title(self):
        return self._s_title

    def _set_s_title(self, ps_title):
        self._s_title = ps_title

    i_elems = property(fget=_get_i_elems, fset=None)
    i_active_elem = property(fget=_get_i_active_elem, fset=None)
    s_title = property(fget=_get_s_title, fset=_set_s_title)
