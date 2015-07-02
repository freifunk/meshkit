import os
import time
import shutil


def main():
    delete_before_time = time.time() - (config.keep_images * 3600)
    if os.access(config.images_output_dir, os.R_OK):
        for filename in os.listdir(config.images_output_dir):
            dir = os.path.join(config.images_output_dir, filename)
            stat = os.stat(dir)
            if stat.st_mtime < delete_before_time:
                try:
                    shutil.rmtree(dir)
                except OSError:
                    print "Could not delete " + dir
    else:
        print config.images_output_dir + " does not exist."

if __name__ == '__main__' and config.keep_images > 0:
    main()
