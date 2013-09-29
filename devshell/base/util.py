# Fedora Developer Shell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors: Yaakov M. Nemoy <ynemoy@redhat.com>
#

from __future__ import with_statement

from contextlib import contextmanager
from datetime import datetime
from os import chdir, getcwd, remove
from os import symlink as sym
from os.path import abspath, lexists, isdir, islink, isfile
from shutil import copyfileobj, rmtree
from shutil import move as mv
from shutil import copytree as cpthree
from urllib import urlopen

from devshell.base.base import log

@contextmanager
def pwd(dir):
    old_dir = getcwd()
    chdir(dir)
    yield
    chdir(old_dir)

@contextmanager
def log_file(fname):
    with file(fname, 'a') as fout:
        fout.write("-- Beginning log of %s at %s --\n" % (fname, datetime.now().isoformat(' ')))
        fout.flush()
        yield fout
        fout.write("-- Ending log of %s at %s --\n\n" % (fname, datetime.now().isoformat(' ')))

def rm(tgt):
    if isdir(tgt):
        rmtree(tgt)
    else:
        remove(tgt)

def copy(src, dst):
    # we're using copyfileobj so we can do this from a URL
    if isfile(src):
        src_f = file(src, 'rb')
    else:
        src_f = urlopen(src)
    dst_f = file(dst, 'wb')
    copyfileobj(src_f, dst_f)
    src_f.close()
    dst_f.close()
    # return the dst path as a matter of utility
    return dst

def symlink(src, dst):
    if lexists(dst):
        rm(dst)
    sym(abspath(src), abspath(dst))
    return dst

def move(src, dst):
    if lexists(dst):
        rm(dst)
    mv(src, dst)
    return dst

def copytree(src, dst):
    if lexists(dst):
        rm(dst)
    # cee-pee-tree in jamaica, mon!
    cpthree(src, dst)
    return dst

def remove_all(i, l):
    while i in l:
        l.remove(i)

def one(l, f):
    for x in l:
        if f(x):
            return x

def isiter(i):
    return hasattr(i, '__iter__')

def flatten(l):
    acc = []
    def _flatten(acc, i):
        if isiter(i):
            for x in i:
                _flatten(acc, x)
        else:
            acc.append(i)
    _flatten(acc, l)
    return acc

def base_dir(tarball):
    ti = tarball.next()
    if ti.name == 'pax_global_header':
        ti = tarball.next()
    return ti.name.split('/')[0]

_to_close = list()
_all_closed = False

def close_later(directory):
    global _to_close
    if directory not in _to_close:
        _to_close.append(directory)
    return directory

def close_all():
    global _all_closed
    global _to_close
    if _all_closed:
        return
    _all_closed = True
    for directory in _to_close:
        directory.close()
    

__all__ = ['pwd', 'copy', 'with_sudo', 'with_su', 'symlink', 'move',
           'log_file', 'one', 'remove_all', 'flatten', 'base_dir',
           'close_later', 'close_all']
