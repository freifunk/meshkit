from meshkit import *

if not config == None:
    db.define_table('imageconf',
        Field('target',
            requires=IS_IN_SET(targets, error_message=T('%(name)s is invalid') % dict(name=T('Target')))
        ),
        Field('status',
            requires=IS_EMPTY_OR(
                IS_IN_SET([ '0', '1', '2', '3' ], error_message=T('%(name)s is invalid') % dict(name=T('Status')))
            )
        ),
        Field('noconf', 'boolean'),
        Field('mail',
            requires=IS_EMPTY_OR(IS_EMAIL(error_message=T('%(name)s is invalid') % dict(name=T('Email'))))
        ),
        Field('community',
            requires=IS_EMPTY_OR(IS_IN_SET(communities, error_message=T('%(name)s is invalid') % dict(name=T('Community'))))
        ),
        Field('pubkeys',type='text',
            requires=IS_EMPTY_OR([
                    IS_LENGTH(32768,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Pubkeys'), len='32768')),
                    IS_MATCH('[a-zA-Z0-9\/\+,-@\.\=]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Pubkeys')) )
                ])
        ),
        Field('profile',
            requires=IS_EMPTY_OR(IS_MATCH('[a-zA-Z0-9\-]+', error_message=T('%(name)s is invalid') % dict(name=T('Profile'))))
        ),
        Field('webif',
            requires=IS_EMPTY_OR(IS_IN_SET(config.webifs, error_message=T('%(name)s is invalid') % dict(name=T('Webinterface'))))
        ),
        Field('theme',
            requires=IS_EMPTY_OR(IS_IN_SET(themes, error_message=T('%(name)s is invalid') % dict(name=T('Theme'))))
        ),
        Field('ipv6', 'boolean'),
        Field('ipv6_config',
            requires=IS_EMPTY_OR(IS_IN_SET(['static', 'auto-ipv6-random', 'auto-ipv6-fromv4'], error_message=T('%(name)s is invalid') % dict(name=T('Webinterface'))))
        ),
        Field('packages',
            requires=IS_EMPTY_OR(IS_MATCH('[a-zA-Z0-9\-\_\n]+', error_message=T('%(name)s is invalid') % dict(name=T('Packages'))))
        ),
        Field('rand',
            requires=IS_EMPTY_OR([
                IS_ALPHANUMERIC(),
                IS_LENGTH(32)])
        ),
        Field('hostname',
            requires=IS_EMPTY_OR(IS_MATCH('[a-zA-Z0-9][a-zA-Z0-9\.\-]+[a-zA-Z0-9]', error_message=T('%(name)s is invalid') % dict(name=T('Hostname'))))
        ),
        Field('latitude',
            requires=IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(-180, 180, error_message=T('%(name)s is invalid') % dict(name=T('Latitude'))))
        ),
        Field('longitude',
            requires=IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(-180, 180, error_message=T('%(name)s is invalid') % dict(name=T('Longitude'))))
        ),
        Field('upload', 'upload',
            requires=IS_EMPTY_OR(IS_UPLOAD_FILENAME(extension='gz', error_message=T('%(name)s is invalid') % dict(name=T('Upload'))))
        ),
        Field('wifiifsnr', 'integer'),
        Field('wifi0ipv4addr',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='WIFI0 ' + T('IP address'))))
        ),
        Field('wifi0ipv6addr',
            requires=IS_EMPTY_OR(IS_IPV6CIDR(error_message=T('%(name)s is invalid') % dict(name='WIFI0 ' + T('IPv6 address'))))
        ),
        Field('wifi0ipv6ra', 'boolean'),
        Field('wifi0chan',
            requires=IS_EMPTY_OR(IS_INT_IN_RANGE(1, 170, error_message=T('%(name)s is invalid') % dict(name='WIFI0 ' + T('Channel'))))
        ),
        Field('wifi0dhcp','boolean'),
        Field('wifi0vap','boolean'),
        Field('wifi0dhcprange',
            requires=IS_EMPTY_OR(IS_IPV4CIDR(error_message=T('%(name)s is invalid') % dict(name='WIFI0 ' + T('DHCP Range'))))
        ),
        Field('wifi1ipv4addr',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='WIFI1 ' + T('IP address'))))
        ),
        Field('wifi1ipv6addr',
            requires=IS_EMPTY_OR(IS_IPV6CIDR(error_message=T('%(name)s is invalid') % dict(name='WIFI1 ' + T('IPv6 address'))))
        ),
        Field('wifi1ipv6ra', 'boolean'),
        Field('wifi1chan',
            requires=IS_EMPTY_OR(IS_INT_IN_RANGE(1, 170, error_message=T('%(name)s is invalid') % dict(name='WIFI1 ' + T('Channel'))))
        ),
        Field('wifi1dhcp','boolean'),
        Field('wifi1vap','boolean'),
        Field('wifi1dhcprange',
            requires=IS_EMPTY_OR(IS_IPV4CIDR(error_message=T('%(name)s is invalid') % dict(name='WIFI1 ' + T('DHCP Range'))))
        ),
        Field('wifi2ipv4addr',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='WIFI2 ' + T('IP address'))))
        ),
        Field('wifi2ipv6addr',
            requires=IS_EMPTY_OR(IS_IPV6CIDR(error_message=T('%(name)s is invalid') % dict(name='WIFI2 ' + T('IPv6 address'))))
        ),
        Field('wifi2ipv6ra', 'boolean'),
        Field('wifi2chan',
            requires=IS_EMPTY_OR(IS_INT_IN_RANGE(1, 170, error_message=T('%(name)s is invalid') % dict(name='WIFI2 ' + T('Channel'))))
        ),
        Field('wifi2dhcp','boolean'),
        Field('wifi2vap','boolean'),
        Field('wifi2dhcprange',
            requires=IS_EMPTY_OR(IS_IPV4CIDR(error_message=T('%(name)s is invalid') % dict(name='WIFI2 ' + T('DHCP Range'))))
        ),
        Field('nickname',
            requires=IS_EMPTY_OR(
                IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Nickname'), len='32'))
            )
        ),
        Field('name',
            requires=IS_EMPTY_OR(
                IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Name'), len='32'))
            )
        ),
        Field('email', requires=IS_EMPTY_OR(IS_EMAIL(error_message=T('Not a valid email address!')))),
        Field('phone', requires=IS_EMPTY_OR(
            IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Phone'), len='32'))
            )
        ),
        Field('location',
            requires=IS_EMPTY_OR(
                IS_LENGTH(64,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Location'), len='64'))
            )
        ),
        Field('note',
            requires=IS_EMPTY_OR(
                    IS_LENGTH(512,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Note'), len='512'))
                )
        ),
        Field('wanproto',
            requires=IS_EMPTY_OR(
                IS_IN_SET(config.wanprotos, error_message=T('%(name)s is invalid') % dict(name=T('Wan Protocol')))
            )
        ),
        Field('wanipv4addr',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='WAN ' + T('IP address'))))
        ),
        Field('wannetmask',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='WAN ' + T('Netmask'))))
        ),
        Field('wangateway',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='WAN ' + T('Gateway'))))
        ),
        Field('wandns',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='WAN ' + T('DNS'))))
        ),
        Field('wan_allow_ssh','boolean'),
        Field('wan_allow_web','boolean'),
        Field('sharenet','boolean'),
        Field('localrestrict','boolean'),
        Field('lanproto',
            requires=IS_EMPTY_OR(
                IS_IN_SET(config.lanprotos, error_message=T('%(name)s is invalid') % dict(name='LAN ' +T('Protocol')))
            )
        ),
        Field('lanipv4addr',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='LAN ' + T('IP address'))))
        ),
        Field('lannetmask',
            requires=IS_EMPTY_OR(IS_IPV4(error_message=T('%(name)s is invalid') % dict(name='LAN ' + T('Netmask'))))
        ),
        Field('lanipv6addr',
            requires=IS_EMPTY_OR(IS_IPV6CIDR(error_message=T('%(name)s is invalid') % dict(name='LAN ' + T('IPv6 address'))))
        ),
        Field('lanipv6ra', 'boolean'),
        Field('landhcp','boolean'),
        Field('landhcprange',
            requires=IS_EMPTY_OR(IS_IPV4CIDR(error_message=T('%(name)s is invalid') % dict(name='LAN ' + T('DHCP Range'))))
        ),
    )
