import logging
import os
import sys

''' Options '''
loglevel = logging.DEBUG


def initialize_logging(request_folder, name):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s\t%(message)s')
    logger.setLevel(loglevel)
    logfile = os.path.join(request_folder, "logs", "buildqueue.log")

    if not logger.handlers:
        log2file = logging.FileHandler(logfile)
        log2file.setFormatter(formatter)
        logger.addHandler(log2file)
        log2stdout = logging.StreamHandler(sys.stdout)
        log2stdout.setFormatter(formatter)
        logger.addHandler(log2stdout)

    return logger
