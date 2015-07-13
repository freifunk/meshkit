#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import errno
import distutils
from distutils.dir_util import copy_tree
from gluon import current
if hasattr(current, 'T'):
        T = current.T

import log
logger = log.initialize_logging(current.request.folder, __name__)


def write_file(file, content):
    """ Write content to a file

        Args:
            file -- full path to the file to write to (string)
            content -- content written to the file (str)

        Returns:
            True if the file was written, else False.

        Logs an critical error in Case of IOError

    """
    logger.debug("write file: %s" % file)
    try:
        with open(file, "w") as f:
            f.write(content)
            return True
    except IOError as e:
        err = T('Could not write %s because of an IOError: %s: %s') \
            % (file, e.errno, e.strerror)

        logger.critical(err)
        return False


def mkdir_p(path):
    """ Create a directory

        Args:
            path -- full pathname of the directory to create (string)

        Returns:
            True if the directory was created or already exists, else False

    """
    try:
        os.makedirs(path)
        return True
    except OSError as e:
        if e.errno == errno.EEXIST:
            return True
        else:
            logger.critical("Error: Could not create directory %s" % path)
            return False


def cptree(src, dst):
    """ recursively copy a directory tree to a new location

        Args:
            src -- source path (string)
            dst -- destination path (string)

        Returns:
            True if successful, else False

    """

    ret = False
    try:
        copy_tree(src, dst, preserve_symlinks=0)
        logger.debug('Copied %s to %s' % (src, dst))
        ret = True
    except distutils.errors.DistutilsFileError as e:
        logger.warning(
            'Source directory %s does not exist. %s' % (src, str(e))
        )
    except IOError as e:
        logger.critical(
            'Could not create/write to directory %s. Check permissions.' %
            dst
        )

    return ret
