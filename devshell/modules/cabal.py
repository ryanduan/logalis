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

class Cabal(BuildSystem):
    '''A wrapper around common cabal operations

    This provides a useful api for other modules around the cabal build system
    '''
    def __init__(self, name):
        '''creates a new cabal module

        this api is deprecated, because it should be more autodetecting

        name is a Package (Directory) that uses cabal for its build system
        '''
        super(Cabal, self).__init__(name)
        self.compiler = haskell_compiler

    def find_setup(self):
        '''returns the name of the Setup.?hs script for cabal.
        '''
        setup_re = compile("Setup\.l?hs")
        with self.pkg_src.src_dir():
            return one(listdir(getcwd()), setup_re.search)

    def compile_setup(self, *args):
        '''compiles the setup script for faster execution
        '''
        with self.logged('ghc') as ghc_out:
            with self.pkg_src.in_src_dir():
                setup_f = self.find_setup()
                p = Popen([self.compiler, '--make', setup_f] + list(args),
                          stdout=ghc_out, stderr=ghc_out)
                log.info('Building %s, please wait...' % setup_f)
                p.communicate()

    def configure(self, target='home', *args):
        '''runs the configure stage of cabal
        
        target is either 'home' or 'root' and will configure the package to
        install either to the user's home directory, or to the system
        wide haskell.

        Some help is needed making this more flexible
        '''
        user = True if target == 'home' else False
        self.compile_setup()
        with self.logged() as cabal_out:
            with self.pkg_src.in_src_dir():
                cmd = [abspath('Setup'), 'configure'] \
                    + (['--user', '--prefix=' + expanduser('~')] if user else []) \
                    + list(args)
                p = Popen(cmd, stdout=cabal_out, stderr=cabal_out)
                log.info('Configuring %s, please wait...' % self.name)
                p.communicate()

    def build(self, *args):
        '''runs the build stage of cabal

        This is not safe to run on an unconfigured source dir, because
        this module does not track the state of cabal systems. The user
        must do this on their own.
        '''
#         with self.pkg_src.src(*args):
        self.compile_setup()
        with self.logged() as cabal_out:
            with self.pkg_src.in_src_dir():
                cmd = [abspath('Setup'), 'build'] + list(args)
                p = Popen(cmd, stdout=cabal_out, stderr=cabal_out)
                log.info('Building %s, please wait...' % self.name)
                p.communicate()

    def install(self, *args):
        '''runs the install stage of cabal

        This is not safe to run on an unconfigured source dir, because
        this module does not track the state of cabal systems. The user
        must do this on their own.
        '''
        self.compile_setup()
        with self.logged() as cabal_out:
            with self.pkg_src.in_src_dir():
                cmd = [abspath('Setup'), 'install'] + list(args)
                p = Popen(cmd, stdout=cabal_out, stderr=cabal_out)
                log.info('Building %s, please wait...' % self.name)
                p.communicate()
    
    def install_source(self, target='home', *args):
        '''perform configure, build, and install steps in one
        '''
#         with self.pkg_src.src(*args):
        self.configure(target)
        self.build()
        self.install()

    def gen_spec(self, name):
        cabal_file = name + '.cabal'
        with self.logged('cabal2spec') as c2s_log:
            with self.pkg_src.in_dir():
                cmd = ['cabal2spec', cabal_file]
                p = Popen(cmd, stdout=c2s_log, stderr=c2s_log)
                log.info('Generating spec file for %s' % cabal_file)
                p.communicate()

    def close(self):
        self.pkg_src.close()

__all__ = ['Cabal']
