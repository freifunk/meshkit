#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon import current
from meshkit import *

hint_directory = " %s" % T('Hint: Must end with a "/".')

db.define_table(
    'config',
    Field(
        'gui',
        'list:reference gui',
        default=range(1, 99),  # hack to enable all available by default
        label=T('Web Interface'),
        comment=T('Available GUIs. Configure them in the db.gui table.'),
        requires=IS_IN_DB(db, db.gui.id, '%(full_name)s', multiple=True),
        widget=SQLFORM.widgets.checkboxes.widget,
    ),
    Field(
        'noconf',
        'boolean',
        default=False,
        label=T('No configuration'),
        comment=T(
            'If this is checked, then there will be no image configuration ' +
            'options and only building images is possible.'
        ),
    ),
    Field(
        'communitysupport',
        'boolean',
        default=True,
        label=T("Community support"),
        comment=T("Enable to support builds for different community profiles.")
    ),
    Field(
        'profiles',
        length=255,
        label=T("Profiles directory"),
        comment=('Directory with community profiles (uci).'),
        requires=IS_EMPTY_OR(
            IS_MATCH(
                '^\/.*\/$',
                error_message=T(
                    '%(name)s is invalid.'
                ) % dict(name=T('Profiles directory')) + hint_directory
            )
        )
    ),
    Field(
        'communityfiles_dir',
        length=255,
        label=T("Community files"),
        comment=T("Directory containing custom files for communities."),
        requires=IS_EMPTY_OR(
            IS_MATCH(
                '^\/.*\/$',
                error_message=T(
                    '%(name)s is invalid.'
                ) % dict(name=T('Community files directory')) + hint_directory
            )
        )
    ),
    Field(
        'buildroots_dir',
        length=255,
        label=T('Buildroots directory'),
        comment=T('Directory containing extracted OpenWrt imagebuilders.'),
        requires=IS_MATCH(
            '^\/.*\/$',
            error_message=T(
                '%(name)s is invalid.'
            ) % dict(name=T('Buildroots directory')) + hint_directory
        )
    ),
    Field(
        'images_output_dir',
        length=255,
        label=T('Images output directory'),
        comment=T('Directory where finished images are saved.'),
        requires=IS_MATCH(
            '^\/.*\/$',
            error_message=T(
                '%(name)s is invalid'
            ) % dict(name=T('Images output directory')) + hint_directory
        )
    ),
    Field(
        'images_web_dir',
        length=255,
        label=T('Images download URL'),
        comment=T('Base-URL from where the images can be downloaded.'),
        requires=IS_URL(
            error_message=T('%(name)s is invalid') %
            dict(name=T('Images download URL'))
        )
    ),
    Field(
        'documentation_url',
        length=255,
        default='http://doc.meshkit.freifunk.net',
        label=T('Documentation URL'),
        comment=T('Link to the documentation'),
        requires=IS_URL(
            error_message=T('%(name)s is invalid') %
            dict(name=T('URL to documentation'))
        )
    ),
    Field(
        'add_defaultpackages',
        label=T('Default Packages'),
        comment=T('Default package set added to all images'),
        default="-community-profiles -nas -ppp -ppp-mod-pppoe -wpad-mini" +
                "freifunk-common uhttpd",
        type='text',
        requires=IS_MATCH(
            '^[a-zA-Z0-9\s-]*$', error_message=T('%(name)s is invalid') %
            dict(name=T('Default packages'))
        )
    ),
    Field(
        'defaulttheme',
        default='luci-theme-freifunk-generic',
        label=T('LuCI Default Theme'),
        comment=T('Default theme for the LuCI Web Interface'),
        requires=IS_MATCH(
            '^[a-zA-Z0-9-]*$', error_message=T('%(name)s is invalid') %
            dict(name=T('Defaulttheme'))
        )
    ),
    Field(
        'keep_images',
        'integer',
        default=72,
        label=T('Keep images'),
        comment=T(
            'Keep generated images for this number of hours. After this " +'
            'time the will be deleted by a cleanup job.'
        )
    ),
    Field(
        'ipv6packages',
        type='text',
        label=T('IPv6 Packages'),
        default='kmod-ipv6 ip6tables -odhcpd -dnsmasq dnsmasq-dhcpv6',
        comment=T('Packages that will be added if IPv6 is enabled.'),
        requires=IS_MATCH(
            '^[a-zA-Z0-9\s-]*$', error_message=T('%(name)s is invalid') %
            dict(name=T('IPv6 packages'))
        )
    ),
    Field(
        'adminmail',
        length=255,
        label=('Administrator Email'),
        comment=T('Email address of the administrator.'),
        requires=IS_EMAIL(
            error_message=T('%(name)s is invalid') %
            dict(name=T('Administrator email'))
        )
    ),
    Field(
        'lanprotos',
        length=255,
        label=T('LAN Protocols'),
        comment=T('Available LAN protocols'),
        default='static, olsr',
        requires=IS_MATCH(
            '^[a-zA-Z0-9,\s]*$', error_message=T('%(name)s is invalid') %
            dict(name=T('LAN Protocols'))
        )
    ),
    Field(
        'wanprotos',
        length=255,
        label=T('WAN Protocols'),
        comment=T('Available WAN protocols'),
        default='dhcp, static, olsr',
        requires=IS_MATCH(
            '^[a-zA-Z0-9,\s]*$', error_message=T('%(name)s is invalid') %
            dict(name=T('WAN Protocols'))
        )
    ),
    Field(
        'expandablehelp',
        'boolean',
        default=True,
        label=T('Expandable help'),
        comment=T(
            'If enabled, helptexts are hidden and will only be shown after ' +
            'a click.'
        ),
    ),
    Field(
        'showexpertmode',
        'boolean',
        default=True,
        label=T('Show expert mode'),
        comment=T(
            'If enabled, there will be an extra checkbox in step 1 to use ' +
            'an expert mode with much more options.'
        )
    ),
    Field(
        'autosubmit',
        'boolean',
        default=False,
        label=T('Auto submit step 1'),
        comment=T('If enabled, step 1 of the form will be auto-submitted.')
    ),
    migrate=settings.migrate, fake_migrate=settings.fake_migrate
)

config = db.config[1]

if config:
    if config.lanprotos:
        config.lanprotos = [x.strip(' ') for x in config.lanprotos.split(',')]
    if config.wanprotos:
        config.wanprotos = [x.strip(' ') for x in config.wanprotos.split(',')]

    # We need to have this check here. else the buildqueue script will fail
    # because it does not know about any session
    if session.target is not None:
        themes = get_luci_themes(config.buildroots_dir, session.target)
    else:
        profiles = ["a"]
        themes = ["a"]

    targets = get_targets(config.buildroots_dir)

    if config.noconf:
        config.communitysupport = False

    if config.communitysupport:
        if config.profiles and os.access(config.profiles, os.R_OK):
            communities = get_communities(config.profiles)
        else:
            communities = []
    else:
        communities = []

# Needs to be there so config can be accessed in modules
current.config = config
