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

from os import listdir, getcwd
from os.path import expanduser, expandvars, abspath

from re import compile, DOTALL

from subprocess import Popen

from devshell.base.base import log
from devshell.base.exceptions import ExecutionException
from devshell.base.factories import DirFactory
from devshell.base.util import pwd, one, log_file
from devshell.base.vars import orig_src_dir, haskell_compiler

from devshell.modules.buildsystem import BuildSystem
from devshell.modules.sourceball import SourceBall

class Autotools(BuildSystem):
    '''A wrapper around common autotools operations

    This provides a useful api for other modules around the autotools build system
    '''
    def __init__(self, name):
        '''creates a new autotools module

        this api is deprecated, because it should be more autodetecting

        name is a Package (Directory) that uses autotools for its build system
        '''
        super(Autotools, self).__init__(name)

    def prepare(self, install=False, force=False, *args):
        with self.logged() as autotools_out:
            with self.pkg_src.in_src_dir():
                print 'preparing'
                cmd = ['autoreconf'] \
                    + ['--install'] if install else [] \
                    + ['--force'] if force else [] \
                    + list(args)
                p = Popen(cmd, stdout=autotools_out, stderr=autotools_out)
                log.info('Preparing %s, please wait...' % self.name)
                p.communicate()



    def configure(self, target='home', *args):
        '''runs the configure stage of autotools
        
        target is either 'home' or 'root' and will configure the package to
        install either to the user's home directory, or to the system
        wide haskell.

        Some help is needed making this more flexible
        '''
        user = True if target == 'home' else False
        with self.logged() as autotools_out:
            with self.pkg_src.in_src_dir():
                cmd = [abspath('configure'),
                       '--prefix=' + expanduser('~') if user else target] \
                       + list(args)
                p = Popen(cmd, stdout=autotools_out, stderr=autotools_out)
                log.info('Configuring %s, please wait...' % self.name)
                p.communicate()

    def build(self, *args):
        '''runs the build stage of autotools

        This is not safe to run on an unconfigured source dir, because
        this module does not track the state of autotools systems. The user
        must do this on their own.
        '''
        with self.logged() as autotools_out:
            with self.pkg_src.in_src_dir():
                cmd = ['make'] + list(args)
                p = Popen(cmd, stdout=autotools_out, stderr=autotools_out)
                log.info('Building %s, please wait...' % self.name)
                p.communicate()

    def install(self, *args):
        '''runs the install stage of autotools

        This is not safe to run on an unconfigured source dir, because
        this module does not track the state of autotools systems. The user
        must do this on their own.
        '''
        with self.logged() as autotools_out:
            with self.pkg_src.in_src_dir():
                cmd = ['make', 'install'] + list(args)
                p = Popen(cmd, stdout=autotools_out, stderr=autotools_out)
                log.info('Installing %s, please wait...' % self.name)
                p.communicate()
    
    def install_source(self, target='home', *args):
        '''perform configure, build, and install steps in one
        '''
#         with self.pkg_src.src(*args):
        self.configure(target, orig)
        self.build(orig)
        self.install(orig)

    def gen_spec(self, name):
        spec_file = name + '.spec'
        with self.logged('rpmdevtools') as rdt_log:
            with self.pkg_src.in_dir():
                cmd = ['rpmdev-newspec', spec_file]
                p = Popen(cmd, stdout=rdt_log, stderr=rdt_log)
                log.info('Generating spec file for %s' % spec_file)
                p.communicate()

    def close(self):
        self.pkg_src.close()

__all__ = ['Autotools']
