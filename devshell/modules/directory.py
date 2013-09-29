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
# Authors: Luke Macken <lmacken@redhat.com>
#          Yaakov M. Nemoy <ynemoy@redhat.com>
#

from __future__ import with_statement


from configobj import ConfigObj
from os import makedirs, getcwd, listdir
from os.path import abspath, join, split, splitext, basename, exists, dirname
from contextlib import contextmanager

from devshell.base.base import log
import devshell.base.factories as factories
from devshell.base.factories import DirFactory
from devshell.base.module import Module
from devshell.base.util import pwd, copytree, close_all

class MetaDirectory(type):
    def __init__(cls, name, bases, attrs):
        t = name.lower()
        cls._type = t
        factories.register_directory(cls, t)

class Directory(Module):
    '''a generic base class for any module that has to maintain state 
    on the file system in a directory
    '''
    __metaclass__ = MetaDirectory
    def __init__(self, name=None):
        ''' initializer
        
        name is a path to the directory we are loading, if not given
            name is gleaned by assuming the current directory is the
            package desired
        '''
        if not name:
            cwd = getcwd()
            if self.is_sysdir_dir(cwd):
                self.load_dir(cwd)
            else:
                self.make_dir(cwd)
        else:
            dir = abspath(name)
            if not exists(dir):
                makedirs(dir)
            if self.is_sysdir_dir(dir):
                self.load_dir(dir)
            else:
                self.make_dir(dir)

    def is_sysdir_dir(self, dir):
        '''given a directory, determine if the system directory is
        already a directory or not'''
        with pwd(dir):
            cfg = ConfigObj('.devshell')
            try:
                if self._type  in cfg['type']:
                    return True
                else:
                    return False
            except KeyError, e:
                return False

    def load_dir(self, dir):
        '''presuming dir is a directory, load it's state'''
        with pwd(dir):
            parent, name = split(getcwd())
            self.parent = parent
            self.cfg = ConfigObj('.devshell')
            if not self.name == name:
                # we are saving name in the .devshell file so we can detect
                # if the name has been changed or not. we don't want to have to run
                # rename all the time
                self.rename(name)
                pass

    def make_dir(self, dir):
        '''since dir is not a directory, make it into one'''
        with pwd(dir):
            self.cfg = ConfigObj('.devshell')
            parent, name = split(getcwd())
            # type is defined by the subclass
            self.cfg['type'] = self._type
            self.cfg['name'] = name
            self.parent = parent
            self.cfg.write()

    @property
    def name(self):
        ''' the name of the directory/module as defined by the user
        '''
        return self.cfg['name']

    @property
    def dir(self):
        '''absolute pathname to the directory where it is held on the file system'''
        return join(self.parent, self.name)

    @contextmanager
    def in_dir(self):
        with pwd(self.dir):
            yield

    def close(self):
        '''called by devshell, closes the open objects'''
        log.debug('writing self.cfg for ' + self.dir)
        with pwd(self.dir):
            self.cfg.write()
        close_all()

    def rename(self, new_name):
        '''renames the directory internally, assuming it's been renamed 
        on the file system

        subclass authors take note, this must be reimplemented, and the 
        superclass version called when any property or state depends on
        self.name in any way shape or form.
        '''
        self.cfg['name'] = new_name

    def move(self, new_loc):
        '''given a new location, moves everything there, and renames'''
        new_loc = abspath(new_loc)
        new_parent, new_name = split(new_loc)
        old_dir = self.dir
        copytree(self.dir, new_loc)
        self.parent = new_parent
        self.rename(new_name)
        with pwd(self.dir):
            self.cfg.write()
        rm(old_dir)

    def copy(self, new_loc):
        '''makes a copy of the contents in a new location, renames, 
        and returns a reference to a new object rpresenting the new directory'''
        new_loc = abspath(new_loc)
        new_parent, new_name = split(new_loc)
        copytree(self.dir, new_loc)
        new_dir = DirFactory(new_loc)
        return new_dir

__all__ = ['Directory']
