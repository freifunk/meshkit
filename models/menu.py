#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEVELOPMENT_MENU = False
if config.mode == 'development':
    DEVELOPMENT_MENU = True

response.menu = [
    (T('Index'), False, URL('default', 'index')),
    (T('About'), False, URL('default', 'about')),
    (T('Status'), False, URL('default', 'status')),
]
