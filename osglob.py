#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''File operations with pathname pattern expansion (remove, move and copy functionality of os and shutil together with glob)
List of files/content (as os.listdir) filtered by pattern.
Directories operations without error raising for existing/non-existing directories (mkdir, makedirs, rmdir, removedirs)

os.remove -> osglob.remove ...
  Example: osglob.remove('*.pyc')
less exceptions reported

Same as in glob: pattern '*' doesn't affect '.*' files.
Use osglob.<function>('.*' [, ...]) to work with '.*' files only.
Use osglob.files.<function>(...) to work with all files include '.*' files.
Use osglob.content.<function>(...) to work with all sub-directories and all files include '.*' files.

Hint for Windows users: '*' means all files, '*.*' means files with extension.
'''


import glob
import os
import shutil

# files = Files()       # defined bellow the Files class definition
# content = Content()   # defined bellow the Content class definition


def listdir(pattern):
    pass

def mkdir(path, *args, **kwargs):
    '''create a directory
    raises no error if directory already exists (however 'mode' parameter is ignored)
    optional parameter purge (str or bool):
        True or 'content' will remove whole content of the directory if it already exists
        False or 'files' will remove all files from directory if it already exists
        None (or not used purge parameter) will do nothing with the content of the directory
    other parameters (i.e. 'mode' as positional or named) will be used for os.mkdir()
    '''

    _mkdir(os.mkdir, path, *args, **kwargs)

def makedirs(path, *args, **kwargs):
    '''create a directory chain
    raises no error if directory exists already (however 'mode' parameter is ignored)
    optional parameter purge (str or bool):
        True or 'content' will remove whole content of the directory if it already exists
        False or 'files' will remove all files from directory if it already exists
        None (or not used purge parameter) will do nothing with the content of the directory
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
    if path and not os.path.isdir(path):
        _nosuchdir(path)
    ok = True
    for filename in filter(lambda candidate: os.path.isfile(candidate), glob.iglob(pattern)):
        try:
            os.remove(filename)
        except:
            ok = False
    return ok


class Files(object):
    '''accesible as osglob.files
    osglob.files.functions behaves as osglob.functions but affect '*'+'.*' files, i.e. all files (but not sub-directories)
    '''

    def __init__(self):
        self.module_root_remove = remove

    def remove(self, path):
        '''files.remove(path) - delete files include hidden files (.*) in given directory
        the path directory will stay without files (but with sub-directories)
        '.' and '..' are allowed for path
        '''

        _testdir(path)
        ok = self.module_root_remove(os.path.join(path, '.*'))
        return self.module_root_remove(os.path.join(path, '*')) and ok

files = Files()

class Content(object):
    '''accesible as osglob.content
    osglob.content.functions behaves as osglob.functions but affect '*'+'.*'+directories, i.e. whole directory content
    '''

    def remove(self, path):
        '''content.remove(path) - delete sub-directories and files include hidden files (.*) in given directory
        the path directory will stay empty
        '.' is allowed for path
        '''

        _testdir_noparent(path)
        ok = True
        for itemname in os.listdir(path):
            fullname = os.path.join(path, itemname)
            if os.path.isdir(fullname):
                try:
                    shutil.rmtree(fullname)
                except:
                    ok = False
                    self.remove(fullname)  # delete what is possible
            else:
                try:
                    os.remove(fullname)
                except:
                    ok = False
        return ok

content = Content()


def _testdir(path):
    if not os.path.isdir(path):
        _nosuchdir(path)

def _testdir_noparent(path):
    _testdir(path)
    if path == '..' or os.getcwd().startswith(path) and len(path) < len(os.getcwd()):
        raise OSError, "Parent directory is not allowed here: '%s'" % path

def _nosuchdir(path):
    raise OSError, "No such directory: '%s'" % path

def _mkdir(mkfunc, path, *args, **kwargs):
    purge_mode = kwargs.pop('purge', None)
    if not os.path.isdir(path):
        mkfunc(path, *args, **kwargs)
    elif purge_mode is not None:
        purge_mode = {False: False, 'files': False, True: True, 'content': True}[purge_mode]
        if purge_mode:
            os.content.remove(path)
        else:
            os.files.remove(path)
