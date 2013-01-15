# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
import meshkit
import uci
import utils
import os
import subprocess
import formhelpers

### end requires

# Make sure the build_queue is running. because internal crontab performance is really bad with wsgi
# fake crontab functionality here. Also it is not possible to call private/build_queue.py directly
# when using wsgi. So call this init instead.
def check_queue():
    queue_status = utils.check_pid(os.path.join(request.folder, "private", "buildqueue.pid"), False)
    if queue_status:
        return True
    else:
        subprocess.call(['python', 'web2py.py', '-S', 'meshkit', '-M', '-N',  '-R', os.path.join(request.folder, 'init', 'build_queue.py')])

# We don't use first/lastname, so replace firstname with username to show in navbar
if auth.user:
    auth.user.first_name = auth.user.username

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
        communities = []
            
    targets = get_targets(config.buildroots_dir)
    
    if auth.user:
        user_email = auth.user.email
        session.community = auth.user.community
    else:
        user_email = ''
        session.community = ''
        
    form = SQLFORM.factory(db.imageconf)
    modellist = '{'
    i = 1
    for k in sorted(config_modellist.keys()):
        modellist += k + ":" + str(config_modellist[k]) + ","
    modellist += '}'

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
        redirect(URL('wizard'))
    elif form.errors:
        errormsg = ''
        for i in form.errors:
            errormsg = errormsg + "<li>" + str(form.errors[i]) + "</li>"
            response.flash = XML(T('Form has errors:') + "</br><ul>" + errormsg + "</ul>")
    return dict(form=form,communities=communities, targets=targets, user_email=user_email,
                formhelpers=formhelpers, vars=form.vars, modellist=modellist, startpage=startpage)
    
# coding: utf8
# try something like
def wizard():
    import random
    import datetime
    import hashlib
    # add target to response subtitle
    response.subtitle = settings.subtitle + " [" + session.target + "]"
    # check if community and target are set, else redirect to the index page
    # todo
    # list of profiles
    session.profiles = get_profiles(config.buildroots_dir, session.target, os.path.join(request.folder, "static", "ajax"))
    form = SQLFORM(db.imageconf)
    # session.profiles = get_profiles(config.buildroots_dir, session.target, os.path.join(request.folder, "static", "ajax"))
    defaultpkgs = get_defaultpkgs(config.buildroots_dir, session.target, os.path.join(request.folder, "static", "ajax"))
    session.theme = config.defaulttheme
    # generate a static package list (this is only done once.
    # if package lists change delete the cache file in static/package_lists/<target>
    create_package_list(config.buildroots_dir, session.target, os.path.join(request.folder, "static", "package_lists"))
    user_packagelist = ''
    latitude = longitude = defchannel = mesh_network = defip = community_packages = ipv6 = ipv6_config = ipv6_packages = ""
    if config.communitysupport == True:
        c = uci.UCI(config.profiles, "profile_" + session.community)
        community_defaults = c.read()
        # Add meshwizard to defaultpackages and lucipackages
        defaultpkgs.append('meshwizard')
        lucipackages = config.lucipackages + " luci-app-meshwizard"
        session.communitysupport = True
        latitude = c.get(community_defaults, 'profile', 'latitude', '48')
        longitude = c.get(community_defaults, 'profile', 'longitude', '10')
        defchannel = c.get(community_defaults, 'wifi_device', 'channel', '1')
        mesh_network = c.get(community_defaults, 'profile', 'mesh_network', '10.0.0.0/8')
        if mesh_network:
            defip = meshkit.defip(mesh_network)
        else:
            defip = ""
        community_packages  = c.get(community_defaults, 'profile', 'extrapackages', '')
        ipv6 = c.get(community_defaults, 'profile', 'ipv6', '0')
        ipv6_config = c.get(community_defaults, 'profile', 'ipv6_config', False)
        session.theme = c.get(community_defaults, 'profile', 'theme', config.defaulttheme)
    else:
        session.communitysupport == False
        lucipackages = config.lucipackages
        community_defaults = dict()
        
    session.localrestrict=True

    if not session.mail:
        session.mail = ''
    if ipv6 == '1':
        session.ipv6 = True
        session.wifi0ipv6ra = True
        session.wifi1ipv6ra = True
        session.wifi2ipv6ra = True
        session.ipv6conf = True
        session.ipv6_config = ipv6_config
        ipv6_packages = config.ipv6packages or ''
        if ipv6_config == 'auto-ipv6-random' or ipv6_config == 'auto-ipv6-fromv4':
            ipv6_packages = ipv6_packages + ' auto-ipv6-ib'
    else:
        session.ipv6 = False
        session.ipv6conf = False
        session.ipv6_config = None
        session.wifi0ipv6ra = False
        session.wifi1ipv6ra = False
        session.wifi2ipv6ra = False

    if auth.user:
        session.nickname = auth.user.username or ''
        session.name = auth.user.name or ''
        session.phone = auth.user.phone or ''
        session.location = auth.user.location or ''
        session.note = auth.user.note or ''
        session.pubkeys = auth.user.pubkeys or ''
    else:
        session.nickname = ''
        session.name = ''
        session.phone = ''
        session.location = ''
        session.note = ''
        session.pubkeys = ''
    if form.process(session=None, formname='step2', keepvalues=True).accepted:
        session.profile = form.vars.profile
        session.noconf = form.vars.noconf or config.noconf
        session.rand = form.vars.rand
        redirect(URL('build'))
    elif form.errors:
        errormsg = ''
        for i in form.errors:
            errormsg = errormsg + "<li>" + str(form.errors[i]) + "</li>"
            response.flash = XML(T('Form has errors:') + "</br><ul>" + errormsg + "</ul>")
        session.profile = form.vars.profile or ''
        session.webif = form.vars.webif or ''
        session.theme = form.vars.theme or config.defaulttheme
        session.wifiifsnr = form.vars.wifiifsnr or 1
        session.ipv6 = form.vars.ipv6 or False
        session.wifi0ipv6ra = form.vars.wifi0ipv6ra or False
        session.wifi1ipv6ra = form.vars.wifi1ipv6ra or False
        session.wifi2ipv6ra = form.vars.wifi2ipv6ra or False
        session.localrestrict = form.vars.localrestrict or False
        user_packagelist = form.vars.packages or ''
        latitude = form.vars.latitude or ''
        longitude = form.vars.longitude or ''
        
    hash = hashlib.md5(str(datetime.datetime.now()) + str(random.randint(1,999999999))).hexdigest()
    return dict(form=form, packages='',rand=hash, defaultpkgs=defaultpkgs, lucipackages=lucipackages,
                lat=latitude, lon=longitude, defchannel=defchannel, defip=defip,
                community_packages=community_packages  + " " + config.add_defaultpackages,
                user_packagelist=user_packagelist, addpackages='',
                ipv6_packages=ipv6_packages, formhelpers=formhelpers
                )

def build():
    return dict()
    
def about():
    adminmail = config.adminmail.replace('@', '(at)')
    return dict(adminmail=adminmail)

def status():
    status = check_queue()
    loadavg = cache.ram('loadavg',lambda:utils.loadavg(),time_expire=10)
    memory = cache.ram('memory',lambda:utils.memory_stats(),time_expire=10)
    memused, memfree = str(memory[1]), str(memory[2])
    totalimg = cache.ram('totalimg',lambda:db(db.imageconf).select(db.imageconf.id.max()).first()['MAX(imageconf.id)'],time_expire=60)
    failedimg = cache.ram('failedimg',lambda:len(db((db.imageconf.status=='2') | (db.imageconf.status=='3')).select()),time_expire=60)
    successimg = cache.ram('successimg',lambda:totalimg - failedimg,time_expire=60)
    return locals()
