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

class Module(object):
    """ Our parent class for all command modules """
    def close(self):
        raise NotImplementedError
    
    def __call__(self, *args):
        '''This is needed for those command line calls that have no target

        TODO: This is a bloody stupid hack that should be taken out back and shot
        '''
        return
