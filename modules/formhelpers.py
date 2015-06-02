import gluon
from gluon import *
if hasattr(current, 'T'):
        T = current.T

def errormsg(key, error, custom=None):
    """ This returns a formatted div containing the errormessage if field was invalid

    Args:
      key: the name of the field 
      error: error message from web2py (is None if there was no error)
      custom: Show this custom error message instead of the web2py one (optional)

    Returns:
      A formatted div with the errormessage if there was an error in this field,
      otherwise ''

    """
    if not error:
        return ''
    else:
        if custom:
            return gluon.html.XML('<div id="' + key + '__error" class="error">' + custom + '</div>')
        else:
            return gluon.html.XML('<div id="' + key + '__error" class="error">' + error + '</div>')


def helptext(text, expandable=True):
    """Render a span element which contains the helptext.

    Args:
        text: The helptext which should be displayed
        expandable: False or True. If True additional html is rendered to make
                      the help expandable.
    Returns:
        A web2py html helper (in fact this is like returning html)

    """
    
    config = current.config
    help = ""

    if text:
        if config.expandablehelp is True:
            help = TAG[''](SPAN("?",_class='helpLink'), DIV(text, _class='helptext'))
        else:
            help = DIV(text, _class='helptext')
        
    return XML(help)

class customField:
    """
    Class that outputs form fields

    Args:
        form -- Web2py form object
        tablename -- table name (string) 
    """
    
    def __init__(self, form=None, tablename=None):
        self.form = form
        self.tablename = tablename
     
    def field(self, col, advanced=None, suboption=False):
        """ Create a form field
        
        Args:
            col -- a database column (string)
            advanced -- id of a div with advanced options
            
        """
        id = "%s_%s" % (self.tablename, col)
        label = self.form.custom.label[col]
        widget = self.form.custom.widget[col]
        comment = self.form.custom.comment[col]
        
        advancedToggle = ''
        
        if advanced:
            advancedToggle = SPAN(
                "+/-",
                _title=T("Advanced Options"),
                _class="advanced",
                _onclick="ToggleDiv(\'%s\')" % advanced
            )
        
        fieldset = CAT(
            LABEL (
                label,
                _class="form_label",
                _for=id
            ),
            DIV(
                CAT(
                    widget,
                    helptext(comment),
                    advancedToggle
                ),
                _class="form_value"
            )
        )
        
        if suboption:
            fieldset = DIV (
                fieldset,
                _id=suboption,
                _class="suboptions"
            )
        
        return fieldset

class formfield:
    """
    Class that outputs form fields

    Args:
        name = name of the formfield
        label = label for the formfield
        options = dict of options for the form field
        helptext = the help text to be shown with form fields
        special = Special value to insert into the input tag
    """


    def __init__(self, name=None, label=None, options=None, helptext=None, special='', value='', valuelist={}, valueselected=None, errormsg=None, advanced=None, inputtype=None, valuetext=None):
        self.Name = name
        self.Label = label
        self.Options = options
        self.Helptext = helptext
        self.Special = special
        self.Value = value
        self.Valuelist = valuelist
        self.Valueselected = valueselected
        self.Errormsg = errormsg
        self.Advanced = advanced
        self.Inputtype = inputtype
        self.Valuetext = valuetext

    def chkbox(self):
        if not (self.Name and self.Label):
            return gluon.html.XML('<div class="error">Missing variables, at least specify name and label for a checkbox!</div>')
        label = '<label class="form_label" for="imageconf_' + self.Name + '" id="imageconf_' + self.Name + '__label">' + self.Label + '</label>'
        field =  '<div class="form_value">'
        checked = ''
        if self.Value:
            checked = 'checked="1"'
        field += '<input ' + self.Special + ' class="boolean" id="imageconf_' + self.Name + '" name="' + self.Name + '" type="checkbox" ' + checked + '/>'
        if self.Advanced:
            field += self.Advanced;
        if self.Helptext:
            field += helptext(self.Helptext)
        field += '</div>'
        if self.Errormsg:
            field += errormsg(self.Name, "form.errors." + self.Name, self.Errormsg)
        return gluon.html.XML(label + field)

    def input(self):
        if not (self.Name and self.Label):
            return gluon.html.XML('<div class="error">Missing variables, at least specify name and label for a input field!</div>')
        label = '<label class="form_label" for="imageconf_' + self.Name + '" id="imageconf_' + self.Name + '__label">' + self.Label + '</label>'
        
        field =  '<div class="form_value">'
        
        typevalue = 'text'
        
        if not(self.Inputtype):
            typevalue = 'text'
        else:
            typevalue = self.Inputtype
        
        field += '<input id="imageconf_' + self.Name + '" ' +  self.Special + ' value="' + str(self.Value) + '" name="' + self.Name + '" type="' + typevalue + '">'
        if self.Helptext:
            field += helptext(self.Helptext)
        
        if self.Valuetext:
            field += self.Valuetext
    
        field += '</div>'
        if self.Errormsg:
            field += errormsg(self.Name, "form.errors." + self.Name, self.Errormsg)
        return gluon.html.XML(label + field)

    def select(self):
        if not (self.Name and self.Label):
            return gluon.html.XML('<div class="error">Missing variables, at least specify name and label for a select field!</div>')
        label = '<label class="form_label" for="imageconf_' + self.Name + '" id="imageconf_' + self.Name + '__label">' + self.Label + '</label>'
    
        field =  '<div class="form_value">'
        field += '<select ' + self.Special + ' name="' + self.Name + '" id="imageconf_' + self.Name + '" class="generic-widget">'
        for v in self.Valuelist:
            selected = ""
            if v == self.Valueselected:
                selected = " SELECTED"
            field += '<option value="' + v +'"' + selected + '>' + v + '</option>'
        field += '</select>'
        if self.Helptext:
            field += helptext(self.Helptext)
        if self.Errormsg:
            field += errormsg(self.Name, "form.errors." + self.Name, self.Errormsg)
        field += '</div>'
        return gluon.html.XML(label + field)

    def textarea(self, rows=5):
        if not (self.Name and self.Label):
            return gluon.html.XML('<div class="error">Missing variables, at least specify name and label for a textarea field!</div>')
        label = '<label class="form_label" for="imageconf_' + self.Name + '" id="imageconf_' + self.Name + '__label">' + self.Label + '</label>'
        field =  '<div class="form_value">'
        field += '<textarea ' + self.Special + ' rows="' + str(rows) + '" class="text note" id="imageconf_' + self.Name + '" name="' + self.Name + '" type="text">'
        field += self.Value + '</textarea>'
        if self.Helptext:
            field += helptext(self.Helptext)
        if self.Errormsg:
            field += errormsg(self.Name, "form.errors." + self.Name, self.Errormsg)
        field += '</div>'
        return gluon.html.XML(label + field)
