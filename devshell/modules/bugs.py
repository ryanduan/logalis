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
#
import os
from devshell.base.module import Module

class Bugs(Module):
    """
    Interface for doing useful things with Bugs.
    TODO: add support for arbitrary bug trackers!
          python-bugzilla integration!
    """
    def view(self, data):
        """
        View a given bug number, or show all bugs for a given component
        Example: bugs view #1234, bugs view nethack
        """
        if data[0] == '#':
            os.system('firefox "https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=%s"' % data[1:])
        else:
            os.system('firefox "https://bugzilla.redhat.com/bugzilla/buglist.cgi?product=Fedora+Core&component=%s&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bug_status=MODIFIED&short_desc_type=allwordssubstr&short_desc=&long_desc_type=allwordssubstr&long_desc="' % data)

    def search(self, text):
        """
        Search bugzilla for a given keyword
        """
        os.system('firefox "https://bugzilla.redhat.com/buglist.cgi?query_format=specific&order=bugs.bug_id&bug_status=__open__&product=&content=%s"' % text)

__all__ = ['Bugs']
