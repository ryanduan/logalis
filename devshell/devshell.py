#!/usr/bin/python -tt
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
# TODO:
# - query pkgdb
# - view all branch versions, and easily move versions between branches
# - List available bugzillas.. give the ability to view/control all bugs of theirs or for any component in any of the bugzillas

# v0.1 release
# - fedora-qa!!!!
# - push updates to bodhi
# - koji building/querying
# - query versions of any package, drop into its code, view patches
# - Ability to grep mailing lists and even IRC (?!)
# - readline support@!
# - audit <project> (flawfinder/rats/etc)

import os

from base.base import load_modules, shell, setup_logger, setup_options, log
from devshell.base.vars import FEDORA_DIR

def main():
    (opts, args) = setup_options()

    setup_logger(opts)

    if not os.path.isdir(FEDORA_DIR):
        log.info("Creating %s" % FEDORA_DIR)
        os.makedirs(FEDORA_DIR)

    load_modules()
    shell()
    
if __name__ == '__main__':
    main()
