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

class Hackage(Fetcher):
    def latest_version(self, pkg):
        '''download information from hackage to find out the latest version of a package
        '''
        hackage_title = compile(r'<title.*?>HackageDB: (.*)-(.*)</title.*?>', DOTALL)
        site = 'http://hackage.haskell.org/cgi-bin/hackage-scripts/package/' + pkg
        u = urlopen(site)
        page = u.read()
        match = hackage_title.search(page)
        groups = match.groups()
        print groups
        if pkg == groups[0]:
            return groups[1]
        else:
            raise ExecutionException("package does not match package name, can't determine version, sorry")

    def url(self, pkg, ver):
        '''returns the url for tarball for a hackage package'''
        return 'http://hackage.haskell.org/packages/archive/' + \
            pkg + '/' + ver + '/' + pkg + '-' + ver + '.tar.gz'

    def vcs_url(self, pkg):
        return 'http://darcs.haskell.org/' + pkg
