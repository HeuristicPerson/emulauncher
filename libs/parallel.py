"""
Library to handle parallel tasks of the program. In principle, it will be only used to work with the installation of
ROMs.
"""

import threading


# Classes
#=======================================================================================================================
class ParallelTask:
    """
    Class to store the configuration for a parallel thread task to be launched.

    :ivar o_callback: Callable.
    :ivar _lx_args: Tuple
    :ivar _dx_args: Dict
    """
    def __init__(self, po_callback, plx_args=None, pdx_args=None, pb_close_gui=False):
        """
        :param po_callback:
        :type po_callback: Callable

        :param plx_args: Positional arguments to be passed to the callback function.
        :type plx_args: List

        :param pdx_args: Keyword arguments to be passed to the callback function.
        :type pdx_args: Dict

        :return: Nothing.
        """
        self.o_callback = po_callback   # Callback function to be run by the parallel thread.

        # A status object to capture messages and percent progress of the task (must be updated by the task).
        self._o_status = _TaskStatus()  # Status object to capture progress of the task.

        # TODO: Make po_status argument optional with a default of None, so we can write simpler test cases.

        # Positional arguments
        #---------------------
        # We insert the status object as the first positional argument, so it's mandatory for all the callback functions
        # of a ParallelTask to use the status object.
        if plx_args is None:
            lx_args = []
        else:
            lx_args = plx_args.copy()

        #lx_args.insert(0, self._o_status)
        self._lx_args = lx_args         # Positional arguments to be passed to the parallel function.

        # Keyword arguments
        #------------------
        if pdx_args is None:
            pdx_args = {}

        # Keyword arguments to be passed to the callback function (including an extra one to track progress)
        self._dx_args = pdx_args.copy()
        self._dx_args['po_status'] = self._o_status

        # Thread object that will be populated once the parallel task is started
        self._o_thread = None
        self._b_close_gui = pb_close_gui

    def join(self):
        """
        Method to wait for the ParallelTask to complete.

        :return: Nothing.
        """
        if self._o_thread is not None:
            self._o_thread.join()
        else:
            s_msg = 'ParallelTask not started yet.'
            raise RuntimeError(s_msg)

    def start(self):
        """
        Method to start the parallel task.
        :return:
        """
        if self._o_thread is None:
            self._o_thread = threading.Thread(target=self.o_callback,
                                              args=self._lx_args,
                                              kwargs=self._dx_args)
            self._o_thread.start()

        else:
            s_msg = 'ParallelTask already running or complete, can\'t be launched again'
            raise RuntimeError(s_msg)

        # Todo, find a way of automatically setting self._o_thread = None when the function is finished.

    def _get_b_started(self):
        """
        :return:
        :rtype: Bool
        """
        b_started = False

        if self._o_thread is not None and self._o_thread.is_alive():
            b_started = True

        return b_started

    def _get_b_completed(self):
        b_completed = False
        if self._o_thread:
            b_completed = not self._o_thread.is_alive()

        return b_completed

    def _get_b_close_gui(self):
        return self._b_close_gui

    def _get_s_status(self):
        """
        Method to the text status of the task and return it.

        :return:
        :rtype: Str
        """
        return self._o_status.s_message

    def _get_f_progress(self):
        """
        Method to get the numerical progress of the task.

        :return: The progress of the task. It'll be a number from 0.0 to 1.0
        :rtype: Float
        """
        return self._o_status.f_progress

    b_started = property(fget=_get_b_started, fset=None)
    b_completed = property(fget=_get_b_completed, fset=None)
    s_status = property(fget=_get_s_status, fset=None)
    f_progress = property(fget=_get_f_progress, fset=None)
    b_close_gui = property(fget=_get_b_close_gui, fset=None)


class _TaskStatus:
    """
    Class to store information about the progress of a parallel task.
    """
    def __init__(self):
        self.s_message = ''
        self._f_progress = 0.0

    def __str__(self):
        """
        :return: A text representation of the instance.
        :rtype: Str
        """
        i_id = id(self)
        s_out = f'{i_id}> {self._f_progress:.2f} - {self.s_message}'
        return s_out

    def _get_f_progress(self):
        """
        :return:
        :rtype: Float
        """
        return self._f_progress

    def _set_f_progress(self, pf_value):
        """
        :param pf_value: Numerical value of the task progress. It'll bounded to [0.0, 1.0].
        :type pf_value: Float

        :return: Nothing.
        """
        f_value = pf_value
        f_value = max(f_value, 0.0)
        f_value = min(f_value, 1.0)

        self._f_progress = f_value

    f_progress = property(fget=_get_f_progress, fset=_set_f_progress)
