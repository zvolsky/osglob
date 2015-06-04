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


def mkdir(path, *args, **kwargs):
    '''create a directory
    raises no error if directory exists already
    '''

    if not os.path.isdir(path):
        os.mkdir(path, *args, **kwargs)

def makedirs(path, *args, **kwargs):
    '''create a directory chain
    raises no error if directory exists already
    '''

    if not os.path.isdir(path):
        os.makedirs(path, *args, **kwargs)

def rmdir(path, silent=False):
    '''remove a directory
    raises no error if directory doesn't exist
    return True if directory no longer exists
    silent: if True, then OSError exception is never raised (you can check returned value if directory was removed)
    '''

    if os.path.isdir(path):
        try:
            os.rmdir(path)
        except OSError as e:
            if not silent:
                raise e
            return False
    return True

def removedirs(path, root='', silent=False):
    '''remove a directory chain as long as no error occurs
      (an error usually means a not empty folder and such error is not raised)
    raises no error if directories don't exist
    return True if whole path no longer exists
    root: path is relative to this directory (which is not affected)
    silent: if True, then OSError exception is never raised (you can check returned value if path was removed)
    '''

    if rmdir(os.path.join(root, path), silent=silent):
        while os.sep in path:
            path = path.rsplit(os.sep, 1)[0]
            try:
                rmdir(os.path.join(root, path))
            except OSError:
                return False
        return True
    else:
        return False

def remove(pattern):
    '''remove files based on pattern
    pattern can contain path
    raises no error if no such file exists
    '''

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
        '''remove files based on pattern, include hidden (.*) files if pattern=='*'
        '''

        ok = True
        if pattern=='*':
            ok = self.cls_remove('.*') and ok
        return self.cls_remove(pattern) and ok

total = Total()
