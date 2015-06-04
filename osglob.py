#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Python file operations with pathname pattern expansion (os/shutil together with glob)

os.remove -> osglob.remove ...
  Example: osglob.remove('*.pyc')
less exceptions reported

Same as in glob: pattern '*' doesn't affect '.*' files.
Use osglob.<function>('.*' [, ...]) to work with '.*' files only.
Use osglob.total.<function>('*' [, ...]) to work with '.*' files too.

Hint for Windows users: '*' means all files, '*.*' means files with extension.
'''


import glob
import os

# total = Total()    # defined bellow the Total class definition


def remove(pattern):
    ok = True
    path = os.path.dirname(pattern)
    if path and not os.path.isdir(path):
        raise OSError, "No such directory: '%s'" % path
    else:
        for filename in filter(lambda candidate: os.path.isfile(candidate), glob.iglob(pattern)):
            try:
                os.remove(filename)
            except:
                ok = False
    return ok

class Total(object):
    '''accesible as osglob.total
    osglob.total.functions behaves as osglob.functions but pattern=='*' will affect '.*' files too
    '''

    def __init__(self):
        self.cls_remove = remove

    def remove(self, pattern='*'):
        ok = True
        if pattern=='*':
            ok = self.cls_remove('.*') and ok
        return self.cls_remove(pattern) and ok

total = Total()
