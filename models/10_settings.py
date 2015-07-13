#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ConfigParser
import uuid
from gluon.storage import Storage
from gluon import current

config_file = os.path.join(request.folder, "conf", "meshkit.conf")

# raw config parser and default values
appconfig = ConfigParser.RawConfigParser(
    {
        'mode': 'development',
        'title': 'Meshkit',
        'subtitle': 'Freifunk OpenWrt Imagebuilder',
        'layout': 'Default',
        'database_uri': 'sqlite://storage.sqlite',
        'security_key': None,
        'server': '127.0.0.1',
        'sender': 'noreply@example.com',
        'tls': False,
        'login': None,
    },
)
appconfig.read(config_file)

settings = Storage()
try:
    settings.app_mode = appconfig.get('general', 'mode')
except ConfigParser.NoSectionError:
    raise HTTP(
        500,
        T(
            'No configuration found. Copy conf/meshkit_example.conf to ' +
            'conf.meshkit.conf and edit it.'
        )
    )

# DB Migration is off. See below where it gets enabled in developer mode
settings.migrate = False
settings.fake_migrate = False
settings.fake_migrate_all = False

# default title/subtitle for the page header
response.title = settings.title = appconfig.get('general', 'title')
response.subtitle = settings.subtitle = appconfig.get('general', 'subtitle')


# settings.author = 'soma'
# settings.author_email = 'freifunk@somakoma.de'
# settings.keywords = 'Freifunk,Mesh,Wireless,Wifi,OpenWrt,Imagebuilder'
# settings.description = (
#    'This imagebuilder will build firmware images for Freifunk or similar' +
#    'wireless mesh networks. The firmware images are preconfigured and ' +
#    ' ready to mesh out of the box.'
# )

# layout - currently unused, leave at 'Default'
settings.layout_theme = appconfig.get('general', 'layout')

# database connection
settings.database_uri = appconfig.get('db', 'database_uri')

# security key. If none exists it will be auto-generated
settings.security_key = appconfig.get('general', 'security_key')
if not settings.security_key:
    sec_key = str(uuid.uuid4())
    settings.security_key = sec_key
    tmpconfig = ConfigParser.RawConfigParser()
    tmpconfig.read(config_file)
    tmpconfig.set('general', 'security_key', sec_key)
    with open(config_file, 'w') as cf:
        tmpconfig.write(cf)

# Mail configuration
settings.email_server = appconfig.get('mail', 'server')
settings.email_sender = appconfig.get('mail', 'sender')
settings.email_tls = appconfig.getboolean('mail', 'tls')
settings.email_login = appconfig.get('mail', 'login')

# Login configuration
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []

# default css classes for SQLFORM.grid
settings.ui_grid = dict(
    widget='',
    header='',
    content='',
    default='',
    cornerall='',
    cornertop='',
    cornerbottom='',
    button='btn btn-default',
    buttontext='',
    buttonadd='icon-plus big',
    buttonback='icon-left big',
    buttonexport='icon-down big',
    buttondelete='icon-trash big',
    buttonedit='icon-pencil big',
    buttontable='icon-right big',
    buttonview='icon-eye big'
)

settings.colors = {
    "ff-yellow": "#ffb400",
    "ff-magenta": "#dc0067",
    "ff-blue": "#009ee0",
    "flotcharts-yellow": "#EDC240",
    "flotcharts-blue": "#AFD8F8",
    "flotcharts-red": "#CB4B4B",
}

# scheduler settings
settings.scheduler = dict(
    heartbeat=2,
    timeout=120,
    retry_failed=0
)

if settings.app_mode == "development":
    # reload modules that have changed
    from gluon.custom_import import track_changes
    track_changes(True)
    # enable database migration
    settings.migrate = True
    settings.fake_migrate = False
    settings.fake_migrate_all = False
else:
    # optimize handling of static files
    response.optimize_css = 'concat,minify'
    response.optimize_js = 'concat,minify'

# save settings to current, so we can use it in modules
current.settings = settings

