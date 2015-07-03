#!/usr/bin/env python
# -*- coding: utf-8 -*-

# force https
# request.requires_https()

import custom_layout as custom

db = DAL(settings.database_uri)

# if SQLite is used, then use a seperate db for the scheduler. From the web2py
# manual: "If you use SQLite it's recommended to use a separate db from the one
# used by your app in order to keep the app responsive."

if settings.database_uri.startswith("sqlite://"):
    db_scheduler = DAL('sqlite://scheduler.sqlite')
else:
    db_scheduler = db

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []


# use a custom bootstrap3 form style (SQLFORM)
response.formstyle = custom.formstyle_bootstrap3(3)

response.logo = A(
    IMG(
        _src=URL('static', 'images/logo.png'),
        _alt="Freifunk Logo"
    ),
    _href=URL('index'),
    _class="site-logo"
)
