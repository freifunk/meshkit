# -*- coding: utf-8 -*-
# required - do no delete


def user():
    return dict(form=auth())


def download():
    return response.download(request, db)


def call():
    return service()
import mkutils
import os
import subprocess
import formhelpers
from meshkit import target_shorten


def error():
    if not config.noconf:
        if not config.profiles or not os.access(config.profiles, os.R_OK):
            return dict(
                error=T(
                    'The directory %(dir)s which should contain community ' +
                    'profiles was not accessible! Please check the config.'
                ) % dict(dir=config.profiles))


def config_not_found():
    return dict()


def index():
    # if config doesn't exist in database yet redirect to appadmin
    if not config:
        response.flash = "No config found, redirecting you to create one"
        redirect(
            URL(request.application,
                request.controller,
                'config_not_found'))

    # Get a list of communities we know
    if config.communitysupport:
        if not config.profiles or not os.access(config.profiles, os.R_OK):
            redirect(URL(request.application, request.controller, 'error'))
        else:
            communities = get_communities(config.profiles)
    else:
        db.imageconf.community.requires = IS_EMPTY()
        communities = []

    # allow empty values for webif in this step
    db.imageconf.webif.requires = IS_EMPTY_OR(
        IS_IN_DB(
            db, db.gui.id, '%(full_name)s'
        ),
    ),

    targets = get_targets(config.buildroots_dir)
    if len(targets) == 1:
        db.imageconf.target.default = targets[0]
        db.imageconf.target.writable = False
        db.imageconf.target.widget = SQLFORM.widgets.string.widget
        session.target = targets[0]

    if len(communities) == 1:
        db.imageconf.community.default = communities[0]
        db.imageconf.community.writable = False
        db.imageconf.community.widget = SQLFORM.widgets.string.widget
        session.community = communities[0]

    if auth.user:
        user_defaults = db(
            db.user_defaults.id_auth_user == auth.user_id).select(
        ).first(
        )
        if user_defaults:
            if "community" in user_defaults:
                session.community = user_defaults.community
                db.imageconf.community.default = session.community
                if "expert" in user_defaults:
                    db.imageconf.expert.default = user_defaults.expert
        # use the registration email here, not the one from user defaults.
        db.imageconf.mail.default = auth.user.email
    else:
        session.community = ''

    form = SQLFORM.factory(db.imageconf, table_name='imageconf')

    modellist = '{'
    i = 1
    for k in sorted(config_modellist.keys()):
        modellist += k + ":" + str(config_modellist[k]) + ","
    modellist += '}'

    # TODO. rework. Use wiki?

    lang = T.accepted_language or 'en'
    if lang == "de" and content_de:
        content = content_de
    else:
        content = content_en

    if content:
        startpage = content.startpage or content_en.startpage or ''
    else:
        startpage = ''

    if form.process(session=None, formname='step1', keepvalues=True).accepted:
        response.flash = "form accepted"
        if "community" in form.vars:
            session.community = form.vars.community
        if "target" in form.vars:
            session.target = form.vars.target
        session.mail = form.vars.mail
        session.profile = form.vars.profile or 'Default'
        session.noconf = form.vars.noconf or config.noconf
        session.expert = form.vars.expert
        if session.noconf:
            session.expert = True
        redirect(URL('wizard'))
    elif form.errors:
        errormsg = ''
        for i in form.errors:
            errormsg = errormsg + "<li>" + str(form.errors[i]) + "</li>"
            response.flash = XML(
                T('Form has errors:') + "</br><ul>" + errormsg + "</ul>")

    return dict(form=form, formhelpers=formhelpers, modellist=modellist,
                startpage=startpage)


def wizard():
    import random
    import datetime
    import hashlib

    # check if community and target are set, else redirect to the index page
    # todo
    # list of profiles
    if not session.target:
        redirect((URL('error')))

    session.target_short = target_shorten(session.target)

    session.profiles = get_profiles(
        config.buildroots_dir,
        session.target,
        os.path.join(request.folder, "static", "ajax"),
        True
    )

    # overwrite field defaults and requires before creating the SQLFORM

    if auth.user:
        user_defaults = db(
            db.user_defaults.id_auth_user == auth.user_id).select(
        ).first(
        )
        ud_items = [
            'pubkeys',
            'expert',
            'location',
            'nickname',
            'name',
            'email',
            'homepage',
            'phone',
            'note',
            'password_hash']

        for k in ud_items:
            if k in user_defaults and user_defaults[k]:
                db.imageconf[k].default = user_defaults[k]


    db.imageconf.profile.requires = IS_IN_SET(
        session.profiles,
        zero=None,
        error_message=T('%(name)s is invalid') % dict(name=T('Profile'))
    )
    db.imageconf.profile.default = session.profile

    db.imageconf.theme.requires = IS_IN_SET(
        themes,
        error_message=T('%(name)s is invalid') % dict(name=T('Theme')),
        zero=None,
    )

    db.imageconf.lanproto.requires = IS_IN_SET(
        config.lanprotos,
        error_message=T('%(name)s is invalid') % dict(
            name='LAN ' + T('Protocol')),
        zero=None
    )

    db.imageconf.wanproto.requires = IS_IN_SET(
        config.wanprotos,
        error_message=T('%(name)s is invalid') % dict(name=T('Wan Protocol')),
        zero=None
    )

    # add fields for wireless interfaces wifi0 to wifi2 by cloning them from
    # the db.wifi_interfaces table and adding custom names.

    wfields = []
    for i in range(3):
        for f in ['chan', 'dhcp', 'dhcprange', 'ipv4addr', 'ipv6addr', 'vap',
                  'ipv6ra', 'enabled']:
            name = 'wifi%s%s' % (i, db.wifi_interfaces[f].name)
            # default = db.wifi_interfaces[f].default
            # wfields.append(db.wifi_interfaces[f].clone(name=name,
            # default=default))
            wfields.append(db.wifi_interfaces[f].clone(name=name))

    form = None
    id = None
    if auth.user and request.args(0):
        record = db.imageconf(
            request.args(0)) or redirect(URL('access_denied')
        )

        if record.id_user == auth.user_id:
            form = SQLFORM.factory(
                db.imageconf,
                table_name='imageconf',
                *wfields
            )
            id = request.args(0)
        else:
            # access denied
            redirect(URL('access_denied'))
    else:
        form = SQLFORM.factory(db.imageconf, table_name='imageconf', *wfields)

    # session.profiles = get_profiles(config.buildroots_dir, session.target,
    # os.path.join(request.folder, "static", "ajax"))
    defaultpkgs = get_defaultpkgs(
        config.buildroots_dir,
        session.target,
        os.path.join(request.folder, "static", "ajax")
    )
    # generate a static package list (this is only done once).
    # if package lists change delete the cache file in
    # static/package_lists/<target>
    create_package_list(
        config.buildroots_dir,
        session.target,
        os.path.join(request.folder, "static", "package_lists")
    )
    user_packagelist = ''
    ipv6_packages = ""

    session.url = URL(
        request.application,
        request.controller,
        'api/json/buildimage',
        scheme=True,
        host=True
    )
    if config.communitysupport:
        nodenumber = ''
        # Add meshwizard to defaultpackages
        defaultpkgs.append('meshwizard')
        session.communitysupport = True
    else:
        session.communitysupport = False
        nodenumber = False

    if not session.mail:
        session.mail = ''

    if session.ipv6:
        ipv6_packages = config.ipv6packages or ''
        if session.ipv6_config == 'auto-ipv6-random' or \
           session.ipv6_config == 'auto-ipv6-fromv4':
            ipv6_packages = ipv6_packages + ' auto-ipv6-ib'

    if form.process(session=None, formname='step2', keepvalues=True).accepted:
        session.profile = form.vars.profile
        session.noconf = form.vars.noconf or config.noconf
        session.rand = form.vars.rand
        session.id = form.vars.id
        session.hostname = get_hostname_from_form_vars(form.vars)
        session.lanipv4addr = form.vars.lanipv4addr or '192.168.1.1'
        session.location = session.location or '-'

        wifi_options = filter_wifi_interfaces(form.vars)

        # write id of logged in user:
        if auth.user:
            form.vars.id_user = auth.user_id

        # auto-set hostname if it is empty
        if not form.vars.hostname:
            form.vars.hostname = session.hostname

        if id:
            query = (db.imageconf.id == id)
            db(query).update(**db.imageconf._filter_fields(form.vars))
            session.id = id
        else:
            id = db.imageconf.insert(**db.imageconf._filter_fields(form.vars))
            session.id = id

        session.main_mesh_ip = None
        for i in wifi_options:
            if i["enabled"]:
                id_row = db.wifi_interfaces.insert(
                    id_build=id,
                    **db.wifi_interfaces._filter_fields(i))
                if id_row:
                    row = db(db.wifi_interfaces.id == id_row).select().first()
                    row.update_record(id_build=id, enabled=True)
                    db.commit()
                if not session.main_mesh_ip:
                    if i["ipv4addr"]:
                        session.main_mesh_ip = i["ipv4addr"]

        # schedule task
        scheduler.queue_task(
            build,
            pvars=dict(id=id),
            immediate=True,
            task_name="build-%s" % id,
            timeout=settings.scheduler['timeout'],
            retry_failed=settings.scheduler['retry_failed']
        )
        redirect(URL('build'))

    elif form.errors:
        errormsg = ''
        for i in form.errors:
            errormsg = errormsg + "<li>" + str(form.errors[i]) + "</li>"
            response.flash = XML(
                T('Form has errors:') + "</br><ul>" + errormsg + "</ul>")
        session.profile = form.vars.profile or ''
        session.webif = form.vars.webif or ''
        session.wifiifsnr = form.vars.wifiifsnr or 1
        user_packagelist = form.vars.packages or ''

    hash = hashlib.md5(str(datetime.datetime.now())
                       + str(random.randint(1, 999999999))).hexdigest()

    community_packages = "%s %s" % (
        session.community_packages,
        config.add_defaultpackages
    )
    return dict(
        form=form, packages='', rand=hash, defaultpkgs=defaultpkgs,
        nodenumber=nodenumber, community_packages=community_packages,
        user_packagelist=user_packagelist, addpackages='',
        ipv6_packages=ipv6_packages, formhelpers=formhelpers,
        fh=formhelpers.customField(form, "imageconf")
    )


@auth.requires_login()
def user_defaults():
    """ user defaults to prefill fields in forms """
    user_defaults = db(
        db.user_defaults.id_auth_user == auth.user_id).select(
    ).first()
    id_user_defaults = None

    if user_defaults:
        id_user_defaults = user_defaults.id
    else:
        # no user defaults exist, creating a new row
        id_user_defaults = db.user_defaults.insert(
            id_auth_user=auth.user_id,
            nickname=auth.user.username,
            email=auth.user.email
        )
        user_defaults = db(
            db.user_defaults.id_auth_user == auth.user_id).select(
        ).first(
        )

    db.user_defaults.id.readable = False
    db.user_defaults.id_auth_user.readable = False
    db.user_defaults.id_auth_user.writable = False

    form = SQLFORM(db.user_defaults, id_user_defaults)

    if form.process(
        session=None,
        formname='user_defaults',
        keepvalues=True
    ).accepted:
        response.flash = 'form accepted'
        # reload page to get list:string options correct
        redirect(URL('user_defaults'))

    elif form.errors:
        errormsg = ''
        for i in form.errors:
            errormsg = errormsg + "<li>" + str(form.errors[i]) + "</li>"
            response.flash = XML(
                T('Form has errors:') + "</br><ul>" + errormsg + "</ul>")

    return(
        dict(
            form=form,
            formhelpers=formhelpers,
            fh=formhelpers.customField(form, "user_defaults")
        )
    )


@auth.requires_login()
def user_builds():
    """ Builds the user has done """

    def delete_multiple(ids):
        if not ids:
                session.flash=T('Select at least one record.')
        else:
                for id in ids:
                        db(
                            (db.imageconf.id_user == auth.user_id) & \
                            (db.imageconf.id == id)
                        ).delete()
                pass
        pass
        return ''

    if len(request.args) > 2:
        if request.args[0] == "edit":
            redirect(URL(wizard, args=[request.args[2]]))

    fields = [
        db.imageconf.hostname,
        db.imageconf.target,
        db.imageconf.profile,
        db.imageconf.location
    ]

    db.imageconf.target.represent = lambda target, _: target_shorten(target)
    
    grid = SQLFORM.grid(
        db.imageconf.id_user == auth.user_id,
        user_signature=False,
        showbuttontext=False,
        fields=fields,
        create=False,
        details=False,
        paginate=100,
        csv=False,
        maxtextlength=50,
        ui=settings.ui_grid,
        selectable=[
            [
                T('Delete'),
                lambda ids: delete_multiple(ids),
                "btn w2p-confirm"
            ]
        ]
    )

    heading=grid.elements('th')
    if heading:
        heading[0].append(
            INPUT(
                _type='checkbox',
                _id="imageconf-check-all",
                _class="grid-check-all",
                _title=T('Check all')
            )
        )

    # builds = db(db.user_defaults.id_auth_user ==
    # auth.user_id).select().first()
    return dict(grid=grid)


def build():
    queuedimg = str(
        cache.ram(
            'queuedimg',
            lambda: len(db(db.imageconf.status == '1').select()),
            time_expire=60
        )
    )
    url_summary = A(
        "summary.json",
        _title=T('Summary of the configuration (JSON)'),
        _target="blank",
        _href="%s/%s/bin/summary.json" % (config.images_web_dir, session.rand)
    )
    return locals()


def about():
    adminmail = config.adminmail.replace('@', '(at)')
    return dict(adminmail=adminmail)


def access_denied():
    return dict()


# API

@service.json
def targets():
    targets = get_targets(config.buildroots_dir)
    if targets:
        return targets


@service.json
def status():
    import status
    ret = {}
    ret['num_workers'] = mkutils.workers_online()
    ret['loadavg'] = cache.ram(
        'loadavg',
        lambda: mkutils.loadavg(),
        time_expire=10
    )
    memory = cache.ram(
        'memory',
        lambda: mkutils.memory_stats(),
        time_expire=10
    )

    queued = cache.ram(
        'queuedimg',
        lambda: db(db.imageconf.status == '1').count(),
        time_expire=60
    )

    failed = cache.ram(
        'failedimg',
        lambda: db(
            (db.build_log.status == '2') | (db.build_log.status == '3')
        ).count(),
        time_expire=60
    )

    success = cache.ram(
        'successimg',
        lambda: db(db.build_log.status == '0').count(),
        time_expire=60
    )

    ret['memused'], ret['memfree'] = str(memory[1]), str(memory[2])

    ret['build_status'] = {
        "data": {
            "queued": [
                queued,
                T("queued"),
                settings.colors["flotcharts-blue"]
            ],
            "success": [
                success,
                T("successful"),
                settings.colors["flotcharts-yellow"]
            ],
            "failed": [
                failed,
                T("failed"),
                settings.colors["flotcharts-red"]
            ]
        },
        "title": T("Build status")
    }

    ret['builds_community'] = {
        "data": cache.ram(
            'builds_community',
            lambda: status.community_builds(),
            time_expire=60
        ),
        "title": T("Builds per community")
    }
    ret['builds_target'] = {
        "data": cache.ram(
            'builds_target',
            lambda: status.target_builds(),
            time_expire=60
        ),
        "title": T("Builds per target")
    }

    return ret


@service.json
def buildstatus():
    try:
        _id = int(request.vars.id)
    except ValueError:
        return {'errors': 'Required variable "id" is invalid or missing.'}
    if not request.vars.rand:
        return {'errors': 'Required variable "rand" is missing.'}

    try:
        row = db(db.imageconf.id == request.vars.id).select()
        row = row[0]
    except KeyError:
        return {'errors': 'Wrong id.'}

    if not row.rand == request.vars.rand:
        return {'errors': 'Invalid rand number.'}

    ret = {}
    ret['queued'] = cache.ram(
        'queuedimg',
        lambda: len(db(db.imageconf.status == '1').select()),
        time_expire=10
    )
    # add some summary information
    ret['status'] = int(row.status)
    if row.hostname:
        ret['hostname'] = row.hostname
#    elif row.wifi0ipv4addr:
#        ret['hostname'] = row.wifi0ipv4addr.replace(".", "-")
#    else:
#        ret['hostname'] = '-'

    if row.nodenumber:
        ret['nodenumber'] = row.nodenumber

    ret['community'] = row.community or '-'
    ret['location'] = row.location or '-'
    ret['target'] = row.target or '-'
    ret['profile'] = row.profile or '-'

    if row.status == "0":
        ret['downloaddir'] = config.images_web_dir + \
            '/' + request.vars.rand + '/bin/'
        ret['files'] = []
        out_dir = "%s/%s/bin/" % (config.images_output_dir, request.vars.rand)
        for filename in os.listdir(out_dir):
            ret['files'].append(filename)

    return ret


@service.json
def buildimage():
    import random
    import datetime
    import hashlib

    request.vars.rand = hashlib.md5(
        str(datetime.datetime.now()) + str(random.randint(1, 999999999))
    ).hexdigest()

    request.vars.url = URL(
        request.application,
        request.controller,
        'wizard',
        scheme=True
    )
    request.vars.status = "1"

    if not request.vars.target:
        return {'errors': 'Required variable "target" is missing.'}

    # apply some magic (rename packages that have been renamed/merged)
    # so firmwareupdate.sh keeps working in this case
    if request.vars.packages:
        replacement_table = {
            'luci-proto-6x4': 'luci-proto-ipv6',
            'luaneightbl': 'luci-lib-luaneightbl'}
        request.vars.packages = replace_obsolete_packages(
            os.path.join(request.folder,
                         "static",
                         "package_lists",
                         request.vars.target),
            request.vars.packages,
            replacement_table)

    # auto-set hostname if it is empty
    if not request.vars.hostname:
        request.vars.hostname = get_hostname_from_form_vars(request.vars)

    ret = db.imageconf.validate_and_insert(
        **db.imageconf._filter_fields(request.vars))
    # session.id = ret.id

    wifi_options = filter_wifi_interfaces(request.vars)
    for i in wifi_options:
        id_row = db.wifi_interfaces.insert(**db.imageconf._filter_fields(i))
        if id_row:
            row = db(db.wifi_interfaces.id == id_row).select().first()
            row.update_record(id_build=ret.id, enabled=True)
            db.commit()

    ret['rand'] = request.vars.rand
    return ret


def api():
    session.forget()
    return service()
