import subprocess
import os
import re
from datetime import timedelta
from gluon import current


def workers_online():
    """ return the number of connected workers

        Returns:
            integer -- number of connected workers
    """
    db = current.globalenv['db']
    # show only workers, whose last heartbeat was not more than 3 * heartbeat
    # seconds ago.
    expiration = current.request.now - timedelta(
        seconds=current.settings.scheduler['heartbeat'] * 3
    )
    workers = db(
        (db.scheduler_worker.last_heartbeat > expiration) & (
            (db.scheduler_worker.status == "ACTIVE") |
            (db.scheduler_worker.status == "PICK")
        )
    ).select()
    num_worker = len(workers)
    return num_worker


def loadavg():
    ''' Returns loadaverage

        Returns:
            string -- string with current load: "1m, 5m, 15m"
    '''

    load = os.getloadavg()
    return str(load[0]) + ", " + str(load[1]) + ", " + str(load[2])


def memory_stats():
    """ Returns memory usage on linux

        Returns:
            list -- list containing total, used (free+buffers+cached)
                    and free memory
    """
    ps = subprocess.Popen(
        ['cat', '/proc/meminfo'],
        stdout=subprocess.PIPE
    ).communicate()[0]
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
