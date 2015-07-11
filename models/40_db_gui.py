#!/usr/bin/env python
# -*- coding: utf-8 -*-

db.define_table(
    'gui',
    Field(
        'short_name',
        label=T('Short internal name'),
        comment=T(
            'A short internal name. Only Alphanumeric characters allowed.'
        ),
        requires=IS_ALPHANUMERIC(
            error_message=T('%(name)s is invalid') %
            dict(name=T('Short internal name'))
        )
    ),
    Field(
        'full_name',
        label=T('Full name'),
        comment=T('Full name of the Webinterface that is shown to users.'),
        requires=IS_MATCH(
            '^[a-zA-Z0-9\s-]*$', error_message=T('%(name)s is invalid') %
            dict(name=T('Full name'))
        )
    ),
    Field(
        'is_default',
        'boolean',
        label=T('Default'),
        comment=T('Use this GUI as the default. Should only be selected once.')
    ),
    Field(
        'packages',
        type='text',
        label=T('Packages'),
        comment=T('Packages to install when this GUI is selected.'),
        requires=IS_MATCH(
            '^[a-zA-Z0-9\s-]*$', error_message=T('%(name)s is invalid') %
            dict(name=T('Packages'))
        )
    ),
)

# populate if there are no entries in the db.gui table
if db(db.gui.id > 0).count() == 0:
    db.gui.insert(
        short_name='none',
        full_name='No web interface',
        is_default=False,
        packages=None
    )
    db.gui.insert(
        short_name='luci',
        full_name='LuCI',
        is_default=True,
        packages='luci-mod-admin-full luci-i18n-base-de luci-app-firewall ' +
                 'luci-i18n-firewall-de luci-app-freifunk-widgets uhttpd ' +
                 'luci-mod-freifunk luci-i18n-freifunk-de ' +
                 'luci-mod-freifunk-community libiwinfo-lua ' +
                 'olsrd-mod-jsoninfo luci-i18n-meshwizard-de ' +
                 'luci-i18n-olsr-de luci-i18n-splash-de uhttpd'
    )
