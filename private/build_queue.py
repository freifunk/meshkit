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
            logger.critical("Error: Could not create directory " + path)
            return False

def cptree(src,dst):
    try:
        copy_tree(src, dst, preserve_symlinks=0)
        logger.debug('Copied "' + src + '" to "' + dst +'"')
    except distutils.errors.DistutilsFileError, e:
        logger.warning("Source directory " + src + " does not exist.")
    except IOError, e:
        logger.error("Could not create/write to directory " + dst + ". Check permissions.")


class BuildImages(object):

    """
    This class is for configuring and building the images
    
    Args:
        config_path: Path where the uci config files are stored
        config_file: filename of the config file
    """

    def __init__(self, id=None, rand=None, target=None, profile=None,
                 pkgs=None, upload=None, mail=None, noconf=True, pubkeys=None,
                 hostname=None, latitude=None, longitude=None,
                 ipv6=False, ipv6_config=None,
                 location=None, community=None, nickname=None,
                 name=None, email=None, phone=None, note=None,
                 theme=None,
                 wifi0ipv4addr=None, wifi0chan=None, wifi0dhcp=None, wifi0dhcprange=None,
                 wifi0vap=False, wifi0ipv6addr=None, wifi0ipv6ra=False,
                 wifi1ipv4addr=None, wifi1chan=None, wifi1dhcp=None, wifi1dhcprange=None,
                 wifi1vap=False, wifi1ipv6addr=None, wifi1ipv6ra=False,
                 wifi2ipv4addr=None, wifi2chan=None, wifi2dhcp=None, wifi2dhcprange=None,
                 wifi2vap=False, wifi2ipv6addr=None, wifi2ipv6ra=False,
                 lanproto=None, lanipv4addr=None, lannetmask=None, landhcp=None,
                 landhcprange=None, wanproto=None, wanipv4addr=None, wannetmask=None,
                 wangateway=None, wandns=None, wan_allow_ssh=None, wan_allow_web=None,
                 localrestrict=None, sharenet=None, url=None
                 ):
        self.Id = str(id)
        self.Rand = rand
        self.Target = target
        self.Profile = profile
        self.Pubkeys = pubkeys
        self.Pkgs = pkgs or ''
        if not noconf == True:
            self.Pkgs += ' meshwizard'
        if wifi0vap == True or wifi1vap == True or wifi2vap == True:
            self.Pkgs += ' hostapd-mini'
        self.Upload = upload
        self.Mail = mail # this is the mailaddress used to send mails after build
        self.Noconf = noconf
        self.Latitude = latitude or ''
        self.Longitude = longitude or ''
        self.Ipv6 = ipv6
        self.Ipv6_config = ipv6_config
        self.Location = location or ''
        self.Community = community or 'augsburg'
        self.Nickname = nickname or ''
        self.Name = name or ''
        self.Email = email or '' # this is the email address for contact information
        self.Phone = phone or ''
        self.Note = note or ''
        if theme:
            self.Theme = theme.replace("luci-theme-", "") or 'freifunk-generic'
	else:
            self.Theme = 'freifunk-generic'
        self.Wifi0ipv4addr = wifi0ipv4addr
        self.Wifi0ipv6addr = wifi0ipv6addr
        self.Wifi0chan = wifi0chan or "1"
        self.Wifi0dhcp = wifi0dhcp and "1" or "0"
        self.Wifi0ipv6ra = wifi0ipv6ra and "1" or "0"
        self.Wifi0vap = wifi0vap and "1" or "0"
        self.Wifi0dhcprange = wifi0dhcprange or ''
        self.Wifi1ipv4addr = wifi1ipv4addr
        self.Wifi1ipv6addr = wifi1ipv6addr
        self.Wifi1chan = wifi1chan or "1"
        self.Wifi1dhcp = wifi1dhcp and "1" or "0"
        self.Wifi1ipv6ra = wifi1ipv6ra and "1" or "0"
        self.Wifi1vap = wifi1vap and "1" or "0"
        self.Wifi1dhcprange = wifi1dhcprange or ''
        self.Wifi2ipv4addr = wifi2ipv4addr
        self.Wifi2ipv6addr = wifi2ipv6addr
        self.Wifi2chan = wifi2chan or "1"
        self.Wifi2dhcp = wifi2dhcp and "1" or "0"
        self.Wifi2ipv6ra = wifi2ipv6ra and "1" or "0"
        self.Wifi2vap = wifi2vap and "1" or "0"
        self.Wifi2dhcprange = wifi2dhcprange or ''
        self.Lanproto = lanproto or 'dhcp'
        self.Lanipv4addr = lanipv4addr
        self.Lannetmask = lannetmask or '255.255.255.0'
        self.Landhcp = landhcp and "1" or "0"
        self.Landhcprange = landhcprange or ''
        self.Wanproto = wanproto or 'static'
        self.Wanipv4addr = wanipv4addr
        self.Wannetmask = wannetmask or '255.255.255.0'
        self.Wangateway = wangateway or ''
        self.Wandns = wandns or ''
        self.Wan_allow_ssh = wan_allow_ssh and 1 or 0
        self.Wan_allow_web = wan_allow_web and 1 or 0
        self.Localrestrict = localrestrict and "1" or "0"
        self.Sharenet = sharenet and "1" or "0"
        self.Hostname = hostname
        if not self.Hostname:
            if self.Wifi0ipv4addr:
	        self.Hostname = self.Wifi0ipv4addr.replace(".", "-")
            elif self.Wifi1ipv4addr:
                self.Hostname = self.Wifi1ipv4addr.replace(".", "-")
            elif self.Wifi2ipv4addr:
                self.Hostname = self.Wifi12pv4addr.replace(".", "-")
            else:
                self.Hostname = "OpenWrt"
 
        self.OutputDir = os.path.join(config.images_output_dir, self.Rand)
        self.FilesDir = os.path.join(self.OutputDir, "files")
        self.FilesDirInit = os.path.join(self.FilesDir, 'etc', 'init.d')
        self.FilesDirRc = os.path.join(self.FilesDir, 'etc', 'rc.d')
        self.FilesDirConfig = os.path.join(self.FilesDir, 'etc', 'config')
        self.BinDir = os.path.join(self.OutputDir, "bin")
        self.OutputDirWeb = os.path.join(config.images_web_dir, self.Rand)
        self.BinDirWeb = os.path.join(self.OutputDirWeb, "bin")
        self.Url = url or ''


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

    def SendMail(self, status):
        if status == 0:
            mailsubject = T("Meshkit has built your images")
            mailmessage = T("Your images were built sucessfully, download them at ") + self.BinDirWeb + "."
        elif status == 3:
            mailsubject = T("Meshkit could not built your images")
            mailmessage = T("Your images could not be build because there was a system error.")
            # also send a email to admin to let him know something went wrong
            if config.adminmail and mail.send(   
                to=config.adminmail,
                subject="There is a system error with the build queue",
                message="please inspect the build queue, something is fishy there."
                ):
                logger.debug("Mail to Admin (" + config.adminmail + ") sucessfully sent.")
            else:
                logger.error("There was an error sending mail to Admin (" + config.adminmail + ").")
        else:
            mailsubject = T("Meshkit could not built your images")
            mailmessage = T("I tried hard, but i was not able to build your images. You will find a log of the build process at ") + self.BinDirWeb + "/build.log."
        if self.Mail:
            if mail.send(   
                to=self.Mail,
                subject=mailsubject,
                message=mailmessage
                ):
                logger.debug("Mail to " + self.Mail + " sucessfully sent.")
            else:
                logger.error(" + There was an error sending mail to " + self.Mail + ".")
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
        for i in range(0,3): # configure up to 3 wifi interfaces
            i = str(i)
            try:
                wifiipv4 = eval('self.Wifi' + i + 'ipv4addr')
                wifiipv6 = eval('self.Wifi' + i + 'ipv6addr')
                ra = eval('self.Wifi' +  i + 'ipv6ra')
                vap = eval('self.Wifi' +  i + 'vap')
                if wifiipv4 is not None:
                    chan = eval('self.Wifi' + i + 'chan')
                    dhcp = eval('self.Wifi' +  i + 'dhcp')
                    dhcprange = eval('self.Wifi' + i + 'dhcprange')
                    config += "\toption 'IB_wifi" + i + "_config' '1'\n"
                    config += "\toption 'IB_wifi" + i + "_ip4addr' '" + wifiipv4 + "'\n"
                    config += "\toption 'IB_wifi" + i + "_channel' '" + chan + "'\n"
                    config += "\toption 'IB_wifi" + i + "_dhcp' '" + dhcp + "'\n"
                    config += "\toption 'IB_wifi" + i + "_dhcprange' '" + dhcprange + "'\n"
                    config += "\toption 'IB_wifi" + i + "_vap' '" + vap + "'\n"

                    if self.Ipv6 and self.Ipv6_config == 'static' and wifiipv6:
                        config += "\toption 'IB_wifi" + i + "_ip6addr' '" + wifiipv6 + "'\n"
                    if self.Ipv6 and (self.Ipv6_config == 'auto-ipv6-random' or
                                      self.Ipv6_config == 'auto-ipv6-fromv4' or
                                      self.Ipv6_config == 'static'):
                        config += "\toption 'IB_wifi" + i + "_ipv6ra' '" + ra + "'\n"
            except NameError:
                pass

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
        if self.Lanproto == 'static':
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
	#config_meshkit = 'config "meshkit" "update"\n'
        #for o in self.__dict__:
        #    v = "{key}\t'{value}'".format(key=o, value=self.__dict__[o])
        #    config_meshkit += '\toption' + '\t' + v + '\n'

        config_meshkit = add_section('meshkit', 'update')
        if self.Profile:
            config_meshkit += add_option('profile', self.Profile)
        config_meshkit += add_option('target', self.Target)
        config_meshkit += add_option('url', self.Url)

        try:
            f = open(os.path.join(self.FilesDirConfig, 'meshkit'), "w")
            try:
                f.write(config_meshkit)
            finally:
                f.close()
        except IOError:
            logger.critical("Could not write /etc/config/meshkit!")


    

    def build(self):
        logger.info("Build started, ID: " + self.Id + ", target: " + self.Target)
        if builder.createdirectories():
            if not self.Noconf == True:
                builder.createconfig()

            #handle files in <meshkit>/files
            mkfilesdir = os.path.join(request.folder, "files")
            if os.path.exists(mkfilesdir):
                cptree(mkfilesdir, self.FilesDir) 
                logger.info("Copied files from " + mkfilesdir)


            # handle files/ in imagebuilder
            ibfilesdir = os.path.join(config.buildroots_dir, self.Target, "files")
            if os.path.exists(ibfilesdir):
                cptree(ibfilesdir, self.FilesDir) 

            # handle community files (custom files uploaded by community)
            if config.communitysupport and config.communityfiles_dir:
		cfilesdir = os.path.join(config.communityfiles_dir, self.Community, "files")
                if os.path.exists(cfilesdir):
                    cptree(cfilesdir, self.FilesDir)
                    
            # Handle uploaded archive
            if self.Upload:
                uploaded_file = os.path.join(request.folder, "uploads", self.Upload)
                if os.access(uploaded_file, os.R_OK):
                    logger.info("extracting " + uploaded_file)
                    pu_ret = processupload.extract(uploaded_file, self.FilesDir)
                    if pu_ret:
                        logger.warning(pu_ret)
                    # delete uploaded file
                    try:
                        os.remove(uploaded_file)
                        logger.debug("Deleted " + uploaded_file)
                    except:
                        logger.warning("Could not delete " + uploaded_file)

            out = open(self.BinDir + "/build.log", "w")
            if self.Profile:
                option_profile = "PROFILE='" + self.Profile + "'"
            else:
                option_profile = ""

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
                    logger.critical("make was killed by signal", -ret)
                else:
                    logger.critical("make failed with return code", ret)
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
                builder = BuildImages(id=row.id, rand=row.rand, target=row.target, mail=row.mail,
                                      profile=row.profile, pkgs=row.packages, upload=row.upload,
                                      noconf=row.noconf, pubkeys=row.pubkeys, hostname=row.hostname,
                                      latitude=row.latitude, longitude=row.longitude, location=row.location,
                                      ipv6=row.ipv6, ipv6_config=row.ipv6_config,
                                      community=row.community, nickname=row.nickname, name=row.name,
                                      email=row.email, phone=row.phone, note=row.note, theme=row.theme,
                                      wifi0ipv4addr=row.wifi0ipv4addr, wifi0chan=row.wifi0chan,
                                      wifi0ipv6addr=row.wifi0ipv6addr, wifi0ipv6ra=row.wifi0ipv6ra,
                                      wifi0dhcp=row.wifi0dhcp, wifi0vap=row.wifi0vap, wifi0dhcprange=row.wifi0dhcprange,
                                      wifi1ipv4addr=row.wifi1ipv4addr, wifi1chan=row.wifi1chan,
                                      wifi1ipv6addr=row.wifi1ipv6addr, wifi1ipv6ra=row.wifi1ipv6ra,
                                      wifi1dhcp=row.wifi1dhcp, wifi1vap=row.wifi1vap, wifi1dhcprange=row.wifi1dhcprange,
                                      wifi2ipv4addr=row.wifi2ipv4addr, wifi2chan=row.wifi2chan,
                                      wifi2ipv6addr=row.wifi2ipv6addr, wifi2ipv6ra=row.wifi2ipv6ra,
                                      wifi2dhcp=row.wifi2dhcp, wifi2vap=row.wifi2vap,wifi2dhcprange=row.wifi2dhcprange,
                                      lanproto=row.lanproto, lanipv4addr=row.lanipv4addr,
                                      lannetmask=row.lannetmask, landhcp=row.landhcp,
                                      landhcprange=row.landhcprange, wanproto=row.wanproto,
                                      wanipv4addr=row.wanipv4addr, wannetmask=row.wannetmask,
                                      wangateway=row.wangateway, wandns=row.wandns,
                                      wan_allow_ssh=row.wan_allow_ssh, wan_allow_web=row.wan_allow_web,
                                      localrestrict=row.localrestrict, sharenet=row.sharenet, url=row.url
                                      )
                ret = builder.build()
                if ret == 0:
                    logger.info("Build finished, ID: " + str(row.id))
                    status = 0
                elif ret == 3:
                    logger.error("Build aborted due to previous errors, ID: " + str(row.id))
                    status = 3
                else:
                    logger.error("Build failed, ID: " + str(row.id))
                    status = 2
                builder.SendMail(status)
                row.update_record(status=status)
                db.commit()
            time.sleep(30)
    except KeyboardInterrupt as e:
        logger.info('Buildqueue stopped by keyboard interrupt.')
        raise
