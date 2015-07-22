#!/bin/python
# -*- coding: utf-8 -*-

from gluon import *
if hasattr(current, 'T'):
        T = current.T


def formstyle_bootstrap3(col_label_size=3):
    """ bootstrap 3 horizontal form layout

    Note:
        Experimental!
    """
    def _inner(form, fields):
        form.add_class('form-horizontal')
        label_col_class = "col-sm-%d" % col_label_size
        col_class = "col-sm-%d" % (12 - col_label_size)
        offset_class = "col-sm-offset-%d" % col_label_size
        parent = CAT()
        for id, label, controls, help in fields:
            # wrappers
            _help = SPAN(help, _class='help-block')
            # embed _help into _controls
            _controls = DIV(controls, _help, _class=col_class)
            if isinstance(controls, INPUT):
                if controls['_type'] == 'submit':
                    controls.add_class('btn btn-primary')
                    _controls = DIV(
                        controls, _class="%s %s" % (col_class, offset_class))
                if controls['_type'] == 'button':
                    controls.add_class('btn btn-default')
                elif controls['_type'] == 'file':
                    controls.add_class('input-file')
                elif controls['_type'] in ('text', 'password'):
                    controls.add_class('form-control')
                elif controls['_type'] == 'checkbox':
                    controls.add_class('form-control checkbox')

                elif isinstance(controls, (SELECT, TEXTAREA)):
                    controls.add_class('form-control')

            elif isinstance(controls, SPAN):
                _controls = P(controls.components,
                              _class="form-control-static %s" % col_class)
            elif isinstance(controls, UL):
                for e in controls.elements("input"):
                    e.add_class('form-control')
            if isinstance(label, LABEL):
                label['_class'] = 'control-label %s' % label_col_class

            parent.append(DIV(label, _controls, _class='form-group', _id=id))
        return parent
    return _inner


def navbar(auth_navbar, user_defaults=False):
    """ create a custom user navbar element (login, register...)

        see gluon/tools.py

        Args:
            user_defaults: Show user defaults link for logged in users if True

    """
    from gluon.tools import Auth
    bar = auth_navbar
    user = bar["user"]

    if not user:
        toggletext = current.T("Log In")
        toggle = A(toggletext,
                   _href="#",
                   _class="dropdown-toggle",
                   _rel="nofollow",
                   ** {"_data-toggle": "dropdown"})

        li_login = LI(A(current.T("Log In"), _class="icon-user",
                        _href=bar["login"], _rel="nofollow"))

        li_register = LI(A(current.T("Sign Up"), _class="icon-user-add",
                           _href=bar["register"], _rel="nofollow"))

        li_reset_pass = LI(A(
            current.T("Lost Password?"),
            _class="icon-mail",
            _href=bar["request_reset_password"],
            _rel="nofollow"
        ))

        auth = Auth(current.globalenv['db'])
        form = auth.login()

        # use https as target for the login form if it is enabled
        if current.settings.https_enabled:
            login_url = URL(
                "user",
                args=["login"],
                scheme="https",
                port=current.settings.https_port
            )
            form.custom.begin = XML(
                str(form.custom.begin).replace("#", login_url)
            )

        field_username = form.custom.widget.username
        field_username.update(_placeholder=T('Username'))
        field_password = form.custom.widget.password
        field_password.update(_placeholder=T('Password'))
        login_submit = form.custom.submit
        login_submit.update(**{"_data-w2p_disable_with": "%s" % T("Working")})

        li_login_form = LI(
            CAT(
                form.custom.begin,
                field_username,
                field_password,
                form.custom.widget.remember_me,
                LABEL(
                    T("Remember me"),
                    _for="auth_user_remember_me"
                ),
                form.custom.submit,
                form.custom.end
            )
        )

        dropdown = UL(
            li_reset_pass,
            li_register,
            LI('', _class="divider"),
            li_login,
            li_login_form,
            _class="dropdown-menu user-menu", _role="menu"
        )

        return LI(toggle, dropdown, _class="dropdown")

    else:
        toggletext = "%s %s" % (bar["prefix"], user)
        toggle = A(toggletext,
                   _href="#",
                   _class="dropdown-toggle",
                   _rel="nofollow",
                   ** {"_data-toggle": "dropdown"})
        li_profile = LI(A(current.T("Account Details"), _class="icon-user",
                        _href=bar["profile"], _rel="nofollow"))

        li_builds = LI(
            A(
                current.T("Your Builds"),
                _class="icon-picture",
                _href=URL("user_builds"),
                _rel="nofollow",
            )
        )

        li_password = LI(A(current.T("Password"), _class="icon-lock",
                           _href=bar["change_password"], _rel="nofollow"))

        if user_defaults:
            li_defaults = LI(
                A(current.T("Firmware Defaults"), _class="icon-wrench",
                  _href=URL("user_defaults"), _rel="nofollow"))
        else:
            li_defaults = ''

        li_logout = LI(A(current.T("Log Out"), _class="icon-login",
                       _href=bar["logout"], _rel="nofollow"))

        dropdown = UL(li_defaults,
                      li_builds,
                      li_profile,
                      li_password,
                      LI('', _class="divider"),
                      li_logout,
                      _class="dropdown-menu", _role="menu")

        return LI(toggle, dropdown, _class="dropdown user-menu")
