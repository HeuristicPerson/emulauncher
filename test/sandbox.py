"""
File to do quick and manual python tests when needed.
"""

import os
import shutil
import subprocess

import libs.cons as cons


s_patcher_src = os.path.join(cons.s_SCRIPT_ROOT, 'resources', 'vendoring', 'lppf')
s_patcher_dst = os.path.join('/tmp', 'lppf')

shutil.copyfile(s_patcher_src, s_patcher_dst)
os.chmod(s_patcher_dst, 0o777)

ts_cmd = (s_patcher_dst, )

o_process = subprocess.Popen(ts_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
s_stdout, s_stderr = o_process.communicate()

print(s_stdout)
print(s_stderr)
