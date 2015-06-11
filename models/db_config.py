#!/usr/bin/env python
# -*- coding: utf-8 -*-

from meshkit import *
from gluon import current

db.define_table('config',
    Field('mode', label=T('Application Mode'), default='production',
        comment=T('Development mode disables caching and minimizing/merging of assets (js and css files).'),
        requires=IS_IN_SET(
            {
                'production': T('Production'),
                'development': T('Development')
            },
            zero=None,
        )
    ),
    Field('noconf', 'boolean'),
    Field('communitysupport', 'boolean'),
    Field('profiles',
        requires=IS_EMPTY_OR(IS_MATCH('^\/.*\/$', error_message=T('%(name)s is invalid') % dict(name=T('Profiles directory'))))
    ),
    Field('communityfiles_dir',
        requires=IS_EMPTY_OR(IS_MATCH('^\/.*\/$', error_message=T('%(name)s is invalid') % dict(name=T('Community files directory'))))
    ),
    Field('buildroots_dir',
        requires=IS_MATCH('^\/.*\/$', error_message=T('%(name)s is invalid') % dict(name=T('Buildroots directory')))
    ),
    Field('images_output_dir',
        requires=IS_MATCH('^\/.*\/$', error_message=T('%(name)s is invalid') % dict(name=T('Images output directory')))
    ),
    Field('images_web_dir',
        requires=IS_URL(error_message=T('%(name)s is invalid') % dict(name=T('Images web directory')))
    ),
    Field('documentation_url',
        requires=IS_URL(error_message=T('%(name)s is invalid') % dict(name=T('URL to documentation')))
    ),
    Field('add_defaultpackages', type='text', 
        requires=IS_MATCH('^[a-zA-Z0-9\s-]*$', error_message=T('%(name)s is invalid') % dict(name=T('Add_defaultpackages')))
    ),
    Field('keep_images', 'integer'),
    Field('webifs',
        requires=IS_MATCH('^[a-zA-Z0-9,\s]*$', error_message=T('%(name)s is invalid') % dict(name=T('Webinterfaces')))
    ),
    Field('lucipackages', type='text',
        requires=IS_MATCH('^[a-zA-Z0-9\s-]*$', error_message=T('%(name)s is invalid') % dict(name=T('Lucipackages')))
    ),
    Field('defaulttheme',
        requires=IS_MATCH('^[a-zA-Z0-9-]*$', error_message=T('%(name)s is invalid') % dict(name=T('Defaulttheme')))
    ),
    Field('ipv6packages', type='text',
        requires=IS_MATCH('^[a-zA-Z0-9\s-]*$', error_message=T('%(name)s is invalid') % dict(name=T('IPv6Packages')))
    ),
    Field('adminmail',
        requires=IS_EMAIL(error_message=T('%(name)s is invalid') % dict(name=T('Adminmail')))
    ),
    Field('lanprotos',
        requires=IS_MATCH('^[a-zA-Z0-9,\s]*$', error_message=T('%(name)s is invalid') % dict(name=T('Lanprotos')))
    ),
    Field('wanprotos',
        requires=IS_MATCH('^[a-zA-Z0-9,\s]*$', error_message=T('%(name)s is invalid') % dict(name=T('Lanprotos')))
    ),
    Field('expandablehelp', 'boolean'),
    Field('showexpertmode', 'boolean'),
    Field('autosubmit', 'boolean'),
    migrate=settings.migrate, fake_migrate=settings.fake_migrate
)

config = db.config[1]

if config:
    if config.webifs and config.webifs is not None:
        config.webifs = [x.strip(' ') for x in config.webifs.split(',')]
    if config.lanprotos:
        config.lanprotos = [x.strip(' ') for x in config.lanprotos.split(',')]
    if config.wanprotos:
        config.wanprotos = [x.strip(' ') for x in config.wanprotos.split(',')]
        
    # We need to have this check here. else the buildqueue script will fail because it does not know about any session
    if session.target is not None:
        themes = get_luci_themes(config.buildroots_dir, session.target)
    else:
        profiles = [ "a" ]
        themes = [ "a" ]

    targets = get_targets(config.buildroots_dir)

    if config.noconf:
        config.communitysupport == False

    if config.communitysupport == True:
        if config.profiles and os.access(config.profiles, os.R_OK):
            communities = get_communities(config.profiles)
        else:
            communities = []
    else:
        communities = []

    # development/production settings:
    
    if config.mode == 'development':
        # enable reloading of modules when their code was modified
        from gluon.custom_import import track_changes
        track_changes(True)
        settings.migrate = migrate = True
        #fake_migrate=True
        #fake_migrate_all=True
    else:
        response.optimize_css = 'concat,minify'
        response.optimize_js = 'concat,minify'

# Needs to be there so config can be accessed in modules
current.config = config
