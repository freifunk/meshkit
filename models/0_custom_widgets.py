#!/bin/env python
# -*- coding: utf-8 -*-

def password_md5crypt(field, value):
    id = "%s_%s" % (field._tablename, field.name)
    input_hash = INPUT(_name=field.name,
                    _id=id,
                    _class=field.type + " password-hash",
                    _value=value,
                    data={
                        'error': T("Error calculating the password hash."),
                        'removed': T("Password hash removed."),
                        'placeholder': T("Password"),
                        'placeholder_confirm': T("Confirm Password"),
                        'cancel': T("Cancel"),
                        'edit': T("Edit"),
                        'apply': T("Apply"),
                        'pass_empty': T('No password set. Click button to set a new one.'),
                        'pass_set': T('Password set. Click Button to change it.')
                    },
                    requires=field.requires)
                 
    widget = DIV(
                 CAT(
                        input_hash,
                        BUTTON(
                            T("Edit"),
                            _type="button",
                            _class="password-edit-toggle"
                        ),
                    ),
                    _id="%s_container" % id,
                    _class="password-hash-container"
                )
    return widget

