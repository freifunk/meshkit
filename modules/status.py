#!/usr/bin/env python
# coding: utf8

import os
import subprocess
import re
from datetime import timedelta
from gluon import current


def workers_online():
    """ return the number of connected workers

        Returns:
            integer -- number of connected workers
    """
    db_scheduler = current.globalenv['db_scheduler']
    # show only workers, whose last heartbeat was not more than 3 * heartbeat
    # seconds ago.
    expiration = current.request.now - timedelta(
        seconds=current.settings.scheduler['heartbeat'] * 3
    )
    workers = db_scheduler(
        (db_scheduler.scheduler_worker.last_heartbeat > expiration) & (
            (db_scheduler.scheduler_worker.status == "ACTIVE") |
            (db_scheduler.scheduler_worker.status == "PICK")
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


def community_builds():
    """ Get a dict of communities and how many builds each has done

        Returns:
            dict:   community name as key and a list as value

        The value of each dict entry is a list in the form:
        [ count, title, color ], where only the first one is required

    """
    db = current.globalenv['db']
    community_stats = {}

    count = db.build_log.community.count()
    community_stats_select = db().select(
        db.build_log.community, count, groupby=db.build_log.community
    )

    for row in community_stats_select:
        community_name = row.build_log.community
        community_builds = row._extra['COUNT(build_log.community)']
        if community_name:
            community_stats[community_name] = [community_builds]

    return community_stats


def target_builds():
    """ Get a dict of targets and how many builds were done for each

        Returns:
            dict:   shortened target name as key and a list as value

        The value of each dict entry is a list in the form:
        [ count, title, color ], where only the first one is required

    """
    from meshkit import target_shorten
    db = current.globalenv['db']
    target_stats = {}

    count = db.build_log.target.count()
    target_stats_select = db().select(
        db.build_log.target, count, groupby=db.build_log.target
    )

    for row in target_stats_select:
        target_name = row.build_log.target
        target_builds = row._extra['COUNT(build_log.target)']
        if target_name:
            target_stats[target_shorten(target_name)] = [target_builds]

    return target_stats

def profile_builds():
    """ Get a dict of profiles and how many builds were done for each

        Returns:
            dict:   profile name as key and a list as value

        The value of each dict entry is a list in the form:
        [ count, title, color ], where only the first one is required

    """
    db = current.globalenv['db']
    profile_stats = {}

    count = db.build_log.profile.count()
    profile_stats_select = db().select(
        db.build_log.profile, count, groupby=db.build_log.profile
    )

    for row in profile_stats_select:
        profile_name = row.build_log.profile
        profile_builds = row._extra['COUNT(build_log.profile)']
        if profile_name:
            profile_stats[profile_name] = [profile_builds]

    return profile_stats

