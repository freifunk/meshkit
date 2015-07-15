import os
import sys
sys.path.insert(0, '../../../')

from gluon.languages import findT

# create /tmp/languages/template.py
if not os.path.exists('../languages/template.py'):
    open('../languages/template.py', "w").close()
    
findT('../', 'template')
