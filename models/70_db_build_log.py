#!/usr/bin/env python
# -*- coding: utf-8 -*-

db.define_table(
    'build_log',
    Field(
        'id_build',
        'integer',
        label=T('Build Config ID'),
        comment=T(
            'ID of the config, that started this build.'
        ),
        # requires=IS_IN_DB(db, db.imageconf.id, '%(hostname)s'),
    ),
    Field('community', length=128),
    Field('community', length=128),
    Field('target', length=128),
    Field('profile', length=128),
    Field(
        'start',
        'datetime',
        label=T('Started at'),
        # writable=False,
        # readable=False
    ),
    Field(
        'finished',
        'datetime',
        label=T('Finished at'),
        # writable=False,
        # readable=False
    ),
    Field(
        'status',
        default=1,
        requires=IS_EMPTY_OR(
            IS_IN_SET(
                {
                    '0': T("Finished successfully"),
                    '1': T("Queued"),
                    '2': T("Build failed"),
                    '3': T("System error"),
                    '4': T("Processing"),
                },
                error_message=T(
                    '%(name)s is invalid'
                ) % dict(name=T('Status')),
                zero=None,
            )
        )
    ),
    Field(
        'output',
        type='text',
        label=T('Build Log'),
        length=1048576,
        requires=IS_LENGTH(1048576),
    ),
    Field(
        'settings',
        type='text',
        label=T('Settings (JSON)'),
        length=1048576,
        requires=IS_EMPTY_OR(
            [
                IS_LENGTH(1048576),
                IS_JSON(),
            ]
        )
    ),
    migrate=settings.migrate, fake_migrate=settings.fake_migrate
)
