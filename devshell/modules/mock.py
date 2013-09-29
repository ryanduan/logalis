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

from subprocess import Popen

from devshell.base.base import log
from devshell.base.factories import DirFactory
from devshell.base.module import Module
from devshell.base.util import pwd, log_file

from devshell.modules.build import Build
from devshell.modules.package import Package
from devshell.modules.profile import Profile

class Builder(Module):
    pass

class Mock(Builder):
    '''wrapper around mock for integrating with profiles and packages'''
    def __init__(self, profile, build):
        '''initializer

        profile is a path to a profile directory
        build is a path to a buildroot directory
        '''
        self.builder = Build(build)
        self.profile = Profile(profile)

    def build(self, package):
        pkg = DirFactory(package)

        srpm_name = pkg.get_srpm_name(self.profile)
        mock_cfg = self.profile.mock_cfg
        result_dir = self.profile.result_dir
        config_dir = self.profile.mock_cfg_dir
        log.debug('mock_cfg is ' + mock_cfg)
        log.debug('result_dir is ' + result_dir)
        log.debug('config_dir is ' + config_dir)
        cmd = ['mock', '-r', mock_cfg,
               '--configdir=%s' % config_dir,
               '--resultdir=%s' % result_dir,
               srpm_name]
        log.debug('cmd is ' + str(cmd))
        with pwd(result_dir):
            with log_file('mock.log') as mock_out:
                p = Popen(cmd, stdout=mock_out, stderr=mock_out)
                log.info('mock compiling %s... please wait' % srpm_name)
                p.communicate()

    def build_rpm(self, package):
        '''builds an rpm from some package'''
        pkg = DirFactory(package)

        self.builder.setup_source(package)
        self.builder.build_source_rpm(package, self.profile)
        self.builder.fetch_rpms(self.profile.result_dir)

        self.build(package)

    def close(self):
        self.builder.close()
        self.profile.close()

__all__ = ['Mock']
