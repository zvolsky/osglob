#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Python file operations with pathname pattern expansion (os/shutil together with glob)

os.remove -> osglob.remove ...
  Example: osglob.remove('*.pyc')
less exceptions reported

Same as in glob: pattern '*' doesn't affect '.*' files.
Use osglob.<function>('.*' [, ...]) to work with '.*' files only.
#TODO to be deleted later?  Use osglob.total.<function>('*' [, ...]) to work with '.*' files too.

Hint for Windows users: '*' means all files, '*.*' means files with extension.
'''


import glob
import os

# total = Total()    # defined bellow the Total class definition


def mkdir(path, *args, **kwargs):
    '''create a directory
    raises no error if directory already exists (however 'mode' parameter is ignored)
    optional parameter purge=True will remove all files from directory if it already exists
    other parameters (i.e. 'mode' as positional or named) will be used for os.mkdir()
    '''

    _mkdir(os.mkdir, path, *args, **kwargs)

def makedirs(path, *args, **kwargs):
    '''create a directory chain
    raises no error if directory exists already (however 'mode' parameter is ignored)
    optional parameter purge=True will remove all files from directory if it already exists
    other parameters (i.e. 'mode' as positional or named) will be used for os.mkdir()
    '''

    _mkdir(os.makedirs, path, *args, **kwargs)

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

    path = os.path.dirname(pattern)
    _testdir(path)
    ok = True
    for filename in filter(lambda candidate: os.path.isfile(candidate), glob.iglob(pattern)):
        try:
            os.remove(filename)
        except:
            ok = False
    return ok

def purge(path=''):
    '''purge(path) - delete files include hidden files (.*) in given directory
    purge() - delete files include hidden files (.*) in current working directory
    '''

    _testdir(path)
    ok = remove(os.path.join(path, '.*'))
    return remove(os.path.join(path, '*')) and ok

#TODO maybe to be deleted later - start here //remove total=Total(), #total=Total() above, total.xx in module.__doc__
class Total(object):
    '''accesible as osglob.total
    osglob.total.functions behaves as osglob.functions but pattern=='*' will affect '.*' files too
    '''

    def __init__(self):
        self.cls_remove = remove

    def remove(self, path=''):
        '''total.remove(path) - delete files include hidden files (.*) in given directory
        total.remove() - delete files include hidden files (.*) in current working directory
        '''

        _testdir(path)
        ok = self.cls_remove(os.path.join(path, '.*'))
        return self.cls_remove(os.path.join(path, '*')) and ok
total = Total()
# maybe to be deleted later - stop here

def _testdir(path):
    if path and not os.path.isdir(path):
        raise OSError, "No such directory: '%s'" % path

def _mkdir(mkfunc, path, *args, **kwargs):
    purge_it = kwargs.pop('purge', False)
    if not os.path.isdir(path):
        mkfunc(path, *args, **kwargs)
    elif purge_it:
        purge(path)
