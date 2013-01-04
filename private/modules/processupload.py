import os
import tarfile
resolved = lambda x: os.path.realpath(os.path.abspath(x))

def _badpath(path, base):
    return not resolved(os.path.join(base,path)).startswith(base)

# This checks prevents unpacking of illegal files (e.g. absolute pathnames)
badlist = []
def safemembers(members):
    base = resolved(".")
    for finfo in members:
        if _badpath(finfo.name, base):
            badlist.append(finfo.name)
        else:
            yield finfo

def extract(archive, path):
    try:
        tar = tarfile.open(archive)
    except tarfile.ReadError:
        return "Could not open " + archive
    try:
        tar.extractall(path=path, members=safemembers(tar))
    except IOError:
        return "IOError: Could not extract " + archive
    try:
        tar.close()
    except:
        pass

    if len(badlist) > 0:
        badpaths = ""
        for i in badlist:
            badpaths += i + " "
        return "The following files were not extracted for security reasons: " + badpaths
        

