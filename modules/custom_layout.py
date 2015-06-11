#!/bin/python
# -*- coding: utf-8 -*-

from gluon import *

def navbar(auth_navbar, user_defaults=False):
    """ create a custom user navbar element (login, register...)
    
        see gluon/tools.py
        
        Args:
            user_defaults: Show user defaults link for logged in users if True
        
    """
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
            
        li_reset_pass = LI(A(current.T("Lost Password?"), _class="icon-mail",
            _href=bar["request_reset_password"], _rel="nofollow"))
    
        dropdown = UL(li_reset_pass,
                      li_register,
                      LI('', _class="divider"),
                      li_login,
                      _class="dropdown-menu user-menu", _role="menu")
        
        return LI(toggle, dropdown, _class="dropdown")
            
    else:
        toggletext = "%s %s" % (bar["prefix"], user)
        toggle = A(toggletext,
                   _href="#",
                   _class="dropdown-toggle",
                   _rel="nofollow",
                   ** {"_data-toggle": "dropdown"})
        li_profile = LI(A(current.T("Account Details"), _class="icon-cog",
                        _href=bar["profile"], _rel="nofollow"))
        
        li_password = LI(A(current.T("Password"), _class="icon-user",
                        _href=bar["change_password"], _rel="nofollow"))
                        
        
        if user_defaults:
            li_defaults = LI(A(current.T("Firmware Defaults"), _class="icon-wrench",
                            _href=URL("user_defaults"), _rel="nofollow"))
        else:
            li_defaults = ''
                        
        li_logout = LI(A(current.T("Log Out"), _class="icon-login",
                       _href=bar["logout"], _rel="nofollow"))
                       
        dropdown = UL(li_defaults,
                      li_profile,
                      li_password,
                      LI('', _class="divider"),
                      li_logout,
                      _class="dropdown-menu", _role="menu")

        return LI(toggle, dropdown, _class="dropdown user-menu")