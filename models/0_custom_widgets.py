#!/bin/env python
# -*- coding: utf-8 -*-

def password_md5crypt(field, value):
    id = "%s_%s" % (field._tablename, field.name)
    input_hash = INPUT(_name=field.name,
                 _id=id,
                 _class=field.type,
                 _value=value,
                 _readonly="1",
                data={
                    'error': T("Error calculating the password hash."),
                    'removed': T("Password hash removed."),
                    'placeholder': T("Enter new password")
                },
                 requires=field.requires)
                 
    widget = DIV(
        CAT(
            input_hash,
            BUTTON(
                T("Edit"),
                _type="button",
                _onclick="pass_edit('%s')" % id,
                _class="password-edit-toggle"
            ),
        ),
        _id="%s_container" % id
    )
    return widget

