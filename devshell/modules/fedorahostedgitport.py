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

from devshell.base.module import Module
from devshell.base.util import pwd

from devshell.modules.fedorahostedgitfetcher import FedoraHostedGitFetcher
from devshell.modules.git import Git
from devshell.modules.port import Port
from devshell.modules.sourceball import SourceBall

class Foo(Module):
    _type = 'foo'

class FedoraHostedGitPort(Port):
    sourceball = SourceBall
    revision_control = Git
    builder = Foo
    fetcher = FedoraHostedGitFetcher
