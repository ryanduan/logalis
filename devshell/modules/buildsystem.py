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

from os.path import join
from contextlib import contextmanager

import devshell.base.factories as factories

from devshell.base.factories import DirFactory
from devshell.base.module import Module
from devshell.base.util import log_file, rm, log

class MetaBuildSystem(type):
    def __init__(cls, name, bases, attrs):
        t = name.lower()
        cls._type = t
        factories.register_buildsystem(cls, t)

class BuildSystem(Module):
    __metaclass__ = MetaBuildSystem
    def __init__(self, name):
        if type(name) is str:
            self.pkg_src = DirFactory(name)
            self.name = name
        else:
            self.pkg_src = name
            self.name = name.name

    def prepare(self, install=False, force=False, *args):
        '''runs the preparation/distribution stage of a build system

        does not apply to all systems, in particular this is analogous
        to autoreconf of the autotools package

        install has the preparer copy in any shell scripts or other bits
        that need to be distributed

        force forces the preparer to copy in any bits even if they are already there
        '''
        raise NotImplementedError

    def configure(self, target='home', *args):
        '''runs the configure stage of cabal
        
        target is either 'home' or 'root' and will configure the package to
        install either to the user's home directory, or to the system
        wide haskell.

        Some help is needed making this more flexible
        '''
        raise NotImplementedError

    def build(self, *args):
        '''runs the build stage of cabal

        This is not safe to run on an unconfigured source dir, because
        this module does not track the state of cabal systems. The user
        must do this on their own.
        '''
        raise NotImplementedError

    def install(self, *args):
        '''runs the install stage of cabal

        This is not safe to run on an unconfigured source dir, because
        this module does not track the state of cabal systems. The user
        must do this on their own.
        '''
        raise NotImplementedError

    def install_source(self, target='home', *args):
        '''perform configure, build, and install steps in one
        '''
        raise NotImplementedError

    def gen_spec(self, name):
        raise NotImplementedError

    @contextmanager
    def logged(self, name=""):
        with log_file(join(self.pkg_src.pkg_src_dir, 
                           (name if name else self._type) + '.log')) \
                as log_out:
            yield log_out
