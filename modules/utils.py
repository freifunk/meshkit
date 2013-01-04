import subprocess
import os
import re

def process_status(process):
    """ Checks output of 'ps -aux' for a string named 'process'
        Can be used to check if a process is still running

        Args:
            process: A regular expression that matches the process
        Returns: Number of processes that match 'process'
    """
    ps = subprocess.Popen("ps aux", shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    m = re.findall(r'.*' + process + '.*\n', output)
    return len(m)

def check_pid(pidpath, pid):
    '''Checks if a process is running and writes a pidfile

    Args:
        pidpath: absolute path to the pidfile
        pid: pid of the process calling this function

    Returns:
        True if the process is running and not stale
        False if the process isn't running
    '''
    running = False
    if os.path.exists(pidpath):
       pidinfile=open(pidpath, 'r').read().strip()
       if os.path.exists('/proc/%s/cmdline' % pidinfile):
           running = True
       else:
           running = False
    if not running and not pid == False:
        fp = open(pidpath, 'w')
        fp.write(str(pid))
        fp.close
    return running

def loadavg():
    '''Returns loadaverage

       Returns: string with current load: "1m, 5m, 15m"
    '''

    load = os.getloadavg()
    return str(load[0]) + ", " + str(load[1]) + ", " + str(load[2])
 
def memory_stats():
    """ Returns memory usage on linux
    
        Returns: list containing total, used (free+buffers+cached) and free memory
    """
    ps = subprocess.Popen(['cat', '/proc/meminfo'], stdout=subprocess.PIPE).communicate()[0]
    rows = ps.split('\n')
    sep = re.compile('[\s]+')
    for row in rows:
        if re.search(r"^MemTotal", row):
            total = int(sep.split(row)[1]) / 1024
        if re.search(r"^MemFree", row):
            free = int(sep.split(row)[1])
        if re.search(r"^Buffers", row):
            buffers = int(sep.split(row)[1])
        if re.search(r"^Cached", row):
            cached = int(sep.split(row)[1])

    freetotal = (free + buffers + cached) / 1024
    used = total - freetotal
    
    return (total, used, freetotal)
