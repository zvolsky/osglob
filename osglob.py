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
import stat

# files = Files()       # defined bellow the Files class definition
# content = Content()   # defined bellow the Content class definition


def expandpath(pattern):
    '''return the file/path name with expanded '.', '..', '~' and as absolute path
    pattern can contain file mask (glob pattern)
    '''
    return os.path.abspath(os.path.expanduser(pattern))

def justpath(pattern, expanded=True):
    '''return path portion of file/path name
    pattern can contain file mask (glob pattern)
    note: this makes test for directory presence: if pattern is existing directory then path is same as pattern (no name splitting applies)
      i.e. for existing directory entry both /entry and /entry/ are treated as directory name
      but for non-existing directory entry /entry/ is treated as directory name, but /entry as filename
    default behaviour is conversion to absolute path with expanded '.', '..', '~'; to avoid absolute path and expansion use: expanded=False
      expanded=None works like expanded=False, but will return '' instead of '.' if no path is given
    '''
    if os.path.isdir(pattern):
        path = pattern
    else:
        path = os.path.dirname(pattern)
    if expanded is None:
        return os.path.normpath(path) if path else ''
    elif expanded:
        return os.path.abspath(path)
    else:
        return os.path.normpath(path)

def justname(pattern):
    '''return filename portion of file/path name (with expanded '.', '..', '~' and as absolute path)
    pattern can contain file mask (glob pattern)
    note: this makes test for directory presence: if pattern is existing directory then filename is empty (no name splitting applies)
      i.e. for existing directory entry both /entry and /entry/ are treated as directory name
      but for non-existing directory entry /entry/ is treated as directory name, but /entry as filename
    '''
    if os.path.isdir(pattern):
        return ''
    else:
        return os.path.basename(pattern)

def juststem(pattern):
    '''return filename stem portion (filename without extension) of file/path name
    pattern can contain file mask (glob pattern)
    note: this makes test for directory presence: if pattern is existing directory then stem is empty (no name splitting applies)
      i.e. for existing directory entry both /entry and /entry/ are treated as directory name
      but for non-existing directory entry /entry/ is treated as directory name, but /entry as stem of the filename
    '''
    return justname(os.path.splitext(pattern)[0])

def justext(pattern):
    '''return filename extension of file/path name
    pattern can contain file mask (glob pattern)
    '''
    return os.path.splitext(pattern)[1][1:]

def listdir(pattern='.', expanded=False):
    '''list of entries (files and dirs) in directory, pattern can contain path and mask (glob pattern)
    expanded=False : name without path are returned (this is default)
    expanded=True : full pathnames are returned
    expanded=None : names from raw underlying function are returned (this is howwever inconsistent between os.listdir and glob.glob)
    '''
    if os.path.isdir(pattern):
        entries = os.listdir(pattern)
        if expanded:
            path = justpath(pattern)
            entries = [expandpath(os.path.join(path, entry)) for entry in entries]
    else:
        path = os.path.dirname(pattern)
        if path and not os.path.isdir(path):
            _nosuchdir(path)
        entries = glob.glob(pattern)
        if expanded is not None:
            if expanded:
                entries = [expandpath(entry) for entry in entries]
            else:
                entries = [os.path.basename(entry) for entry in entries]
    return entries

def listdirectories(pattern='.', expanded=False, listdir_result=None):
    '''list of sub-directories (filtered by mask from pattern) in directory (current or with path given from pattern)
    pattern: mask for directory names
        .* or ends with /.* ..(linux)hidden directories
        * or ends with /*   ..(linux)nonhidden directories
        ends with /         ..all directories
        default: all directories in current working dir
    expanded: with or without(default) full path (see listdir for details)
    listdir_result [rare required]: result from previous listdir(pattern, expanded) call
        this will prevent additional unnecessary listdir() calls in consecutive calls of directories()/files()/links()
    '''
    return _filtered_by_type(os.path.isdir, pattern, expanded, listdir_result)

def listfiles(pattern='.', expanded=False, listdir_result=None):
    '''list of files (filtered by mask from pattern) in directory (current or with path given from pattern)
    pattern: mask for file names
        .* or ends with /.* ..(linux)hidden files
        * or ends with /*   ..(linux)nonhidden files
        ends with /         ..all files
        default: all files in current working dir
    expanded: with or without(default) full path (see listdir for details)
    listdir_result [rare required]: result from previous listdir(pattern, expanded) call
        this will prevent additional unnecessary listdir() calls in consecutive calls of directories()/files()/links()
    '''
    return _filtered_by_type(os.path.isfile, pattern, expanded, listdir_result)

def listlinks(pattern='.', expanded=False, listdir_result=None):
    '''list of links - for parameters see directories() or files()
    '''
    return _filtered_by_type(os.path.islink, pattern, expanded, listdir_result)

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
            path = justpath(path)
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

        def try_make_rw(func, path, exc):
            '''If the error is due to an access error (read only file)
            it attempts to add write permission and then retries.
            '''
            if not os.access(path, os.W_OK):  # is the error an access error?
                os.chmod(path, stat.S_IWRITE)
                func(path)
            else:
                raise

        _testdir_noparent(path)
        ok = True
        for itemname in os.listdir(path):
            fullname = os.path.join(path, itemname)
            if os.path.isdir(fullname):
                try:
                    shutil.rmtree(fullname, onerror=try_make_rw)
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
    if path == os.pardir or os.getcwd().startswith(path) and len(path) < len(os.getcwd()):
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

def _filtered_by_type(filter_func, pattern, expanded, listdir_result):
    return filter(lambda candidate: filter_func(os.path.abspath(os.path.join(justpath(pattern), candidate))),
                  listdir_result or listdir(pattern, expanded))
