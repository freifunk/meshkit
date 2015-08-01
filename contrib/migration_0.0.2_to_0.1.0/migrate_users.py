#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This scripts can convert the user database from 0.0.2 to 0.1.0

# 1. export old user database as csv (in appadmin)
# 2. change "users_old_csv" (see below) to the location of the csv file
# 3. run script with: python web2py.py -S meshkit -M -R applications/meshkit/contrib/migration_0.0.2_to_0.1.0/migrate_users.py
# 4. check imported data

# NOTE: You should only do this on a EMPTY auth_user database in the new
# installation

import csv
from gluon import current

# EDIT THIS!
users_old_csv = "/tmp/users_old.csv"

db = current.globalenv['db']

with open(users_old_csv) as csvfile:
    cr = csv.DictReader(csvfile)
    i = 0
    for ou in cr:
        ou.pop("auth_user.id")  # drop id

        i = i + 1

        # iterate over all values and fix names / NULL Values
        ou_cleaned = dict()
        for key, value in ou.iteritems():
            new_key = key.replace("auth_user.", '')
            if value == "<NULL>":
                value = None

            if key == 'pubkeys':
                keyslist = []
                k = value.split("ssh-")
                for v in k:
                    if v is not '':
                        keyslist.append("ssh-" + v)
                value = keyslist

            ou_cleaned[new_key] = value

        id = db.auth_user.update_or_insert(
            db.auth_user.username == ou["auth_user.username"],
            **db.auth_user._filter_fields(ou_cleaned)

        )
        # in case the user already exists there is no id from insert
        if not id:
            id = db(
                db.auth_user.username == ou["auth_user.username"]
            ).select().first().id

        # now insert the user defaults
        if not id:
            print(
                "Error: no ID found, skipping the record for %s" %
                ou["auth_user.username"]
            )
            continue

        id_defaults = db.user_defaults.update_or_insert(
            db.user_defaults.id_auth_user == id,
            id_auth_user=id,
            **db.user_defaults._filter_fields(ou_cleaned)
        )

    db.commit()

print("converted %s users" % i)
