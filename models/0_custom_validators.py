# coding: utf8
import re

class IS_IPV4CIDR(object):
    """
    Checks if field's value is an IPv4 host/network in CIDR notation.

    Arguments:
        none

    Examples::

        #Check for valid IPv4 host/network in CIDr notation:
        INPUT(_type='text', _name='name', requires=IS_IPV4CIDR())

    >>> IS_IPV4CIDR()('1.2.3.4/32')
    ('1.2.3.4/32', None)
    >>> IS_IPV4CIDR()('1.2.3.4 ')
    ('1.2.3.4', 'enter valid IPv4 address/network in CIDR Notation')
    >>> IS_IPV4CIDR()('1.2.3.256/32 ')
    ('1.2.3.256/32', 'enter valid IPv4 address/network in CIDR Notation')

    """
    regex = re.compile(
        '^(([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])(/(3[012]|[12]?[0-9]))$')
    
    def __init__(self, error_message='enter valid IPv4 address/network in CIDR Notation'):
        self.error_message = error_message

    def __call__(self, value):
        if self.regex.match(value):
            return (value, None)
        else:
            return (value, self.error_message)
            
class IS_IPV6CIDR(object):
    """
    Checks if field's value is an IPv6 host/network in CIDR notation.

    Arguments:
        none

    Examples::

        #Check for valid IPv6 host/network in CIDR notation:
        INPUT(_type='text', _name='name', requires=IS_IPV6CIDR())

    >>> IS_IPV6CIDR()('2000::1/128')
    ('2000::1/128', None)
    >>> IS_IPV6CIDR()('2000:1')
    ('2000:1', 'enter valid IPv6 address/network in CIDR Notation')
    >>> IS_IPV4CIDR()('xyz::1/128')
    ('xyz::/128', 'enter valid IPv6 address/network in CIDR Notation')

    """
    regex = re.compile(
        '^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*(\/(\d|\d\d|1[0-1]\d|12[0-8]))$'
    )
    
    def __init__(self, error_message='enter valid IPv6 address/network in CIDR Notation'):
        self.error_message = error_message

    def __call__(self, value):
        if self.regex.match(value):
            return (value, None)
        else:
            return (value, self.error_message)
