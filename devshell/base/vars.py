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
# Authors: Luke Macken <lmacken@redhat.com>
#          Yaakov M. Nemoy <ynemoy@redhat.com>
#
from os.path import join, expanduser

__version__ = '0.0.1'
__description__ = 'A shell for hacking on the Fedora project'

FEDORA_DIR = join(expanduser('~'), 'code')
DEVSHELL_DIR = join(expanduser('~'), '.devshell')
MOCK_CFG_DIR = '/etc/mock'

DIFF_EXCLUDES_FILE = '/home/yankee/Projekten/fedora-devshell/diff.excludes'

header = lambda x: "%s %s %s" % ('=' * 2, x, '=' * (76 - len(x)))
prompt = ['\033[34;1mfedora\033[0m']

orig_src_dir = '_orig'
haskell_compiler = 'ghc'
