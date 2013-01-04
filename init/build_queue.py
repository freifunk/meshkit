import sys
import os
import subprocess
sys.path.append(os.path.join(request.folder, "private", "modules"))
import utils

if utils.check_pid(os.path.join(request.folder, "private", "buildqueue.pid"), False):
    pass
else:
    subprocess.Popen(['python', 'web2py.py', '-S', 'meshkit', '-M', '-N',  '-R', os.path.join(request.folder, 'private', 'build_queue.py')])
