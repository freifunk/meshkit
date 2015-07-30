#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import shutil


def cleanup():
    """ Clean expired builds in the image directory

        Builds are considered expired, when their age is more than
        config.keep_images hours.

        Returns:
            mixed -- Number of deleted images if successful or False if there
                     was an error.
    """

    from gluon import current
    import log
    logger = log.initialize_logging(current.request.folder, __name__)
    config = current.config
    out_dir = config.images_output_dir
    if not out_dir:
        logger.critical("Missing variable config.images_output_dir.")
        return False

    delete_before_time = time.time() - (config.keep_images * 3600)
    if os.access(out_dir, os.R_OK):
        i = 0
        for filename in os.listdir(out_dir):
            dir = os.path.join(out_dir, filename)
            stat = os.stat(dir)
            if stat.st_mtime < delete_before_time:
                try:
                    shutil.rmtree(dir)
                    i = i + 1
                except OSError:
                    logger.error("Could not delete %s" % dir)
        if i == 0:
            logger.debug("Cleanup image dir: No builds deleted.")
        else:
            logger.info("Cleanup image dir: Deleted %s builds." % i)
            return i
    else:
        logger.warning("%s does not exist." % out_dir)
        return False

if __name__ == '__main__' and config.keep_images > 0:
    cleanup()
