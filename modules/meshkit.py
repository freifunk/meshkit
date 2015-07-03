#!/usr/bin/env python
# coding: utf8
from __future__ import with_statement  # for compat with 2.5
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from gluon import *
from gluon.storage import Storage
from gluon.cache import Cache
import os
import glob
import re
import subprocess
try:
    import json
except ImportError:
    import simplejson as json
import uci


def get_hostname_from_form_vars(vars):
    """ returns the systems hostname

        if form.vars.hostname is available use it. If not, try to generate
        a hostname from one of the wifi ips. If that fails too: use 'OpenWrt'
        as default.

        Args:
            vars: a web2py form.vars object

        Returns:
            string: system hostname (Default: OpenWrt)

    """

    hostname = "OpenWrt"

    if vars.hostname:
        hostname = vars.hostname
    else:
        for i in range(9):
            if vars["wifi%sipv4addr" % i]:
                hostname = vars["wifi%sipv4addr" % i].replace(".", "-")
                break

    return hostname


def filter_wifi_interfaces(vars):
    """ filter out all wifi options and write to wifi_interfaces table

        Args:
            vars:    a web2py form.vars object

        Returns:
            list:    a list containing all wifi options

    """

    wifi_options = []
    # probably not the most performant way to get the interfaces in order
    for i in range(9):
        for v in vars:
            if v.startswith("wifi%s" % i):
                try:
                    iface_index = int(v[4:5])
                except ValueError:
                    continue
                option = v[5:]
                try:
                    wifi_options[iface_index][option] = vars[v]
                except IndexError:
                    wifi_options.append(dict())
                    wifi_options[iface_index][option] = vars[v]

    return wifi_options


def get_communities(path):
    """Get a list of communities we have profiles for

    Args:
        path: path where the community profiles are stored
    Returns:
        dict: key is extracted from the filename by removing "profile_" from it
              value is read from each profiles (option name)
      """
    communities = {}
    for filename in os.listdir(path):
        if "profile" in filename and not filename == "profile_Freifunk":
            m = re.search('(?<=profile_).*', filename)
            key = m.group(0)
            c = uci.UCI(path, filename)
            community_defaults = c.read()
            name = c.get(community_defaults, 'profile', 'name', key)
            communities[key] = name
            
    return OrderedDict(sorted(communities.items(), key=lambda x: x[1].lower()))
    


def get_targets(ibpath):
    """Get a list of build targets

    Args:
        ibpath: imagebuilder path
    Returns:
        A sorted list containing the directory names of all targets found.
        e.g.
        ['ar71xx-backfire-32500', 'brcm47xx-backfire-32500', 'muchmore']

    """
    targets = []
    for filename in os.listdir(ibpath):
        if os.path.isdir(os.path.join(ibpath, filename)):
            targets.append(filename)
    return sorted(targets)


def dict_pkg_info(ibpath, target, savedir):
    """Reads the output of 'make info' in the target directory into nested tuples

    This function will create nested from the 'make info' imagebuilder command.
    This is a bit expensive in computation time (was about 80ms here). So we
    create this once and cache it for further use on the harddisk.
    The downside of this is that it doesn't update if you changed something in
    the Makefiles in imagebuilder (e.g. add/remove packages from profiles).
    In this (rare) case you will have to delete the cached file manually.


    Args:
        ibpath: imagebuilder path
        target: target (name of the target/architecture folder in ibpath)
        savedir: directory where the generated tuple file should be saved
    Returns:
        nested tuples containing:
        -info (tuple)
            - profile name (tuple)
                - packages
                - desc
         -defpkgs (list)
         e.g.:
         {
            'info':{
                'WZRHPG300NH':{
                    'packages': 'kmod-usb-core kmod-usb2',
                    'desc': 'Buffalo WZR-HP-G300NH'
                },
                'TLWR741NDV1':{
                    'packages': '',
                    'desc': 'TP-LINK TL-WR741ND v1'
                }
            },
            'defpkgs': [
                'base-files', 'kmod-ath9k', 'wpad-mini'
            ]
        }

    """
    try:
        with open(savedir + "/" + target, 'r') as f:
            # info = eval(f.read())
            info = eval(json.loads(f.read)())
            f.closed
            return info
    except:
        pfl = subprocess.Popen(
            ["cd " + ibpath + "/" + target + "; make info", ""],
            stdout=subprocess.PIPE,
            shell=True
        )
        out, err = pfl.communicate()
        out = out.replace("Available Profiles:\n", "")
        info = {}
        # Get Default packages
        pattern = r'(Default Packages:\s.*)'
        regex = re.compile(pattern)
        info['defpkgs'] = []
        for match in regex.finditer(out):
            info['defpkgs'] = match.group(0).replace(
                "Default Packages: ", "").split(" ")

        # get packages info
        pattern = r'([\w-]+:\n.*\n.*)\s+'
        regex = re.compile(pattern)
        info['info'] = {}
        for match in regex.finditer(out):
            group = match.group(1)
            n = re.search("[\w-]+:", group)
            name = n.group(0).replace(":", "")
            pattern = re.compile(".*")
            o = pattern.search(group, n.end(0) + 1)
            desc = o.group(0).replace("\t", "")
            p = pattern.search(group, o.end(0) + 1)
            packages = p.group(0).replace("\tPackages: ", "")
            t = {'desc': desc, 'packages': packages}
            info['info'][name] = t

        # Write info to file
        try:
            f = open(savedir + "/" + target, "w")
            try:
                f.write(str(info))
            finally:
                f.close()
        except IOError:
            pass

        return info


def get_profiles(ibpath, target, savedir, remove_default=False):
    """Get a list of available profiles for one target.

    Args:
        ibpath: imagebuilder path
        target: target (name of the target/architecture folder in ibpath)
        savedir: directory where the cached files will be saved
        remove_default: remove Default profiles, they create a lot of images
                        (boolean)

    Returns:
        dict(): a sorted dictionary containing the profile shortname as key
                and the long name as value.

    """
    profiles = {}
    info = dict_pkg_info(ibpath, target, savedir)
    for p in info['info']:
        if remove_default:
            if "ar71xx" in target and p == "Default":
                pass
            else:
                profiles[p] = info['info'][p]['desc']
        else:
            profiles[p] = info['info'][p]['desc']

    return OrderedDict(sorted(profiles.items(), key=lambda x: x[1].lower()))


def get_profile(ibpath, target, savedir, profile):
    """Get info of one selected profile for one target.

    Args:
        ibpath: imagebuilder path
        target: target (name of the target/architecture folder in ibpath)
        savedir: directory where the cached files will be saved
        profile: get info for this profile
    Returns:
        A tuple which contains packages and description for this profile
        e.g.
        {
            'packages': 'kmod-usb-core kmod-usb2',
            'desc': 'Buffalo WZR-HP-G300NH'
        }

    """
    info = dict_pkg_info(ibpath, target, savedir)
    return info['info'][profile]


def get_defaultpkgs(ibpath, target, savedir):
    """Get the default packages for one target.

    Args:
        ibpath: imagebuilder path
        target: target (name of the target/architecture folder in ibpath)
        savedir: directory where the cached files will be saved
    Returns:
        A list containing the default packages for this target
        e.g.
        ['base-files', 'kmod-ath9k', 'wpad-mini']

    """
    info = dict_pkg_info(ibpath, target, savedir)
    return info['defpkgs']


def get_luci_themes(ibpath, target):
    """Get a list of available themes for one target.

    Args:
        ibpath: imagebuilder path
        target: target (name of the target/architecture folder in ibpath)
    Returns:
        A sorted list which contains the shortened names of all theme
        packages found. They are shortened in a way that allows to directly
        use these names to install them via imagebuilder (or opkg).
        luci-theme-base is filtered from this list.
        e.g.
        [ 'luci-theme-bootstrap', 'luci-theme-fledermaus' ]

    """

    themes = []
    luci_packages = (
        ibpath + "/" + target + "/packages/luci-theme-*",
        ibpath + "/" + target + "/packages/luci/luci-theme-*"
    )

    for package_dir in luci_packages:
        for filename in glob.glob(package_dir):
            if not re.match(".*luci-theme-base.*", filename):
                filename = filename[filename.find("luci-theme"):len(filename)]
                filename = filename.split("_")[0]
                themes.append(filename)
    return sorted(themes)


def create_package_list(ibpath, target, savedir):
    """Generates a static package list and saves it to disk.

    Args:
        ibpath: imagebuilder path
        target: target (name of the target/architecture path in ibpath)
        savedir: folder where the generated packagelist will be saved

    """
    def _generate_packagelist_json(ibpath, target, savedir):
        info = ""
        package_path = os.path.join(ibpath, target, 'packages')
        package_list = os.path.join(ibpath, target, 'packages', 'Packages')

        if os.path.exists(package_list):
            with open(package_list, 'r') as f:
                info = str(f.read())
                f.closed
        else:
            for directory in os.listdir(package_path):
                if os.path.exists(package_path + directory + '/Packages'):
                    alt_packages_path = os.path.join(
                        package_path, directory, 'Packages'
                    )
                    with open(alt_packages_path, 'r') as f:
                        info += str(f.read())
                        f.closed

        infolist = re.split('\n\n', info)
        tmplist = {}
        for block in infolist:
            if len(block) > 1:
                pkgname = re.search("Package: (.*)", block).group(1)
                size = re.search("Installed-Size: (.*)", block).group(1)
                section = re.search("Section: (.*)", block).group(1)
                version = re.search("Version: (.*)", block).group(1)
                try:
                    t = {'version': version, 'size': size}
                    tmplist[section][pkgname] = t
                except:
                    tmplist[section] = {}
                    t = {'version': version, 'size': size}
                    tmplist[section][pkgname] = t

        result = json.JSONEncoder(
            sort_keys=True, separators=(',', ':')).encode(tmplist)
        if not os.path.exists(savedir):
            try:
                os.mkdir(savedir)
            except IOError, e:
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
        try:
            f = open(os.path.join(savedir, target), "w")
            f.write(str(result))
        except IOError, e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            print "Could not write to " + (os.path.join(savedir, target))
        finally:
            f.close()

    if os.access(os.path.join(savedir, target), os.R_OK):
        pass
    else:
        _generate_packagelist_json(ibpath, target, savedir)


def defip(mesh_network):
    """ Returns the first ip from mesh_network

    Args:
        mesh_network = IPv4 network in CIDR notation, e.g. 10.0.0.0/24

    Returns:
        first IP from that network, e.g. 10.0.0.1
    """
    ip_first = mesh_network.split("/")[0]
    octets = ip_first.split(".")
    return "%s.%s.%s.%s" % (
        octets[0], octets[1], octets[2], str(int(octets[3]) + 1)
    )


def replace_obsolete_packages(available_packages_file, packages, rtable):
    """Replaces packages in the package list that have been renamed or deleted

    Args:
        available_packages_file (string): Full path to the json-package list
                                          (static/package_lists/<target>)
        packages (string): List of packages
        rtable (dict): table containing what should be replaced with what
    Returns:
        string with replaced packages
    """

    if not available_packages_file or not packages or not rtable:
        return False
    else:
        with open(available_packages_file, 'r') as f:
            available_packages = json.load(f)
            f.closed

        pkgtbl = packages.split(' ')

        for pkg in rtable:
            has_pkg = False
            for key in available_packages:
                if pkg in available_packages[key]:
                    has_pkg = True

            if not has_pkg:
                # packages = packages.replace(pkg, rtable[pkg])
                pkgtbl = [item for item in pkgtbl if not item.startswith(pkg)]
                pkgtbl.append(rtable[pkg])

        return ' '.join(pkgtbl)
