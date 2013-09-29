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

from os.path import join
from subprocess import Popen, PIPE

from devshell.base.base import log
from devshell.base.vars import FEDORA_DIR
from devshell.base.util import flatten

TARGET = 0
DIST = 1
DISTVAR = 2
DISTVAL = 3

def distdef(dist):
    return dist.replace('.', '')

def define(key, value):
    return ['-D', '%s %s' % (key, value)]

def join_defines(*defines):
    return flatten(defines)

def dist_defines(dist, distvar, distval):
    _dist = define('dist', dist)
    _distvar = define(distvar, distval)
    _distdef = define(distdef(dist), 1)
    return join_defines([_dist, _distvar, _distdef])

head_branch = 'devel'

def get_mock_cfg(distvar, distval, buildarch):
    if distvar == 'fedora' and distval in [4, 5, 6]:
        return '%s-%s-%s-core' % (distvar, distval, buildarch)
    else:
        return '%s-%s-%s' % (distvar, distval, buildarch)

def dir_defines(some_dir):
    defs = list()
    defs.append(define('_sourcedir', join(some_dir, 'SOURCES')))
    defs.append(define('_specdir', join(some_dir, 'SPECS')))
    defs.append(define('_builddir', join(some_dir, 'BUILD')))
    defs.append(define('_srcrpmdir', join(some_dir, 'SRPMS')))
    defs.append(define('_rpmdir', join(some_dir, 'RPMS')))
    return join_defines(defs)

#taken from CVS for now
distro = {'RHL-7':('rhl7','.rhl7','rhl','7'),
          'RHL-8':('rhl8','.rhl8','rhl','8'),
          'RHL-9':('rhl9','.rhl9','rhl','9'),
          'OLPC-2':('dist-olpc2','.olpc2','olpc','2'),
          'OLPC-3':('dist-olpc3','.olpc3','olpc','3'),
          'EL-4':('el4','.el4','epel','4'),
          'EL-5':('el5','.el5','epel','5'),
          'FC-1':('fc1','.fc1','fedora','1'),
          'FC-2':('fc2','.fc2','fedora','2'),
          'FC-3':('fc3','.fc3','fedora','3'),
          'FC-4':('fc4','.fc4','fedora','4'),
          'FC-5':('fc5','.fc5','fedora','5'),
          'FC-6':('fc6','.fc6','fedora','6'),
          'F-7':('dist-fc7','.fc7','fedora','7'),
          'F-8':('dist-f8','.fc8','fedora','8'),
          'F-9':('dist-f9','.fc9','fedora','9'),
          'F-10':('dist-f10','.fc10','fedora','10'),
          'F-11':('dist-f11','.fc11','fedora','11'),
          'devel':('dist-devel','.devel','fedora','rawhide')}

# this class is temporary, it's only for mimickng CVS for now
# later we'll come up with a better way to do custom profiles
class Profile(object):
    def __init__(self, branch):
        self.branch = branch
        self.distro = distro[branch]
    
    @property
    def dist_defines(self):
        d = self.distro
        return dist_defines(d[DIST], d[DISTVAR], d[DISTVAL])
    
    @property
    def mock_cfg(self):
        d = self.distro
        # TODO: buildarchs need to be handled somehow
        # yes i'm lame and i did this i386 only for now
        return get_mock_cfg(d[DISTVAR], d[DISTVAL], 'i386')
    
    @property
    def config_dir(self):
        return '/etc/mock'
    
    @property
    def result_dir(self):
        return FEDORA_DIR
    

def main():
    print distdef('.fc9')
    print ver_rel('ghc-X11.spec', '')
    
if __name__ == '__main__':
    main()
    
__all__ = ['TARGET', 'DISTVAR', 'distdef', 'DISTVAL', 'head_branch',
           'DIST', 'join_defines', 'ver_rel', 'define',
           'dir_defines', 'get_mock_cfg', 'dist_defines',
           'Profile']
