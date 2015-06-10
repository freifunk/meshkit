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
try:
    import json
except ImportError:
    import simplejson as json
import shutil
sys.path.append(os.path.join(request.folder, "private", "modules"))
import mkutils
import processupload
import log
import distutils
from distutils.dir_util import copy_tree


logger = log.initialize_logging(request.folder, 'build_queue')

def mkdir_p(path):
    try:
        os.makedirs(path)
        return True
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            logger.critical("Error: Could not create directory %s" % path)
            return False

def cptree(src,dst):
    try:
        ct = copy_tree(src, dst, preserve_symlinks=0)
        logger.debug('Copied %s to %s' % (src, dst) ) 
    except distutils.errors.DistutilsFileError, e:
        logger.warning('Source directory %s does not exist. %s' % (src, str(e)) )
    except IOError, e:
        logger.error('Could not create/write to directory %s. Check permissions.' % dst)


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
                    
        self.Id = _get('id')
        self.Rand = _get('rand')
        self.Target = _get('target')
        self.Profile = _get('profile')
        self.Pubkeys = _get('pubkeys')
        self.password_hash = _get('password_hash')
        self.Pkgs = _get('pkgs') or ''
        self.rows_wifi = db(db.wifi_interfaces.id_build == self.Id).select()
        self.Noconf = _get('noconf')
        if not self.Noconf == True:
            self.Pkgs += ' meshwizard'
        for row_wifi in self.rows_wifi:
            if row_wifi.vap == True:
                self.Pkgs += ' hostapd-mini'
                break
        self.Upload = _get('upload')
        self.Mail = _get('mail') # this is the mailaddress used to send mails after build
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
        self.Email = _get('email') or '' # this is the email address for contact information
        self.Phone = _get('phone') or ''
        self.Note = _get('note') or ''
        self.Theme = _get('theme')
        if self.Theme:
            self.Theme = self.Theme.replace("luci-theme-", "") or 'freifunk-generic'
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
            files.append({ 'name': filename, 'size': size })
        r = json.dumps(sorted(files))

        # Write info to file
        try:
            f = open(os.path.join(request.folder, "static", "ajax", self.Rand), "w")
            try:
                f.write(str(r))
            finally:
                f.close()
        except IOError:
            pass
            
    def summary_json(self):
        self.rows_wifi = self.rows_wifi.as_dict()
        r = json.dumps(self.__dict__, indent=4)
        summaryfile = os.path.join(self.BinDir, "summary.json")
        logger.debug('Writing summary to %s' % summaryfile)
        
        #write summary to bin directory
        try:
            f = open(summaryfile, "w")
            try:
                f.write(str(r))
            finally:
                f.close()
        except IOError:
               pass

    def SendMail(self, status):
        if status == 0:
            mailsubject = T("Meshkit has built your images")
            mailmessage = T("Your images were built sucessfully, download them at ") + self.BinDirWeb + "."
            mailmessage += "\n\n" + T("Remember! You built this image with these settings:")
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
            mailmessage = T("Your images could not be build because there was a system error.")
            mailmessage += "\n\n" + T("Remember! You tried to build an image with these settings:")
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
                message="Please inspect the build queue, something is fishy there."
                ):
                logger.debug('Mail to Admin (%s) sucessfully sent.' % config.adminmail)
            else:
                logger.error('There was an error sending mail to Admin (%s).' % config.adminmail)
        else:
            mailsubject = T("Meshkit could not built your images")
            mailmessage = T("I tried hard, but i was not able to build your images. You will find a log of the build process at %s" % self.BinDirWeb + "/build.log.")
            mailmessage = T("Your images could not be build because there was a system error.")
            mailmessage += "\n\n" + T("Remember! You tried to build an image with these settings:")
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
                logger.error(' + There was an error sending mail to %s.' % self.Mail)
        else:
            logger.debug("No email sent to user because no email address was given.")


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
        if mkdir_p(self.FilesDir) == False:
            status = 1
        if mkdir_p(self.BinDir) == False:
            status = 1
        if self.Noconf is not True:
            if mkdir_p(self.FilesDirInit) == False:
                status = 1
            if mkdir_p(self.FilesDirRc) == False:
                status = 1
        if mkdir_p(self.FilesDirConfig) == False:
            status = 1
        if status == 1:
            return False
        else:
            return True

    def createconfig(self):
        """ Write uci config file for meshwizard to FilesDirConfig/meshwizard """

        def add_section(type, name):
            return "config '" + type + "' '" + name + "'\n"
        def add_option(option, value):
            return "\toption '" + option + "' '" + value + "'\n"

        # section system
        config = "config 'system' 'system'\n"
        config += "\toption 'hostname' '" + self.Hostname + "'\n"
        config += "\toption 'conloglevel' '8'\n"
        config += "\toption 'cronloglevel' '9'\n"
        config += "\toption 'latitude' '" + self.Latitude + "'\n"
        config += "\toption 'longitude' '" + self.Longitude + "'\n"
        config += "\toption 'location' '" + self.Location + "'\n"
        config += "\n"

        #ssh pubkeys
        if self.Pubkeys:
            keyslist = []
            k = self.Pubkeys.split("ssh-")
            for v in k:
                if v is not '':
                    keyslist.append("ssh-" + v)
            if len(keyslist) > 0:
                config += "config 'system' 'ssh'\n"
                for k in keyslist:
                    k=k.strip("\n")
                    k=k.strip("\r")
                    config += "\tlist 'pubkey' '" + k + "'\n"
                config += "\n"

        # section community
        config += "config 'public' 'community'\n"
        config += "\toption 'name' '" + self.Community + "'\n"
        config += "\n"

        # section contact
        config += "config 'public' 'contact'\n"
        config += "\toption 'nickname' '" + self.Nickname + "'\n"
        config += "\toption 'name' '" + self.Name + "'\n"
        config += "\toption 'homepage' '" + self.Homepage + "'\n"
        config += "\toption 'mail' '" + self.Email + "'\n"
        config += "\toption 'phone' '" + self.Phone + "'\n"
        config += "\toption 'note' '" + self.Note + "'\n"
        config += "\n"

        # section luci_main
        config += "config 'core' 'luci_main'\n"
        config += "\toption 'mediaurlbase' '/luci-static/" + self.Theme + "'\n"
        config += "\n"

        # section netconfig
        config += "config 'netconfig' 'netconfig'\n"
        
        wifi_counter = 0
        for row_wifi in self.rows_wifi:
            config += "\toption 'IB_wifi" + str(wifi_counter) + "_config' '1'\n"
            if row_wifi.ipv4addr:
                config += "\toption 'IB_wifi" + str(wifi_counter) + "_ip4addr' '" + row_wifi.ipv4addr + "'\n"
            if row_wifi.chan:
                config += "\toption 'IB_wifi" + str(wifi_counter) + "_channel' '" + str(row_wifi.chan) + "'\n"
            if row_wifi.dhcp:
                config += "\toption 'IB_wifi" + str(wifi_counter) + "_dhcp' '" + (row_wifi.dhcp and "1" or "0") + "'\n"
            if row_wifi.dhcprange:
                config += "\toption 'IB_wifi" + str(wifi_counter) + "_dhcprange' '" + row_wifi.dhcprange + "'\n"
            if row_wifi.vap:
                config += "\toption 'IB_wifi" + str(wifi_counter) + "_vap' '" + (row_wifi.vap and "1" or "0") + "'\n"
            if row_wifi.ipv6addr and self.Ipv6 and self.Ipv6_config == 'static' and wifiipv6:
                config += "\toption 'IB_wifi" + str(wifi_counter) + "_ip6addr' '" + row_wifi.wifiipv6 + "'\n"
            if row_wifi.ipv6ra and (
                self.Ipv6 and (self.Ipv6_config == 'auto-ipv6-random' or
                self.Ipv6_config == 'auto-ipv6-fromv4' or
                self.Ipv6_config == 'static')):
                config += "\toption 'IB_wifi" +  str(wifi_counter) + "_ipv6ra' '" + (row_wifi.ipv6ra and "1" or "0") + "'\n"
                
            if self.Wanproto == 'olsr' and self.Wanipv4addr is not None:
                config += "\toption 'wan_config' '1'\n"
                config += "\toption 'wan_proto' '" + self.Wanproto + "'\n"
                config += "\toption 'wan_ip4addr' '" + self.Wanipv4addr + "'\n"
                config += "\toption 'wan_netmask' '" + self.Wannetmask + "'\n"

            if self.Lanproto == 'olsr' and self.Lanipv4addr is not None:
                config += "\toption 'lan_config' '1'\n"
                config += "\toption 'lan_proto' '" + self.Lanproto + "'\n"
                config += "\toption 'lan_dhcp' '" + self.Landhcp + "'\n"
                config += "\toption 'lan_dhcprange' '" + self.Landhcprange + "'\n"
                config += "\toption 'lan_ip4addr' '" + self.Lanipv4addr + "'\n"
                config += "\toption 'lan_netmask' '" + self.Lannetmask + "'\n"
        config += "\n"

        # section netconfig/wan for dhcp/static
        if (self.Wanproto == 'static' and self.Wanipv4addr is not None) or self.Wanproto == 'dhcp':
            config += "config 'netconfig' 'wan'\n"
            config += "\toption 'proto' '" + self.Wanproto + "'\n"

            if self.Wanproto == 'static':
                config += "\toption 'ip4addr' '" + self.Wanipv4addr + "'\n"
                config += "\toption 'netmask' '" + self.Wannetmask + "'\n"
                if self.Wanproto == 'static':
                    if self.Wangateway is not None:
                        config += "\toption 'gateway' '" + self.Wangateway + "'\n"
                    if self.Wandns is not None:
                        config += "\toption 'dns' '" + self.Wandns + "'\n"

            if self.Wan_allow_ssh == True:
                config += "\toption 'allowssh' '1'\n"
            if self.Wan_allow_web == True:
                config += "\toption 'allowweb' '1'\n"
            config += "\n"

        # section Lan - static
        if self.Lanproto == 'static' and self.Lanipv4addr and self.Lannetmask:
                config += "config 'netconfig' 'lan'\n"
                config += "\toption 'proto' '" + self.Lanproto + "'\n"
                config += "\toption 'ip4addr' '" + self.Lanipv4addr + "'\n"
                config += "\toption 'netmask' '" + self.Lannetmask + "'\n"
                config += "\n"

        # Section ipv6
        config += add_section("defaults", "ipv6")
        config += add_option("enabled", self.Ipv6 and '1' or '0')
        if self.Ipv6 and self.Ipv6_config:
            config += add_option("config", self.Ipv6_config)
        config += "\n"

        # Section general
        config += "config 'general' 'general'\n"
        config += "\toption 'sharenet' '"+ self.Sharenet + "'\n"
        config += "\toption 'localrestrict' '" + self.Localrestrict + "'\n"
        config += "\n"
        
        # Section qos
        if self.Wan_qos == 1:
            config += "config 'qos' 'wan'\n"
            config += "\toption 'down' '"+ str(self.Wan_qos_down) + "'\n"
            config += "\toption 'up' '"+ str(self.Wan_qos_up) + "'\n"
            config += "\n"

        # Write config to etc/config/meshwizard
        try:
            f = open(os.path.join(self.FilesDirConfig, 'meshwizard'), "w")
            try:
                f.write(config)
            finally:
                f.close()
        except IOError:
            logger.critical("Could not write config!")

        # Make meshwizard start at bootime
        filedir = os.path.join(request.folder, "private", "files")
        initfile = os.path.join(filedir, 'wizard.init')
        shutil.copy(initfile, os.path.join(self.FilesDirInit, 'wizard'))
        try:
            os.symlink('/etc/init.d/wizard', os.path.join(self.FilesDirRc, 'S99wizard'))
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass

        # Write /etc/config/meshkit containing current configuration
        config_meshkit = add_section('meshkit', 'update')
        if self.Profile:
            config_meshkit += add_option('profile', self.Profile)
        config_meshkit += add_option('target', self.Target)
        config_meshkit += add_option('url', self.Url)
        
        # if a password_hash is available then write it to the meshkit config too
        if self.password_hash:
            config_meshkit += "\n"
            config_meshkit += add_section('defaults', 'auth')
            config_meshkit += add_option('password_hash', self.password_hash)
        try:
            f = open(os.path.join(self.FilesDirConfig, 'meshkit'), "w")
            try:
                f.write(config_meshkit)
            finally:
                f.close()
        except IOError:
            logger.critical("Could not write /etc/config/meshkit!")


    def build(self):
        logger.info('Build started, ID: %s, Target: %s' % (self.Id, self.Target) )
        if builder.createdirectories():
            if not self.Noconf == True:
                builder.createconfig()
            
            #write summary to output directory
            builder.summary_json()

            #handle files in <meshkit>/files
            mkfilesdir = os.path.join(request.folder, "files")
            if os.path.exists(mkfilesdir):
                cptree(mkfilesdir, self.FilesDir) 
                logger.info('Copied files from %s to %s.' % (mkfilesdir, self.FilesDir) )


            # handle files/ in imagebuilder
            ibfilesdir = os.path.join(config.buildroots_dir, self.Target, "files")
            if os.path.exists(ibfilesdir):
                cptree(ibfilesdir, self.FilesDir) 
            
            # handle community files (custom files uploaded by community)
            if config.communitysupport and config.communityfiles_dir:
                cfilesdir = os.path.join(config.communityfiles_dir, self.Community, "files")
                logger.info('Copied files from %s to %s' % (cfilesdir, self.FilesDir) )
                if os.path.exists(cfilesdir):
                    cptree(cfilesdir, self.FilesDir)
                    if self.Community == 'weimar':
                        with open(self.FilesDir + "/etc/init.d/apply_profile.code", "r+") as source:
                            data = source.read()
                            data1 = data.replace("#SIM_ARG1=\"olympia\"", "SIM_ARG1=\"ffweimar\"")
                            data2 = data1.replace("#SIM_ARG2=\"adhoc\"", "SIM_ARG2=\"hybrid\"")
                            logger.info("node number: " + self.nodenumber)
                            data3 = data2.replace ("#SIM_ARG3=2", "SIM_ARG3=" + self.nodenumber)
			    source.seek(0)
			    source.write(data3)
			    source.close()
                    
            # Handle uploaded archive
            if self.Upload:
                uploaded_file = os.path.join(request.folder, "uploads", self.Upload)
                if os.access(uploaded_file, os.R_OK):
                    logger.info('extracting %s' % uploaded_file)
                    pu_ret = processupload.extract(uploaded_file, self.FilesDir)
                    if pu_ret:
                        logger.warning(str(pu_ret))
                    # delete uploaded file
                    try:
                        os.remove(uploaded_file)
                        logger.debug('Deleted %s' % uploaded_file)
                    except:
                        logger.warning('Could not delete %s' % uploaded_file)
                        
            out = open(self.BinDir + "/build.log", "w")
            if self.Profile:
                option_profile = "PROFILE='" + self.Profile + "'"
            else:
                option_profile = ""

            # Copy community profile
            if config.communitysupport and self.Community:
                communityprofile = os.path.join(config.profiles, 'profile_' + self.Community)
                if not os.path.exists(communityprofile):
                    logger.warning('The communityfile %s does not exist!' % communityprofile)
                else:
                    logger.debug('Copied %s to %s' % (communityprofile, self.FilesDirConfig) )
                    shutil.copy(communityprofile, self.FilesDirConfig)

            # check if there are any files to include in the image
            if len(os.listdir(self.FilesDir)) > 0:
                option_files = " FILES='" + self.FilesDir + "'"
            else:
                option_files=""

            if self.Pkgs:
                option_pkgs = " PACKAGES='" + self.Pkgs + "'"
            else:
                option_pkgs = " "

            cmd = "cd " + config.buildroots_dir + "/" + self.Target + "; make image " + option_profile + option_pkgs + " BIN_DIR='" + self.BinDir + "' " + option_files
            ret = subprocess.call([cmd, ""], stdout=out, stderr=subprocess.STDOUT, shell=True)
            builder.build_links_json()
            if ret != 0:
                if ret < 0:
                    logger.critical('make was killed by signal %s', str(ret))
                else:
                    logger.critical('make failed with return code %s', str(ret))
                return 2
            else:
                return 0
        else:
            return 3

# Do not start if build_queue is already running
if mkutils.check_pid(os.path.join(request.folder, "private", "buildqueue.pid"), os.getpid()):
    logger.warning('Buildqueue is already running, not starting it again.')
else:
    try:
        logger.info('Starting buildqueue')
        while True:
            try:
                rows = db(db.imageconf.status=='1').select()
            except KeyError:
                rows = []

            for row in rows:
                builder = BuildImages(row)
                ret = builder.build()
                if ret == 0:
                    logger.info('Build finished, ID: %s ' % str(row.id))
                    status = 0
                elif ret == 3:
                    logger.error('Build aborted due to previous errors, ID: %s' % str(row.id))
                    status = 3
                else:
                    logger.error('Build failed, ID: %s' % str(row.id))
                    status = 2
                builder.SendMail(status)
                row.update_record(status=status)
                db.commit()
            time.sleep(30)
    except KeyboardInterrupt as e:
        logger.info('Buildqueue stopped by keyboard interrupt.')
        raise
