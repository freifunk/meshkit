# coding: utf8
## create all tables needed by auth if not custom tables

########################################
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

# If communitysupport is enabled show more fields in profile
if config and config.communitysupport:
    db.define_table('auth_user',
        Field('username', type='string', label=XML('<span class="required">*</span>' + T('Username'))),
        Field('community',
            requires=IS_EMPTY_OR(IS_IN_SET(communities, error_message=T('%(name)s is invalid') % dict(name=T('Community'))))
        ),
        Field('name', type='string',
              label=T('Name')),
        Field('phone', type='string',
              label=T('Phone')),
        Field('location', type='string',
              label=T('Location')),
        Field('note', type='text',
              label=T('Note')),
        Field('email', type='string',
              label=T('Email')),
        Field('pubkeys', type='text',
            requires=IS_EMPTY_OR([
                    IS_LENGTH(32768,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Pubkeys'), len='32768')),
                    IS_MATCH('[a-zA-Z0-9\/\+\s,-@\.\=]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Pubkeys')) )
                ])
        ),
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
    migrate=settings.migrate, fake_migrate=settings.fake_migrate)
    db.auth_user.name.requires = IS_EMPTY_OR([
            IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Nickname'), len='32')),
            IS_MATCH('[a-zA-Z0-9:ÜÄÖüöä \.,\-\_\n]+', )
        ])
    db.auth_user.phone.requires = IS_EMPTY_OR([
            IS_MATCH('[0-9\+\/ \-]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Phone')) ),
            IS_LENGTH(32,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Phone'), len='32') )
        ])
    db.auth_user.location.requires = requires=IS_EMPTY_OR([
            IS_LENGTH(64,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Location'), len='64')),
            IS_MATCH('[a-zA-Z0-9:ÜÄÖüöä \.,\-\_\n]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Location')) )
        ])
    db.auth_user.note.requires = IS_EMPTY_OR([
            IS_LENGTH(512,0, error_message=T('%(name)s can only be up to %(len)s characters long') % dict(name=T('Note'), len='512')),
            IS_MATCH('[a-zA-Z0-9:ÜÄÖüöä \.,\-\_\n]+', error_message=T('%(name)s contains invalid characters') % dict(name=T('Note')) )
        ])
else:
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
        migrate=settings.migrate, fake_migrate=settings.fake_migrate)

db.auth_user.password.requires = CRYPT(key=auth.settings.hmac_key)
db.auth_user.username.requires = IS_NOT_IN_DB(db, db.auth_user.username)
db.auth_user.email.requires = (IS_EMAIL(error_message=auth.messages.invalid_email),
                               IS_NOT_IN_DB(db, db.auth_user.email))
  
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
