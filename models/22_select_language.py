# coding: utf8
if 'all_lang' in request.cookies and not (request.cookies['all_lang'] is None):
    T.force(request.cookies['all_lang'].value)
