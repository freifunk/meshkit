#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defined statuses:
0: build ok
1: pending
2: error building image
3: syserror (e.g. could not create directories)
"""

import time
import os
import errno
import subprocess
import sys
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json
import shutil
import mkutils
import distutils
from distutils.dir_util import copy_tree
from gluon import current
from gluon.scheduler import Scheduler

import sys
sys.path.append(os.path.join(request.folder, "private", "modules"))
import processupload
import log
logger = log.initialize_logging(request.folder, 'build_queue')


def mkdir_p(path):
    try:
        os.makedirs(path)
        return True
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            logger.critical("Error: Could not create directory %s" % path)
            return False


def cptree(src, dst):
    try:
        ct = copy_tree(src, dst, preserve_symlinks=0)
        logger.debug('Copied %s to %s' % (src, dst))
    except distutils.errors.DistutilsFileError as e:
        logger.warning(
            'Source directory %s does not exist. %s' % (src, str(e))
        )
    except IOError as e:
        logger.error(
            'Could not create/write to directory %s. Check permissions.' %
            dst
        )


class BuildImages(object):

    """
    This class is for configuring and building the images

    Args:
        config_path: Path where the uci config files are stored
        config_file: filename of the config file
    """

    def __init__(self, row=None):
        def _get(option):
            ret = None
            try:
                ret = row[option]
            except KeyError:
                logger.warning("Could not get option %s from the db" % option)
                pass
            return ret

        self.mkconfig = ''  # meshkit configuration (UCI format)
        self.Id = _get('id')
        self.Rand = _get('rand')
        self.Target = _get('target')
        self.Profile = _get('profile')
        self.Pubkeys = _get('pubkeys')
        self.password_hash = _get('password_hash')
        self.Pkgs = _get('packages') or ''
        self.rows_wifi = db(db.wifi_interfaces.id_build == self.Id).select()
        self.Noconf = _get('noconf')
        if not self.Noconf:
            self.Pkgs += ' meshwizard'
        for row_wifi in self.rows_wifi:
            if row_wifi.vap:
                self.Pkgs += ' hostapd-mini'
                break
        self.Upload = _get('upload')
        # this is the mailaddress used to send mails after build
        self.Mail = _get('mail')
        self.Latitude = _get('latitude') or ''
        self.Longitude = _get('longitude') or ''
        self.Hostname = _get('hostname')

        self.Ipv6 = _get('ipv6')
        self.Ipv6_config = _get('ipv6_config')
        self.Location = _get('location') or ''
        self.Community = _get('community') or 'augsburg'
        self.nodenumber = _get('nodenumber') or '1024'
        self.Nickname = _get('nickname') or ''
        self.Name = _get('name') or ''
        self.Homepage = _get('homepage') or ''
        self.Email = _get(
            'email') or ''  # this is the email address for contact information
        self.Phone = _get('phone') or ''
        self.Note = _get('note') or ''
        self.Theme = _get('theme')
        if self.Theme:
            self.Theme = self.Theme.replace(
                "luci-theme-",
                "") or 'freifunk-generic'
        else:
            self.Theme = 'freifunk-generic'
        self.Lanproto = _get('lanproto') or 'dhcp'
        self.Lanipv4addr = _get('lanipv4addr')
        self.Lannetmask = _get('lannetmask') or '255.255.255.0'
        self.Landhcp = _get('landhcp') and "1" or "0"
        self.Landhcprange = _get('landhcprange') or ''
        self.Wanproto = _get('wanproto') or 'static'
        self.Wanipv4addr = _get('wanipv4addr')
        self.Wannetmask = _get('wannetmask') or '255.255.255.0'
        self.Wangateway = _get('wangateway') or ''
        self.Wandns = _get('wandns') or ''
        self.Wan_allow_ssh = _get('wan_allow_ssh') and 1 or 0
        self.Wan_allow_web = _get('wan_allow_web') and 1 or 0
        self.Localrestrict = _get('localrestrict') and "1" or "0"
        self.Sharenet = _get('sharenet') and "1" or "0"
        self.Wan_qos = _get('wan_qos') and 1 or 0
        self.Wan_qos_down = _get('wan_qos_down') or "1024"
        self.Wan_qos_up = _get('wan_qos_up') or "128"
        self.Url = _get('url') or ''

        self.OutputDir = os.path.join(config.images_output_dir, self.Rand)
        self.FilesDir = os.path.join(self.OutputDir, "files")
        self.FilesDirInit = os.path.join(self.FilesDir, 'etc', 'init.d')
        self.FilesDirRc = os.path.join(self.FilesDir, 'etc', 'rc.d')
        self.FilesDirConfig = os.path.join(self.FilesDir, 'etc', 'config')
        self.BinDir = os.path.join(self.OutputDir, "bin")
        self.OutputDirWeb = os.path.join(config.images_web_dir, self.Rand)
        self.BinDirWeb = os.path.join(self.OutputDirWeb, "bin")

    def build_links_json(self):
        files = []
        for filename in os.listdir(self.BinDir):
            size = os.path.getsize(os.path.join(self.BinDir, filename))
            files.append({'name': filename, 'size': size})
        r = json.dumps(sorted(files))

        # Write info to file
        try:
            f = open(
                os.path.join(
                    request.folder,
                    "static",
                    "ajax",
                    self.Rand),
                "w")
            try:
                f.write(str(r))
            finally:
                f.close()
        except IOError:
            pass

    def summary_json(self):
        self.rows_wifi = self.rows_wifi.as_dict()
        r = json.dumps(self.__dict__, indent=4)
        return r

    def summary_json_write(self, jsondata):
        summaryfile = os.path.join(self.BinDir, "summary.json")
        logger.debug('Writing summary to %s' % summaryfile)

        # write summary to bin directory
        try:
            f = open(summaryfile, "w")
            try:
                f.write(str(jsondata))
            finally:
                f.close()
        except IOError:
            logger.warning("Could not write the summary.json file!")

    def SendMail(self, status):
        if status == 0:
            mailsubject = T("Meshkit has built your images")
            mailmessage = T(
                "Your images were built sucessfully, download them at %s." %
                self.BinDirWeb
            )
            mailmessage += "\n\n" + \
                T("Remember! You built this image with these settings:")
            mailmessage += "\n" + T("Community") + ": " + self.Community
            mailmessage += "\n" + T("Hostname") + ": " + self.Hostname
            mailmessage += "\n" + T("Location") + ": " + self.Location
            if self.Community == 'weimar':
                mailmessage += "\n" + T("Nodenumber") + ": " + self.nodenumber
            mailmessage += "\n" + T("Target") + ": " + self.Target
            if self.Profile:
                mailmessage += "\n" + T("Profile") + ": " + self.Profile
            mailmessage += "\n\n" + T("Thank you for your cooperation!")
        elif status == 3:
            mailsubject = T("Meshkit could not built your images")
            mailmessage = T(
                "Your images could not be build because there was a system " +
                "error."
            )
            mailmessage += "\n\n" + \
                T("Remember! You tried to build an image with these settings:")
            if self.Community:
                mailmessage += "\n" + T("Community") + ": " + self.Community
            if self.Hostname:
                mailmessage += "\n" + T("Hostname") + ": " + self.Hostname
            if self.location:
                mailmessage += "\n" + T("Location") + ": " + self.Location
            if self.Community == 'weimar':
                mailmessage += "\n" + T("Nodenumber") + ": " + self.nodenumber
            if self.Target:
                mailmessage += "\n" + T("Target") + ": " + self.Target
            if self.Profile:
                mailmessage += "\n" + T("Profile") + ": " + self.Profile or "-"
            mailmessage += "\n\n" + T("Thank you for your cooperation!")
            # also send a email to admin to let him know something went wrong
            if config.adminmail and mail.send(
                to=config.adminmail,
                subject="There is a system error with the build queue",
                message="Please inspect the build queue."
            ):
                logger.debug(
                    'Mail to Admin (%s) sucessfully sent.' %
                    config.adminmail)
            else:
                logger.error(
                    'There was an error sending mail to Admin (%s).' %
                    config.adminmail)
        else:
            mailsubject = T("Meshkit could not built your images")
            mailmessage = T(
                "I tried hard, but i was not able to build your images. " +
                "You will find a log of the build process at %s" %
                self.BinDirWeb + "/build.log."
            )
            mailmessage = T(
                "Your images could not be build because there was a system " +
                "error."
            )
            mailmessage += "\n\n" + \
                T("Remember! You tried to build an image with these settings:")
            if self.Community:
                mailmessage += "\n" + T("Community") + ": " + self.Community
            if self.Hostname:
                mailmessage += "\n" + T("Hostname") + ": " + self.Hostname
            if self.Location:
                mailmessage += "\n" + T("Location") + ": " + self.Location
            if self.Community == 'weimar':
                mailmessage += "\n" + T("Nodenumber") + ": " + self.nodenumber
            mailmessage += "\n" + T("Target") + ": " + self.Target
            if self.Profile:
                mailmessage += "\n" + T("Profile") + ": " + self.Profile
            mailmessage += "\n\n" + T("Thank you for your cooperation!")
        if self.Mail:
            if mail.send(
                to=self.Mail,
                subject=mailsubject,
                message=mailmessage
            ):
                logger.debug('Mail to %s sucessfully sent.' % self.Mail)
            else:
                logger.error(
                    ' + There was an error sending mail to %s.' %
                    self.Mail)
        else:
            logger.debug(
                "No email sent to user because no email address was given.")

    def createdirectories(self):
        """ We need a directory structure like this:
            OutputDir
                bin
                files
            If noconf is not True then we also need to create some subfolders
            inside files, i.e. etc/config, etc/init.d, etc/rc.d
            If creating the directory structure fails then return False and
            don't try to build the images.

        """
        status = 0
        if not mkdir_p(self.FilesDir):
            status = 1
        if not mkdir_p(self.BinDir):
            status = 1
        if self.Noconf is not True:
            if not mkdir_p(self.FilesDirInit):
                status = 1
            if not mkdir_p(self.FilesDirRc):
                status = 1
        if not mkdir_p(self.FilesDirConfig):
            status = 1
        if status == 1:
            return False
        else:
            return True

    def createconfig(self):
        """ Write uci config file for meshwizard to FilesDirConfig/meshwizard
        """

        def add_section(type, name):
            self.mkconfig += "config %s '%s'\n" % (type, name)

        def add_option(option, value):
            self.mkconfig += "\toption %s '%s'\n" % (option, value)

        def add_list(option, value):
            self.mkconfig += "\tlist %s '%s'\n" % (option, value)

        # section system
        add_section('system', 'system')
        add_option('hostname', self.Hostname)
        add_option('conloglevel', '8')
        add_option('cronloglevel', '9')
        add_option('latitude', self.Latitude)
        add_option('longitude', self.Longitude)
        add_option('location', self.Location)
        self.mkconfig += "\n"

        # ssh pubkeys
        if self.Pubkeys:
            keyslist = []
            k = self.Pubkeys.split("ssh-")
            for v in k:
                if v is not '':
                    keyslist.append("ssh-" + v)
            if len(keyslist) > 0:
                add_section('system', 'ssh')
                for k in keyslist:
                    k = k.strip("\n")
                    k = k.strip("\r")
                    add_list('pubkey', k)
                self.mkconfig += "\n"

        # section community
        add_section('public', 'community')
        add_option('name', self.Community)
        self.mkconfig += "\n"

        # section contact
        add_section('public', 'contact')
        add_option('nickname', self.Nickname)
        add_option('name', self.Name)
        add_list('homepage', self.Homepage)
        add_option('mail', self.Email)
        add_option('phone', self.Phone)
        add_option('note', self.Note)
        self.mkconfig += "\n"

        # section luci_main
        add_section('core', 'luci_main')
        add_option('mediaurlbase', "/luci-static/%s" % self.Theme)
        self.mkconfig += "\n"

        # section netconfig
        add_section('netconfig', 'netconfig')
        wifi_counter = 0
        for row_wifi in self.rows_wifi:
            counter = str(wifi_counter)
            add_option("IB_wifi%s_config" % counter, '1')

            if row_wifi.ipv4addr:
                add_option("IB_wifi%s_ip4addr" % counter, row_wifi.ipv4addr)

            if row_wifi.chan:
                add_option("IB_wifi%s_channel" % counter, row_wifi.chan)

            if row_wifi.dhcp:
                add_option(
                    "IB_wifi%s_dhcp" % counter,
                    row_wifi.dhcp and "1" or "0"
                )

            if row_wifi.dhcprange:
                add_option("IB_wifi%s_dhcprange" % counter, row_wifi.dhcprange)

            if row_wifi.vap:
                add_option(
                    "IB_wifi%s_vap" % counter, row_wifi.vap and "1" or "0"
                )

            if row_wifi.ipv6addr and self.Ipv6 and \
               self.Ipv6_config == 'static':
                add_option("IB_wifi%s_ip6addr" % counter, row_wifi.wifiipv6)

            if row_wifi.ipv6ra and (
                self.Ipv6 and (self.Ipv6_config == 'auto-ipv6-random' or
                               self.Ipv6_config == 'auto-ipv6-fromv4' or
                               self.Ipv6_config == 'static')):

                add_option(
                    "IB_wifi%s_ipv6ra" % counter,
                    row_wifi.ipv6ra and "1" or "0"
                )

            if self.Wanproto == 'olsr' and self.Wanipv4addr is not None:
                add_option('wan_config', '1')
                add_option('wan_proto', self.Wanproto)
                add_option('wan_ip4addr', self.Wanipv4addr)
                add_option('wan_netmask', self.Wannetmask)

            if self.Lanproto == 'olsr' and self.Lanipv4addr is not None:
                add_option('lan_config', '1')
                add_option('lan_proto', self.Lanproto)
                add_option('lan_dhcp', self.Landhcp)
                add_option('lan_dhcprange', self.Landhcprange)
                add_option('lan_ip4addr', self.Lanipv4addr)
                add_option('lan_netmask', self.Lannetmask)

        self.mkconfig += "\n"

        # section netconfig/wan for dhcp/static
        if (self.Wanproto == 'static' and self.Wanipv4addr is not None) or \
           self.Wanproto == 'dhcp':
            add_section('netconfig', 'wan')
            add_option('proto', self.Wanproto)

            if self.Wanproto == 'static':
                add_option('ip4addr', self.Wanipv4addr)
                add_option('netmask', self.Wannetmask)

                if self.Wanproto == 'static':
                    if self.Wangateway is not None:
                        add_option('gateway', self.Wangateway)

                    if self.Wandns is not None:
                        add_option('dns', self.Wandns)

            if self.Wan_allow_ssh:
                add_option('allowssh', '1')

            if self.Wan_allow_web:
                add_option('allowweb', '1')

            self.mkconfig += "\n"

        # section Lan - static
        if self.Lanproto == 'static' and self.Lanipv4addr and self.Lannetmask:
            add_section('netconfig', 'lan')
            add_option('proto', self.Lanproto)
            add_option('ip4addr', self.Lanipv4addr)
            add_option('netmask', self.Lannetmask)
            self.mkconfig += "\n"

        # Section ipv6
        add_section("defaults", "ipv6")
        add_option("enabled", self.Ipv6 and '1' or '0')
        if self.Ipv6 and self.Ipv6_config:
            add_option("config", self.Ipv6_config)
        self.mkconfig += "\n"

        # Section general
        add_section('general', 'general')
        add_option('sharenet', self.Sharenet)
        add_option('localrestrict', self.Localrestrict)
        self.mkconfig += "\n"

        # Section qos
        if self.Wan_qos == 1:
            add_section('qos', 'wan')
            add_option('down', self.Wan_qos_down)
            add_option('up', self.Wan_qos_up)
            self.mkconfig += "\n"

        # Write config to etc/config/meshwizard
        try:
            f = open(os.path.join(self.FilesDirConfig, 'meshwizard'), "w")
            try:
                f.write(self.mkconfig)
            finally:
                f.close()
        except IOError:
            logger.critical("Could not write config!")

        # Make meshwizard start at bootime
        filedir = os.path.join(request.folder, "private", "files")
        initfile = os.path.join(filedir, 'wizard.init')
        shutil.copy(initfile, os.path.join(self.FilesDirInit, 'wizard'))
        try:
            os.symlink(
                '/etc/init.d/wizard',
                os.path.join(
                    self.FilesDirRc,
                    'S99wizard'))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass

        # Write /etc/config/meshkit containing current configuration
        self.mkconfig = ''
        add_section('meshkit', 'update')
        if self.Profile:
            add_option('profile', self.Profile)

        add_option('target', self.Target)
        add_option('url', self.Url)
        self.mkconfig += "\n"

        # if a password_hash is available then write it to the meshkit config
        # too
        if self.password_hash:
            add_section('defaults', 'auth')
            add_option('password_hash', self.password_hash)
        try:
            f = open(os.path.join(self.FilesDirConfig, 'meshkit'), "w")
            try:
                f.write(self.mkconfig)
            finally:
                f.close()
        except IOError:
            logger.critical("Could not write /etc/config/meshkit!")

    def _build(self):
        status = 3
        out = ''
	settings_summary_json = {}
        logger.info(
            'Build started, ID: %s, Target: %s' %
            (self.Id, self.Target))
        if self.createdirectories():
            if not self.Noconf:
                self.createconfig()

            # write summary to output directory
            settings_summary_json = self.summary_json()
            self.summary_json_write(settings_summary_json)

            # handle files in <meshkit>/files
            mkfilesdir = os.path.join(request.folder, "files")
            if os.path.exists(mkfilesdir):
                cptree(mkfilesdir, self.FilesDir)
                logger.info(
                    'Copied files from %s to %s.' %
                    (mkfilesdir, self.FilesDir))

            # handle files/ in imagebuilder
            ibfilesdir = os.path.join(
                config.buildroots_dir,
                self.Target,
                "files")
            if os.path.exists(ibfilesdir):
                cptree(ibfilesdir, self.FilesDir)

            # handle community files (custom files uploaded by community)
            if config.communitysupport and config.communityfiles_dir:
                cfilesdir = os.path.join(
                    config.communityfiles_dir,
                    self.Community,
                    "files")
                logger.info(
                    'Copied files from %s to %s' %
                    (cfilesdir, self.FilesDir))
                if os.path.exists(cfilesdir):
                    cptree(cfilesdir, self.FilesDir)
                    if self.Community == 'weimar':
                        filesdir = "%s/etc/init.d/apply_profile.code" % \
                            self.FilesDir
                        with open(filesdir) as source:
                            data = source.read()
                            data1 = data.replace(
                                "#SIM_ARG1=\"olympia\"",
                                "SIM_ARG1=\"ffweimar\"")
                            data2 = data1.replace(
                                "#SIM_ARG2=\"adhoc\"",
                                "SIM_ARG2=\"hybrid\"")
                            logger.info("node number: " + self.nodenumber)
                            data3 = data2.replace(
                                "#SIM_ARG3=2",
                                "SIM_ARG3=" +
                                self.nodenumber)
                            source.seek(0)
                            source.write(data3)
                            source.close()

            # Handle uploaded archive
            if self.Upload:
                uploaded_file = os.path.join(
                    request.folder,
                    "uploads",
                    self.Upload)
                if os.access(uploaded_file, os.R_OK):
                    logger.info('extracting %s' % uploaded_file)
                    pu_ret = processupload.extract(
                        uploaded_file, self.FilesDir)
                    if pu_ret:
                        logger.warning(str(pu_ret))
                    # delete uploaded file
                    try:
                        os.remove(uploaded_file)
                        logger.debug('Deleted %s' % uploaded_file)
                    except:
                        logger.warning('Could not delete %s' % uploaded_file)

            if self.Profile:
                option_profile = "PROFILE=%s" % self.Profile
            else:
                option_profile = ""

            # Copy community profile
            if config.communitysupport and self.Community:
                communityprofile = os.path.join(
                    config.profiles,
                    'profile_' + self.Community)
                if not os.path.exists(communityprofile):
                    logger.warning(
                        'The communityfile %s does not exist!' %
                        communityprofile)
                else:
                    logger.debug(
                        'Copied %s to %s' %
                        (communityprofile, self.FilesDirConfig))
                    shutil.copy(communityprofile, self.FilesDirConfig)

            # check if there are any files to include in the image
            if len(os.listdir(self.FilesDir)) > 0:
                option_files = "FILES=%s" % self.FilesDir
            else:
                option_files = ""

            if self.Pkgs:
                option_pkgs = "PACKAGES=%s" % self.Pkgs
            else:
                option_pkgs = ""

            option_bin_dir = "BIN_DIR=%s" % self.BinDir

            path = os.path.join(config.buildroots_dir, self.Target)

            proc = subprocess.Popen(
                [
                    "make",
                    "image",
                    option_profile,
                    option_pkgs,
                    option_bin_dir,
                    option_files,
                ],
                cwd=path,
                stdout=subprocess.PIPE,
                shell=False,
                stderr=subprocess.STDOUT
            )

            out, _ = proc.communicate()
            ret = proc.returncode

            self.build_links_json()
            if ret != 0:
                if ret < 0:
                    logger.critical('make was killed by signal %s', str(ret))
                else:
                    logger.critical(
                        'make failed with return code %s',
                        str(ret))
                status = 2
            else:
                status = 0

        with open(self.BinDir + "/build.log", 'w') as f:
            f.write(out)

        return status, out, settings_summary_json


def set_failed():
    """ Search for builds, where the status in imageconf.status is
        queued or processing. Then check their status in scheduler_tasks. If
        the status is any of the failed statuses (FAILED, TIMEOUT,EXPIRED),
        then set the status in imageconf table to failed, too.
        This function should be run in regular intervals by the scheduler.
    """

    queued_or_processing = db(
        (db.imageconf.status == 1) | (db.imageconf.status == 4)
    ).select()

    logger.debug("Checking for failed builds")

    if len(queued_or_processing) < 1:
        logger.debug("Nothing to be done")
    else:
        for row in queued_or_processing:
            task_name = "build-%s" % str(row.id)
            logger.debug("Checking %s" % task_name)
            task = db_scheduler(
                db_scheduler.scheduler_task.task_name == task_name
            ).select().last()

            if task:
                if (
                    task.status == "FAILED" or
                    task.status == "TIMEOUT" or
                    task.status == "EXPIRED"
                ):

                    logger.warning("Setting task %s to failed" % task_name)
                    row.update_record(status=3)
                    db.commit()

                else:
                    logger.debug("Task still running")
            else:
                logger.warning(
                    "Task build-%s not found in scheduler_task" % str(row.id)
                )


def build(id):
    row = db.imageconf[id]
    if not row:
        logger.error("No row found for ID %s" % id)
        return 3

    build_start = datetime.now()

    # set status to processing
    row.update_record(status=4)
    db.commit()

    builder = BuildImages(row)
    ret, out, settings_summary_json = builder._build()

    logger.info("ret is: %s" % ret)
    if ret == 0:
        logger.info('Build finished, ID: %s ' % str(row.id))
        status = 0
    elif ret == 3:
        logger.error(
            'Build aborted due to previous errors, ID: %s' %
            str(row.id))
        status = 3
    else:
        logger.error('Build failed, ID: %s' % str(row.id))
        status = 2

    row.update_record(status=status)
    db.build_log.insert(
        id_build=row.id,
        status=status,
        output=out,
        settings=settings_summary_json,
        start=build_start,
        finished=datetime.now()
    )
    db.commit()
    builder.SendMail(status)

    # while it might seem like a good idea to return out (the complete output)
    # here: don't. It will prevent the job from completing, this probably is a
    # scheduler bug. See https://www.pythonanywhere.com/forums/topic/744/
    return ret


# start the scheduler
scheduler = Scheduler(
    db_scheduler,
    discard_results=True,
    heartbeat=settings.scheduler['heartbeat'],

)

# check if the set_failed task is there, else insert it
sched_failed = db_scheduler(
    db_scheduler.scheduler_task.task_name == "set_failed"
).select().first()

if not sched_failed:
    scheduler.queue_task(
        set_failed,
        task_name="set_failed",
        timeout=30,
        retry_failed=-1,
        period=60,
        repeats=0,
    )
