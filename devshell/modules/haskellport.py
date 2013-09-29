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

from devshell.base.util import pwd

from devshell.modules.cabal import Cabal
from devshell.modules.darcs import Darcs
from devshell.modules.hackage import Hackage
from devshell.modules.port import Port
from devshell.modules.sourceball import SourceBall

class HaskellPort(Port):
    sourceball = SourceBall
    revision_control = Darcs
    builder = Cabal
    fetcher = Hackage
    
    def install_tag(self, tag):
        '''assuming a package that supports tagging, install a specific tag

        tag is the name of the tag in the DVCS
        '''
        with pwd(self.package.dir):
            with self.package.tag(tag):
                self.install()
