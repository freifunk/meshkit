#!/usr/bin/env python
# coding: utf8

from gluon import current


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
