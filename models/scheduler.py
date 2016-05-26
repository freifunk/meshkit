#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defined statuses:
0: build ok
1: pending
2: error building image
3: syserror (e.g. could not create directories)
"""

import os
import errno
import subprocess
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json
import shutil
import mkutils
from gluon.scheduler import Scheduler
from gluon.fileutils import abspath
import processupload
import log

logger = log.initialize_logging(request.folder, __name__)


class BuildImages(object):

    """ This class is for configuring and building the images """

    def __init__(self, row=None):
        """ Init

            Args:
                row -- a web2py DAL row (object)
        """

        def _get(option):
            ret = None
            try:
                ret = row[option]
            except KeyError:
                logger.warning("Could not get option %s from the db" % option)
                pass
            return ret

        self.Lang = row.lang or 'en'
        T.force(self.Lang)
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
        self.Community = _get('community')
        self.Nodenumber = _get('nodenumber') or ''
        self.Wifimode = _get('wifimode') or 'hybrid' # kalua: adhoc, ap, hybrid (adhoc+ap)
        self.Ipschema = _get('ipschema') or 'ffweimar' # kalua: configures ip schema, based on node number
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

    def __getitem__(self, key):
        """ get items from self in an dict like notation """
        return self.__dict__[key]

    def _download_links_write(self):
        """ Write a file to static/ajax/<random number> containing all
            Download Links
        """
        files = []
        for filename in os.listdir(self.BinDir):
            size = os.path.getsize(os.path.join(self.BinDir, filename))
            files.append({'name': filename, 'size': size})
        r = json.dumps(sorted(files))

        # Write info to file
        static_ajax_file = os.path.join(
            abspath(request.folder), "static", "ajax", self.Rand
        )
        mkutils.write_file(static_ajax_file, str(r))

    def _summary_json(self):
        """ returns the current configuration as json
            Because wifi interface settings are stored in a seperate table
            they are added here too
        """
        self.rows_wifi = self.rows_wifi.as_dict()
        r = json.dumps(self.__dict__, indent=4)
        return r

    def _summary_json_write(self, jsondata):
        summary_file = os.path.join(self.BinDir, "summary.json")
        logger.debug('Writing summary to %s' % summary_file)
        mkutils.write_file(summary_file, jsondata)

    def _send_mail(self, status):
        mail_template = "mail/build_error"
        if self.Nickname:
            name = self.Nickname
        elif self.Name:
            name = self.Name
        else:
            name = T("fellow free networks enthusiast")

        mail_vars = dict(
            bin_dir=self.BinDirWeb,
            build_log="%s/build.log" % self.BinDirWeb,
            doc_url=config.documentation_url,
            name=name
        )

        settings_summary = dict()
        for o in ["Community", "Hostname", "Location", "Target", "Profile"]:
            if self[o]:
                settings_summary[T(o)] = self[o]

        if self.Community == 'weimar':
            settings_summary[T("Nodenumber")] = self.Nodenumber

        if status == 0:
            mail_template = "mail/build_success"
            mail_subject = T("Meshkit has built your images")
            mail_msg = T(
                'your images have been built and are ready for download'
            )
        else:
            mail_subject = T("Meshkit could not built your images")
            mail_msg = T(
                "I tried hard, but i was not able to build your images. " +
                "You might find a log of the build process here:"
            )
            if status == 3:
                # critical error. there will be no build_log
                mail_vars['build_log'] = None
                mail_msg = T(
                    'There was a critical system error. ' +
                    'The admin has been informed.'
                )

        # send mail to the user if we have an email address
        if self.Mail:
            mail_plaintext = response.render(
                "%s.txt" % mail_template,
                dict(
                    mail_vars=mail_vars,
                    settings_summary=settings_summary,
                    msg=mail_msg
                )
            )
            mail_html = response.render(
                "%s.html" % mail_template,
                dict(
                    mail_vars=mail_vars,
                    settings_summary=settings_summary,
                    msg=mail_msg
                )
            )
            if mail.send(
                to=self.Mail,
                subject=mail_subject,
                message=(mail_plaintext, mail_html)
            ):
                logger.debug('Mail to %s sucessfully sent.' % self.Mail)
            else:
                logger.error(
                    'There was an error sending mail to %s.' % self.Mail)
        else:
            logger.debug(
                "No email sent to user because no email address was given.")

        # in case of a system error also send an email to the admin
        if config.adminmail and status == 3:
            msg = T(
                "Please inspect the build queue, there was a critical system" +
                "error. Most likely Meshkit could not create needed " +
                "directories."
            )
            subject = T(
                'System error with the build queue'
            )
            if mail.send(to=config.adminmail, subject=subject, message=msg):
                logger.debug(
                    'Mail to Admin (%s) sucessfully sent.' %
                    config.adminmail
                )
            else:
                logger.error(
                    'There was an error sending mail to Admin (%s).' %
                    config.adminmail
                )

    def _createdirectories(self):
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
        if not mkutils.mkdir_p(self.FilesDir):
            status = 1
        if not mkutils.mkdir_p(self.BinDir):
            status = 1
        if self.Noconf is not True:
            if not mkutils.mkdir_p(self.FilesDirInit):
                status = 1
            if not mkutils.mkdir_p(self.FilesDirRc):
                status = 1
        if not mkutils.mkdir_p(self.FilesDirConfig):
            status = 1
        if status == 1:
            return False
        else:
            return True

    def _createconfig(self):
        """ Write uci config file for meshwizard and meshkit to
            FilesDirConfig/meshwizard
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
        if self.Pubkeys and len(self.Pubkeys) > 0:
            add_section('system', 'ssh')
            for k in self.Pubkeys:
                add_list('pubkey', k)
            self.mkconfig += "\n"

        # section community
        add_section('public', 'community')
        add_option('name', self.Community)
        if self.Community == 'weimar':
          add_option('nodenumber', self.Nodenumber)
          add_option('ipschema', self.Ipschema)
          add_option('wifimode', self.Wifimode)
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
        mw_conf_file = os.path.join(self.FilesDirConfig, 'meshwizard')
        mkutils.write_file(mw_conf_file, self.mkconfig)

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

        # write meshkit config file
        mk_conf_file = os.path.join(self.FilesDirConfig, 'meshkit')
        mkutils.write_file(mk_conf_file, self.mkconfig)

    def _build(self):
        status = 3
        out = ''
        settings_summary_json = {}
        logger.info(
            'Build started, ID: %s, Target: %s' %
            (self.Id, self.Target))
        if self._createdirectories():
            if not self.Noconf:
                self._createconfig()

            # write summary to output directory
            settings_summary_json = self._summary_json()
            self._summary_json_write(settings_summary_json)

            # handle files in <meshkit>/files
            mkfilesdir = os.path.join(request.folder, "files")
            if os.path.exists(mkfilesdir):
                mkutils.cptree(mkfilesdir, self.FilesDir)
                logger.info(
                    'Copied files from %s to %s.' %
                    (mkfilesdir, self.FilesDir))

            # handle files/ in imagebuilder
            ibfilesdir = os.path.join(
                config.buildroots_dir,
                self.Target,
                "files")
            if os.path.exists(ibfilesdir):
                mkutils.cptree(ibfilesdir, self.FilesDir)

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
                    mkutils.cptree(cfilesdir, self.FilesDir)

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

            # construct the commandline
            path = os.path.join(config.buildroots_dir, self.Target)
            cmdline = ["make", "image"]
            if len(self.Profile) > 0:
                cmdline.append("PROFILE=%s" % self.Profile)
            if self.Pkgs:
                cmdline.append("PACKAGES=%s" % self.Pkgs)
            if len(os.listdir(self.FilesDir)) > 0:
                cmdline.append("FILES=%s" % self.FilesDir)
            if len(self.BinDir) > 0:
                cmdline.append("BIN_DIR=%s" % self.BinDir)

            proc = subprocess.Popen(
                cmdline,
                cwd=path,
                stdout=subprocess.PIPE,
                shell=False,
                stderr=subprocess.STDOUT
            )

            out, _ = proc.communicate()
            ret = proc.returncode

            self._download_links_write()
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

            # write build log
            build_log_file = os.path.join(self.BinDir, "build.log")
            mkutils.write_file(build_log_file, out)

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
        community=row.community,
        target=row.target,
        profile=row.profile,
        status=status,
        output=out,
        settings=settings_summary_json,
        start=build_start,
        finished=datetime.now()
    )
    db.commit()
    builder._send_mail(status)

    # while it might seem like a good idea to return out (the complete output)
    # here: don't. It will prevent the job from completing, this probably is a
    # scheduler bug. See https://www.pythonanywhere.com/forums/topic/744/
    return ret


def clean_imagedir():
    # cleans images that are older than config.keep_images hours
    from clean_imagedir import cleanup
    ret = cleanup()
    return ret


# start the scheduler
scheduler = Scheduler(
    db_scheduler,
    discard_results=True,
    heartbeat=settings.scheduler['heartbeat'],
)

# check if the set_failed task is there, else insert it
sched_failed = cache.ram(
    'sched_failed',
    lambda: db_scheduler(
        db_scheduler.scheduler_task.task_name == "set_failed"
    ).select().first(),
    time_expire=60
)
if not sched_failed:
    scheduler.queue_task(
        set_failed,
        task_name="set_failed",
        timeout=30,
        retry_failed=-1,
        period=60,
        repeats=0,
    )

# check if the clean_imagedir task is there, else insert it
sched_clean_imagedir = cache.ram(
    'sched_clean_imagedir',
    lambda: db_scheduler(
        db_scheduler.scheduler_task.task_name == "clean_imagedir"
    ).select().first(),
    time_expire=60
)
if not sched_clean_imagedir:
    scheduler.queue_task(
        clean_imagedir,
        task_name="clean_imagedir",
        timeout=300,
        retry_failed=-1,
        period=7200,
        repeats=0,
    )
