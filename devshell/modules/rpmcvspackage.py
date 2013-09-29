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

import os

from copy import copy
from os import environ
from os.path import join
from subprocess import Popen
from shutil import move
from tempfile import mkdtemp

from devshell.base.base import log
from devshell.base.util import pwd, log_file, copytree

from devshell.modules.package import Package

CVSROOT = ':pserver:anonymous@cvs.fedoraproject.org:/cvs/pkgs'

class RpmCvsPackage(Package):
    def __init__(self, name=None, fedora_name=None):
        if fedora_name:
            if not name:
                name = fedora_name
            tmp_dir = mkdtemp()
            with pwd(tmp_dir):
                env = copy(environ)
                env['CVSROOT'] = CVSROOT
                cmd = ['cvs', 'co', fedora_name]
                with log_file('cvs.log') as cvs_log:
                    p = Popen(cmd, stdout=cvs_log, stderr=cvs_log,
                              env=env)
                    log.info('Fetching full source from CVS... please wait...')
                    p.communicate()

                with pwd(join(fedora_name, 'common')):
                    with file('branches', 'r') as branches:
                        branches = (branch for branch in branches if ':' in branch)
                        branches = (branch.split(':')[0] for branch in branches)
                        branches = list(branches)
                with pwd(fedora_name):
                    p_branches = os.listdir('.')
                    v_branches = (branch for branch in branches if branch in p_branches)
                    v_branches = list(v_branches)
                for branch in v_branches:
                    dir_name = fedora_name + '.' + branch
                    cvs_branch = join(fedora_name, branch)
                    cmd = ['git', 'cvsimport', '-o', branch, '-C', dir_name, cvs_branch]
                    with log_file('cvs.log') as cvs_log:
                        p = Popen(cmd, stdout=cvs_log, stderr=cvs_log,
                                  env=env)
                        log.info('Fetching partial source from CVS for %s... please wait...' % branch)
                        p.communicate()
                non_devel_v_branches = (branch for branch in v_branches if branch is not 'devel')
                for branch in non_devel_v_branches:
                    dir_name = fedora_name + '.' + branch
                    cvs_branch = join(fedora_name, branch)
                    refspec = branch + ':' + branch
                    cmd = ['git', 'fetch', join(tmp_dir, dir_name), refspec]
                    with log_file('cvs.log') as cvs_log:
                        with pwd(fedora_name + '.devel'):
                            p = Popen(cmd, stdout=cvs_log, stderr=cvs_log,
                                      env=env)
                            log.info('Combining CVS sources for %s ... please wait...' % branch)
                            p.communicate()

            move(join(tmp_dir, fedora_name + '.devel'), name)
            move(join(tmp_dir, fedora_name), join(name, '.fedora_cvs'))
            move(join(tmp_dir, 'cvs.log'), join(name, 'cvs.log'))
        super(RpmCvsPackage, self).__init__(name)
        if fedora_name:
            self.cfg['branches'] = v_branches
            self.cfg['pkg_name'] = fedora_name

    @property
    def branches(self):
        return self.cfg['branches']

    def add_branch(self, branch):
        if branch not in self.branches:
            self.cfg['branches'].append(branch)
