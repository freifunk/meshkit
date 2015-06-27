#!/usr/bin/env python
# -*- coding: utf-8 -*-

# force https
# request.requires_https()

# custom user login controls in navbar
import custom_layout as custom

if not request.env.web2py_runtime_gae:
    # if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
else:
    # connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    # store sessions and tickets there
    session.connect(request, response, db=db)
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
# (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# form style, 'bootstrap3_inline', 'bootstrap3_stacked', 'bootstrap2' or other
response.formstyle = 'bootstrap3_inline'

response.logo = A(
    IMG(
        _src=URL('static', 'images/logo.png'),
        _alt="Freifunk Logo"
    ),
    _href=URL('index'),
    _class="site-logo"
)
