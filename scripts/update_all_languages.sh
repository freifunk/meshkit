#!/bin/sh

echo "IMPORTANT"
echo "Script disabled because it does not work correctly"

# the problem is:
# not all strings are found by findT in ./dict_template_create.py.
# It has problems finding multiline and "generated" translation strings
# and then good strings will be cleaned up as well from the translation files

# the regex responsible for finding the strings is in gluon/languages.py

exit 1

rm -f ../languages/template.py
languages="../languages/*.py"

# create template dict
python ./dict_template_create.py


for l in $languages; do
    # ignore template.py
    [ "$l" = "../languages/template.py" ] && return
	echo "Cleaning up $l\n"
	python dict_cleanup.py $l ../languages/template.py
done

rm -f ../languages/template.py
