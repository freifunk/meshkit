import os
import re

class UCI(object):

    """
    Class used to work with uci files. At this time only reading of uci files is supported
    
    Args:
        config_path: Path where the uci config files are stored
        config_file: filename of the config file
    """

    def __init__(self, config_path="/etc/config", config_file="Freifunk"):
        self.Path = config_path
        self.File = config_file

    def read(self):
        """Reads a uci file into a nested tuple

        Note: this only works with named sections, i.e. it will work with
        config 'foo' 'bar' (bar is the name of the section here)
        but not with
        config 'foo'
    
        Returns:
            A nested tuple with all settings from the uci config, e.g.:
            {'sectionname1': {
                 'option1': 'foo',
                 'option2': 'bar',
             'sectionname2': {
                 'option1': 'foo'},
             }
        """
        config = {}
        file = os.path.join(self.Path, self.File)
        if os.access(file, os.R_OK):
            config_file = open(file, 'r')
            for line in config_file:
                line = line.replace('\n', '')
                line = line.replace("'", '')
                line = line.replace('"', '')
                if line.rstrip().startswith('#'): #remove comments
                    pass
                elif line.startswith('config'): # new config section starting
                    sectionname = line.split(" ")[2]
                    config[sectionname] = {}
                elif re.match(r'\s+', line):    # this is an option
                    line = re.sub(' +',' ', line)
                    line = re.sub('\t',' ', line)
                    line = line.split(' ')
                    length = len(line)
                    option = line[2]
                    # values may be separated by space, so iterate over everything thats left
                    value = ""
                    for v in range(3,length):
                        value = value + " " + line[v]
                    config[sectionname][option] = value.strip()
        else:
            pass
        return config

    def get(self, config, section, option, default):
        try:
            ret = config[section][option]
        except KeyError:
            ret = default
        return ret          
