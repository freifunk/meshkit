import gluon

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
