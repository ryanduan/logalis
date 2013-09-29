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

from configobj import ConfigObj
from os import getcwd
from os.path import abspath, exists

from devshell.base.util import pwd, log
from devshell.base.exceptions import ExecutionException

directory_type = dict()

def register_directory(cls, name):
    global directory_type
    directory_type[name] = cls

buildsystem_type = dict()

def register_buildsystem(cls, name):
    global buildsystem_type
    buildsystem_type[name] = cls

class BuildSystemFactory(object):
    def __new__(cls, type, *args):
        new_cls = buildsystem_type[type]
        foo = new_cls.__new__(new_cls, *args)
        foo.__init__(*args)
        return foo
        

class DirFactory(object):
    '''creates a new object of type defined by a directory's .devshell file'''
    def __new__(cls, name=None):
        if not name:
            log.debug('no name with dirfactory')
            cwd = getcwd()
            type = whatis_sysdir(cwd)
        else:
            log.debug('dirfactory.new with name ' + name)
            cwd = abspath(name)
            if not exists(cwd):
                type = 'directory'
            else:
                type = whatis_sysdir(cwd)
        try:
            new_cls = directory_type[type]
        except KeyError, e:
            raise ExecutionException(e, 'the directory type %s is not supported by this installation of fedora-deveshell' % type.capitalize())
        foo = new_cls.__new__(new_cls, name)
        foo.__init__(name)
        return foo

def whatis_sysdir(dir):
    ''' given a dir, determine it's type'''
    with pwd(dir):
        cfg = ConfigObj('.devshell')
        try:
            type = cfg['type']
            log.debug('is type ' + type)
            return type
        except KeyError, e:
            return 'directory'

__all__ = ['DirFactory', 'BuildSystemFactory', 'register_directory', 'register_buildsystem']
