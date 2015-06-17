#!/bin/env python
# -*- coding: utf-8 -*-


def password_md5crypt(field, value):
    """ custom widget that has a hidden input field for a md5crypt hash

        It uses some javascript magic to add input and validation fields to the
        form and md5crypts a password on the client side, which is the written
        to the hidden input field.

        Args:
            value (string): submitted form value
            field (object): w2p field object

        Returns:
            object: custom string input widget with password hashing function

    """

    id = "%s_%s" % (field._tablename, field.name)
    input_hash = INPUT(
        _name=field.name,
        _id=id,
        _class=field.type + " password-hash form-control",
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
        requires=field.requires
    )

    widget = DIV(
        CAT(
            input_hash,
            BUTTON(
                _type="button",
                _class="password-edit-toggle"
            ),
        ),
        _id="%s_container" % id,
        _class="password-hash-container"
    )
    return widget


def select_webif_options(field, value):
    """ widget to create a select box for GUI selection

        For every available GUI (configured in db.gui), a data-packages
        attribute is added to the option tag. This is used to dynamically
        change the package selection on selecting a web interface (see JS).

        Args:
            value (mixed): submitted form value. Integer or None.
            field (object): w2p field object

        Returns:
            object: custom select widget for selecting the GUI

    """

    select = SQLFORM.widgets.options.widget(field, value)
    for option in select.elements('option'):
        _value = option["_value"]
        if _value:
            row = db.gui(int(_value))
            if row:
                option['_data-packages'] = row.packages or ''
            if not value and row.is_default:
                option['_selected'] = True

    return select


def input_nouislider(field, value, preset='slider-bandwidth'):
    """ widget to create input sliders using noUiSlider

        Args:
            value (integer): submitted form value
            field (object): w2p field object
            preset (string): preset to use for the slider (see JS)

        Returns:
            object: custom integer input widget with range slider
    """

    input = SQLFORM.widgets.integer.widget(field, value)
    input["_class"] = "form-control integer"
    slider = DIV(
        _class="input-slider",
        data={"preset": preset}
    )

    ret = DIV(
        input,
        slider,
    )
    return ret
