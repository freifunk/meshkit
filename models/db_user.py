# coding: utf8
## create all tables needed by auth if not custom tables

########################################
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
# We don't use first/lastname, so replace firstname with username to show in navbar
if auth.user:
    auth.user.first_name = auth.user.username
    
crud, service, plugins = Crud(db), Service(), PluginManager()

db.define_table('auth_user',
    Field('username', type='string',
          label=XML('<span class="required">*</span>' + T('Username'))),
    Field('email', type='string',
          label=T('Email')),
    Field('password', type='password',
          readable=False,
          label=XML('<span class="required">*</span>' + T('Password'))),
    Field('created_on','datetime',default=request.now,
          label=T('Created On'),writable=False,readable=False),
    Field('modified_on','datetime',default=request.now,
          label=T('Modified On'),writable=False,readable=False,
          update=request.now),
    Field('registration_key',default='',
          writable=False,readable=False),
    Field('reset_password_key',default='',
          writable=False,readable=False),
    Field('registration_id',default='',
          writable=False,readable=False),
    format='%(username)s',
    migrate=settings.migrate, fake_migrate=settings.fake_migrate
)
db.auth_user.password.requires = CRYPT(key=auth.settings.hmac_key)
db.auth_user.username.requires = IS_NOT_IN_DB(db, db.auth_user.username)
db.auth_user.email.requires = (IS_EMAIL(error_message=auth.messages.invalid_email),
                               IS_NOT_IN_DB(db, db.auth_user.email))


# If communitysupport is enabled then add a extended user profile with image
# default options

if config and config.communitysupport:
    db.define_table('user_defaults',
        Field('community',
            label=T('Community'),
            comment=T('Please select your wireless community here. This will select reasonable defaults for step 2 of the image configuration.'),
            requires=IS_IN_SET(communities,
                zero='--- %s ---' % T('Please choose a community'),
                error_message=T('%(name)s is invalid') % dict(name=T('Community'))
            )
        ),
        Field('expert', 'boolean', label=T('Expert mode'),
            comment=T('Enable this to show much more options for customizing your firmware.')
        ),
        Field('nickname',
            label = T('Nickname'),
            comment = T('Enter your nickname here.'),
            requires=IS_EMPTY_OR(
                IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Nickname'), len='32'))
            )
        ),
        Field('name',
            label = T('Name'),
            comment = T('Enter your name here.'),
            requires=IS_EMPTY_OR(
                IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Name'), len='32'))
            )
        ),
        Field('email',
            label = T('Mail'),
            comment = T('Enter your email address here.'),
            requires=IS_EMPTY_OR(IS_EMAIL(error_message=T('Not a valid email address!')))
        ),
        Field('phone', label=T('Phone'),
            comment = T('Enter your phone number here.'),
            requires=IS_EMPTY_OR(
            IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Phone'), len='32'))
            )
        ),
        Field('location', label=T('Location'),
            comment=T('Location of your node.'),
            requires=IS_EMPTY_OR(
                IS_LENGTH(64,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Location'), len='64'))
            )
        ),
        Field('note', length=1024, type='text', label = T("Note"),
            comment = T('You may enter a custom comment here.'),
            requires=IS_EMPTY_OR(
                    IS_LENGTH(1024,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Note'), len='1024'))
                )
        ),
        Field('homepage',
            label = T('Homepage'),
            comment = T('If you have a homepage, then you can add it here.'),
            requires=IS_EMPTY_OR(
                IS_URL(error_message=T("%(name)s isn't a valid URL") % dict(name=T('Homepage'), len='255'))
            )
        ),
        Field('password_hash', type='string', default=None,
              requires=IS_EMPTY_OR(
                IS_MD5CRYPT()
              ),
              label=T('Default password'),
              comment=T('Default password that is set on the router. We only store a salted hash of the password on the server. Still you should change the password after you flashed the image and log in for the first time.'),
              widget=password_md5crypt
        ),
        Field('pubkeys',type='text', label=T('Public Keys'),
            comment=T('Add ssh public keys, one per line.'),
            requires=IS_EMPTY_OR([
                    IS_LENGTH(32768,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Pubkeys'), len='32768')),
                    IS_MATCH('[a-zA-Z0-9\/\+,-@\.\=]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Pubkeys')) )
                ])
        ),
        Field(
            'id_auth_user', db.auth_user, label="User Profile ID",
            comment="ID of the parent user profile"
        ),
        Field('created_on','datetime',default=request.now,
              label=T('Created On'),writable=False,readable=False),
        Field('modified_on','datetime',default=request.now,
              label=T('Modified On'),writable=False,readable=False,
              update=request.now),
        format='%(name)s',
        migrate=settings.migrate, fake_migrate=settings.fake_migrate
    )
    db.user_defaults.name.requires = IS_EMPTY_OR([
        IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Nickname'), len='32')),
        IS_MATCH('[a-zA-Z0-9:ÜÄÖüöä \.,\-\_\n]+', )
    ])
    db.user_defaults.phone.requires = IS_EMPTY_OR([
        IS_MATCH('[0-9\+\/ \-]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Phone')) ),
        IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Phone'), len='32') )
    ])
    db.user_defaults.location.requires = requires=IS_EMPTY_OR([
        IS_LENGTH(64,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Location'), len='64')),
        IS_MATCH('[a-zA-Z0-9:ÜÄÖüöä \.,\-\_\n]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Location')) )
    ])
    db.user_defaults.note.requires = IS_EMPTY_OR([
        IS_LENGTH(512,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Note'), len='512')),
        IS_MATCH('[a-zA-Z0-9:ÜÄÖüöä \.,\-\_\n]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Note')) )
    ])
    
#    auth.settings.extra_fields['auth_user'] = [
#        Field(
#            'defaults', db.user_defaults, label="Firmware Defaults",
#            comment="Defaults that are used to prefill some form fields."
#        )
#    ]
    


  
auth.define_tables(migrate = settings.migrate)

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## configure email
mail=auth.settings.mailer
mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.tls = settings.email_tls
mail.settings.login = settings.email_login

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')
