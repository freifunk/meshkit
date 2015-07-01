#!/usr/bin/env python
# -*- coding: utf-8 -*-

# force https
# request.requires_https()

# custom user login controls in navbar
import custom_layout as custom

db = DAL('sqlite://storage.sqlite')

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
# (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# form style, 'bootstrap3_inline', 'bootstrap3_stacked', 'bootstrap2' or other
response.formstyle = custom.formstyle_bootstrap3(3)

response.logo = A(
    IMG(
        _src=URL('static', 'images/logo.png'),
        _alt="Freifunk Logo"
    ),
    _href=URL('index'),
    _class="site-logo"
)

