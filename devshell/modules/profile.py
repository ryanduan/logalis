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

from devshell.base.exceptions import ExecutionException
from devshell.base.profiles import dist_defines, get_mock_cfg, distro, TARGET, DIST, DISTVAR, DISTVAL
from devshell.base.util import pwd, copytree
from devshell.base.vars import MOCK_CFG_DIR

from devshell.modules.directory import Directory

class Profile(Directory):
    '''a profile module to resemble various architectures, branches, build targets, etc...'''
    @property
    def dist(self):
        '''eg .fc7 or .olpc2
        used in rpmmacro %dist'''
        return self.cfg['dist']

    @property
    def distvar(self):
        '''eg: fedora or rhel'''
        return self.cfg['distvar']

    @property
    def distval(self):
        '''eg: 10 or 3 (string form)'''
        return self.cfg['distval']

    @property
    def koji_target(self):
        '''eg: dist-f11'''
        return self.cfg['koji_target']

    @property
    def dist_defines(self):
        '''a list of parameters for an rpm aware function to redefine 
        certain macros to match the profile'''
        return dist_defines(self.dist, self.distvar, self.distval)

    # i'm not sure this is 100% relevant, mock cfg's might be named only after the arch used
    @property
    def mock_cfg(self):
        '''the name of the mock config/profile to be used to compile packages for this profile

        this will probably change once we figure out how to handle branches and build targets better
        '''
        # TODO: buildarchs need to be handled somehow
        # yes i'm lame and i did this i386 only for now
        return get_mock_cfg(self.distvar, self.distval, 'x86_64')

    @property
    def mock_cfg_dir(self):
        '''directory where profile wide mock settings are kept'''
        return join(self.dir, 'mock')

    @property
    def result_dir(self):
        '''where to store results from mock'''
        return self.dir

    def configure_from_system(self, branch):
        '''sets up a profile based on system profiles

        branch is a branch name from the fedora-cvs
        '''
        self.cfg['branch'] = branch
        d = distro[branch]
        self.cfg['koji_target'] = d[TARGET]
        self.cfg['distval'] = d[DISTVAL]
        self.cfg['distvar'] = d[DISTVAR]
        self.cfg['dist'] = d[DIST]
        with pwd(self.dir):
            copytree(MOCK_CFG_DIR, self.mock_cfg_dir)
            
__all__ = ['Profile']
