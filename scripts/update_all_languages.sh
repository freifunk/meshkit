#!/bin/sh

rm -f ../languages/template.py
languages="../languages/*"

# create template dict
python ./dict_template_create.py

for l in $languages; do
	echo "Cleaning up $l\n"
	python dict_cleanup.py $l ../languages/template.py
done

rm -f ../languages/template.py
