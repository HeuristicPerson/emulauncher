import unittest
import time

import libs.parallel as parallel


# Test cases
#=======================================================================================================================
class ClassParallelTask(unittest.TestCase):
    def test_has_started_false(self):
        """
        Test to check whether a ParallelTask has been started.
        :return:
        """
        o_task = parallel.ParallelTask(po_callback=_tic_tac)
        b_started = o_task.b_started

        s_msg = 'Just created ParallelTask not marked as not started.'
        self.assertFalse(b_started, s_msg)

    def test_has_started_true(self):
        o_task = parallel.ParallelTask(po_callback=_tic_tac)
        o_task.start()
        b_started = o_task.b_started

        s_msg = 'Just started ParallelTask not marked as started.'
        self.assertTrue(b_started, s_msg)

    def test_has_finished_true(self):
        """
        Method to test a completed paralleltask.

        :return: Nothing.
        """
        o_task = parallel.ParallelTask(po_callback=_report_foo)
        o_task.start()
        time.sleep(2)
        b_completed = o_task.b_completed

        s_msg = 'Task should be completed but it\'s not marked as such.'
        self.assertTrue(b_completed, s_msg)

    def test_has_finished_false(self):
        """
        Method to test a completed paralleltask.

        :return: Nothing.
        """
        o_task = parallel.ParallelTask(po_callback=_tic_tac)
        o_task.start()
        b_completed = o_task.b_completed
        s_msg = 'Task is still running but it\'s not marked as such.'
        self.assertFalse(b_completed, s_msg)

    def test_multi_launching(self):
        """
        Test to avoid multi-launching of the same parallel task definition.
        :return: Nothing
        """
        o_task = parallel.ParallelTask(po_callback=_tic_tac)
        o_task.start()
        self.assertRaises(RuntimeError, o_task.start)

    def test_something(self):
        o_task = parallel.ParallelTask(po_callback=_tic_tac)
        o_task.start()

        for i_iter in range(24):
            print('Task running: %s %s' % (o_task._o_status.s_message, o_task._o_status.f_progress))
            print(o_task._o_thread)
            if not o_task._o_thread.is_alive():
                break
            time.sleep(0.51)

        self.assertEqual(True, False)  # add assertion here

    def test_init_kwargs_not_modified(self):
        """
        Test that the keyword arguments passed to the parallel task are not modified.

        :return: Nothing.
        """
        dx_args = {'foo': 'bar'}
        parallel.ParallelTask(po_callback=_tic_tac, pdx_args=dx_args)
        dx_expect = {'foo': 'bar'}

        self.assertEqual(dx_expect, dx_args)

    def test_status_is_updated(self):
        o_task = parallel.ParallelTask(_tic_tac)
        o_task.start()
        o_task.join()

        dfs_expect = {0.5: '#0 tic, #1 tic, #2 tic, #3 tic, #4 tic'}
        dfs_actual = {o_task.f_progress: o_task.s_status}

        self.assertEqual(dfs_expect, dfs_actual)


# Helper functions
#=======================================================================================================================
def _tic_tac(po_status=None):
    """
    Functions that prints sets a variable to "tic" and "tac" ten times.

    :param po_status: Parallel status object.
    :type po_status: parallel._TaskStatus

    :return: Nothing.
    """
    f_progress = 0.0
    ls_updates = []

    for i_iter in range(5):
        f_progress += 0.1
        s_update = f'#{i_iter} tic'
        ls_updates.append(s_update)

        if po_status is not None:
            po_status.s_message = ', '.join(ls_updates)
            po_status.f_progress = f_progress
            time.sleep(0.5)


def _report_foo(po_status=None):
    """
    Function that prints sets a variable to "tic" and "tac" ten times.

    :param po_status: Parallel status object.
    :type po_status: parallel._TaskStatus

    :return: Nothing.
    """
    if po_status is not None:
        po_status.f_progress = 95.0
        po_status.s_message = 'Finished at 95%'


def _say_hi_name(ps_name, po_status=None):
    with open('/tmp/foo.bar', 'a') as o_file:
        for i_iter in range(5):
            s_msg = f'Hello, {ps_name}!'
            o_file.write(f'{s_msg}\n')
            print(s_msg)
            time.sleep(0.5)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
