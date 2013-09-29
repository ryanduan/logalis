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

from re import compile, DOTALL
from urllib import urlopen, urlretrieve

from devshell.modules.fetcher import Fetcher

USER = 'ynemoy'

class FedoraHostedGitFetcher(Fetcher):
    def latest_version(self, pkg):
        pass

    def url(self, pkg, ver):
        '''returns the url for tarball for a hackage package'''
        first = pkg[0]
        second = pkg[1]
        return 'https://fedorahosted.org/releases/' + first + '/' + second \
            + '/' + pkg + '/' + pkg + '-' + ver + '.tar.gz'

    def vcs_auth_url(self, pkg):
        return 'ssh://' + USER + '@git.fedorahosted.org/git/' + pkg

    def vcs_anon_url(self, pkg):
        return 'http://git.fedorahosted.org/git/' + pkg

    def vcs_url(self, pkg):
        return self.vcs_anon_url(pkg)
