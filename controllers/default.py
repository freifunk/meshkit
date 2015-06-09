# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
import mkutils
import os
import subprocess
import formhelpers

### end requires

# Make sure the build_queue is running. because internal crontab performance is really bad with wsgi
# fake crontab functionality here. Also it is not possible to call private/build_queue.py directly
# when using wsgi. So call this init instead.
def check_queue():
    queue_status = mkutils.check_pid(os.path.join(request.folder, "private", "buildqueue.pid"), False)
    if queue_status:
        return True
    else:
        subprocess.call(['python', 'web2py.py', '-S', 'meshkit', '-M', '-R', os.path.join(request.folder, 'init', 'build_queue.py')])



def error():
    if not config.noconf == True:
        if not config.profiles or not os.access(config.profiles, os.R_OK):
            return dict(error=T('The directory %(dir)s which should contain community profiles was not accessible! Please check the config.') % dict(dir=config.profiles))

def config_not_found():
    return dict()

def index():
    check_queue()
    # if config doesn't exist in database yet redirect to appadmin
    if not config:
        response.flash = "No config found, redirecting you to create one"
        redirect(URL(request.application, request.controller,'config_not_found'))

    # Get a list of communities we know
    if config.communitysupport == True:
        if not config.profiles or not os.access(config.profiles, os.R_OK):
            redirect(URL(request.application, request.controller,'error'))
        else:
            communities = get_communities(config.profiles)
    else:
        db.imageconf.community.requires=IS_EMPTY()
        communities = []
            
    targets = get_targets(config.buildroots_dir)
    if len(targets) == 1:
        pass
        #db.imageconf.target.default = targets[0]
        #db.imageconf.target.writable = False
        
        
    if len(communities) == 1:
        db.imageconf.community.default = communities[0]
        db.imageconf.community.writable = False
    
    if auth.user:
        session.community = auth.user.community
        db.imageconf.community.default = session.community
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
        response.flash="form accepted"
        session.community = form.vars.community
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
            response.flash = XML(T('Form has errors:') + "</br><ul>" + errormsg + "</ul>")

    return dict(form=form, formhelpers=formhelpers, modellist=modellist,
                startpage=startpage)
    
# coding: utf8
# try something like
def wizard():
    import random
    import datetime
    import hashlib

    # check if community and target are set, else redirect to the index page
    # todo
    # list of profiles
    session.profiles = get_profiles(config.buildroots_dir, session.target, os.path.join(request.folder, "static", "ajax"), True)
    
    # overwrite field defaults and requires before creating the SQLFORM
    
    if auth.user:
        db.imageconf.pubkeys.default = auth.user.pubkeys
        db.imageconf.location.default = auth.user.location
        db.imageconf.nickname.default = auth.user.username
        db.imageconf.name.default = auth.user.name
        db.imageconf.email.default = auth.user.email
        db.imageconf.homepage.default = auth.user.homepage
        db.imageconf.phone.default = auth.user.phone
        db.imageconf.note.default = auth.user.note
        
    
    db.imageconf.profile.requires = IS_IN_SET(
        session.profiles,
        zero=None,
        error_message=T('%(name)s is invalid') % dict(name=T('Profile'))
    )
    db.imageconf.profile.default=session.profile
    
    db.imageconf.webif.requires = IS_IN_SET(
        config.webifs,
        error_message=T('%(name)s is invalid') % dict(name=T('Webinterface')),
        zero=None,
    )
    
    db.imageconf.theme.requires = IS_IN_SET(
        themes,
        error_message=T('%(name)s is invalid') % dict(name=T('Theme')),
        zero=None,
    )
    
    db.imageconf.lanproto.requires = IS_IN_SET(
        config.lanprotos,
        error_message=T('%(name)s is invalid') % dict(name='LAN ' +T('Protocol')),
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
        for f in ['chan', 'dhcp', 'dhcprange', 'ipv4addr', 'ipv6addr', 'vap', 'ipv6ra', 'enabled']:
            name = 'wifi%s%s' % (i, db.wifi_interfaces[f].name)
            #default = db.wifi_interfaces[f].default
            #wfields.append(db.wifi_interfaces[f].clone(name=name, default=default))
            wfields.append(db.wifi_interfaces[f].clone(name=name))

        
    
    form = SQLFORM.factory(db.imageconf, *wfields, table_name='imageconf')
    
    # session.profiles = get_profiles(config.buildroots_dir, session.target, os.path.join(request.folder, "static", "ajax"))
    defaultpkgs = get_defaultpkgs(config.buildroots_dir, session.target, os.path.join(request.folder, "static", "ajax"))
    # generate a static package list (this is only done once).
    # if package lists change delete the cache file in static/package_lists/<target>
    create_package_list(config.buildroots_dir, session.target, os.path.join(request.folder, "static", "package_lists"))
    user_packagelist = ''
    ipv6 = ipv6_config = ipv6_packages = ""
    session.url = URL(request.application, request.controller, 'api/json/buildimage', scheme=True, host=True)
    if config.communitysupport == True:
        nodenumber = ''
        # Add meshwizard to defaultpackages and lucipackages
        defaultpkgs.append('meshwizard')
        lucipackages = config.lucipackages + " luci-app-meshwizard"
        session.communitysupport = True
    else:
        session.communitysupport = False
        lucipackages = config.lucipackages
        nodenumber = False
        community_defaults = dict()
        
    if not session.mail:
        session.mail = ''
        
    if session.ipv6 == True:
        ipv6_packages = config.ipv6packages or ''
        if ipv6_config == 'auto-ipv6-random' or ipv6_config == 'auto-ipv6-fromv4':
            ipv6_packages = ipv6_packages + ' auto-ipv6-ib'


    if form.process(session=None, formname='step2', keepvalues=True).accepted:
        session.profile = form.vars.profile
        session.noconf = form.vars.noconf or config.noconf
        session.rand = form.vars.rand
        session.id = form.vars.id
        
        wifi_options = filter_wifi_interfaces(form.vars)
 
         # auto-set hostname if it is empty
        if not form.vars.hostname:
            form.vars.hostname = get_hostname_from_form_vars(form.vars)
        
        id = db.imageconf.insert(**db.imageconf._filter_fields(form.vars))
        session.id = id
        
        for i in wifi_options:
            if i["enabled"] == True:
                id_row = db.wifi_interfaces.insert(id_build=id, **db.wifi_interfaces._filter_fields(i))
                if id_row:
                    row = db(db.wifi_interfaces.id == id_row).select().first()
                    row.update_record(id_build=id, enabled=True)    
                    db.commit()
                
        redirect(URL('build'))
        
    elif form.errors:
        errormsg = ''
        for i in form.errors:
            errormsg = errormsg + "<li>" + str(form.errors[i]) + "</li>"
            response.flash = XML(T('Form has errors:') + "</br><ul>" + errormsg + "</ul>")
        session.profile = form.vars.profile or ''
        session.webif = form.vars.webif or ''
        session.wifiifsnr = form.vars.wifiifsnr or 1
        user_packagelist = form.vars.packages or ''
        
    hash = hashlib.md5(str(datetime.datetime.now()) + str(random.randint(1,999999999))).hexdigest()
    
    return dict(form=form, packages='',rand=hash, defaultpkgs=defaultpkgs, lucipackages=lucipackages, nodenumber=nodenumber,
                community_packages=session.community_packages  + " " + config.add_defaultpackages,
                user_packagelist=user_packagelist, addpackages='',
                ipv6_packages=ipv6_packages, formhelpers=formhelpers,
                fh = formhelpers.customField(form, "imageconf")
                )

def build():
    queuedimg = str(cache.ram('queuedimg',lambda:len(db(db.imageconf.status=='1').select()),time_expire=60))
    return locals()
    
def about():
    adminmail = config.adminmail.replace('@', '(at)')
    return dict(adminmail=adminmail)

### API

@service.json
def targets():
    targets = get_targets(config.buildroots_dir)
    if targets:
        return targets

@service.json
def status():
    ret = {}
    ret['status'] = check_queue()
    ret['loadavg'] = cache.ram('loadavg',lambda:mkutils.loadavg(),time_expire=10)
    memory = cache.ram('memory',lambda:mkutils.memory_stats(),time_expire=10)
    ret['memused'], ret['memfree'] = str(memory[1]), str(memory[2])
    ret['totalimg'] = cache.ram('totalimg',lambda:db(db.imageconf).select(db.imageconf.id.max()).first()['MAX(imageconf.id)'],time_expire=60)
    ret['queuedimg'] = cache.ram('queuedimg',lambda:len(db(db.imageconf.status=='1').select()),time_expire=60)
    ret['failedimg'] = cache.ram('failedimg',lambda:len(db((db.imageconf.status=='2') | (db.imageconf.status=='3')).select()),time_expire=60)
    ret['successimg'] = cache.ram('successimg',lambda:ret['totalimg'] - ret['failedimg'],time_expire=60)
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
    ret['queued'] = cache.ram('queuedimg',lambda:len(db(db.imageconf.status=='1').select()),time_expire=10)
    #add some summary information
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
        ret['downloaddir'] = config.images_web_dir + '/' + request.vars.rand + '/bin/'
        ret['files'] = []
        for filename in os.listdir(config.images_output_dir + '/' + request.vars.rand + '/bin/' ):
            ret['files'].append(filename)
    
    return ret

@service.json
def buildimage():
    import random
    import datetime
    import hashlib

    request.vars.rand = hashlib.md5(str(datetime.datetime.now()) + str(random.randint(1,999999999))).hexdigest()
    #request.vars.url = URL(request.application, request.controller, 'wizard', scheme=True, f=True)
    request.vars.url = URL(request.application, request.controller, 'wizard', scheme=True)
    request.vars.status = "1"

    if not request.vars.target:
        return {'errors': 'Required variable "target" is missing.'}

    # apply some magic (rename packages that have been renamed/merged) so firmwareupdate.sh
    # keeps working in this case
    if request.vars.packages:
        replacement_table = { 'luci-proto-6x4': 'luci-proto-ipv6', 'luaneightbl': 'luci-lib-luaneightbl' }
        request.vars.packages = replace_obsolete_packages(os.path.join(request.folder, "static", "package_lists", request.vars.target), request.vars.packages, replacement_table)
        
    
    # auto-set hostname if it is empty
    if not request.vars.hostname:
        request.vars.hostname = get_hostname_from_form_vars(request.vars)

    ret = db.imageconf.validate_and_insert(**db.imageconf._filter_fields(request.vars))
    #session.id = ret.id

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
