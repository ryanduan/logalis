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

from shutil import copyfileobj
from os.path import join, abspath, isfile
from os import listdir, getcwd, walk
from subprocess import Popen

from devshell.base.base import log
from devshell.base.factories import DirFactory
from devshell.base.exceptions import ExecutionException
from devshell.base.module import Module
from devshell.base.profiles import dir_defines, join_defines, dist_defines, Profile
from devshell.base.util import pwd, copy, symlink, move, log_file
from devshell.base.vars import FEDORA_DIR

from devshell.modules.directory import Directory
from devshell.modules.package import Package
from devshell.modules.profile import Profile

class Build(Directory):
    '''A wrapper around rpmbuild functions
    '''
    def setup_source(self, package):
        '''Given a package, set's it up in the buildroot for being built with rpmbuild

        package is a directory name to a Package (Directory).

        returns nothing
        '''
        pkg = DirFactory(package)
        with pwd(pkg.dir):
            symlink(pkg.spec_file,
                    join(self.dir, 'SPECS', pkg.spec_file))
            pkg.fetch_sourceballs()
            for source in pkg.spec_all_sources():
                log.debug(source)
                symlink(source, join(self.dir, 'SOURCES', source))

    def build_quick_rpm(self, package, profile=None):
        '''Builds an rpm on the local system using rpmbuild (aka no clean chroots)
 
        This method may be useful in determining the difference between 
        a chroot and the working system. It can also help make sure the 
        package can be built in the first place, and quickly.
 
        package is a directory name to a Package (Directory).
        profile is a Profile object, this parameter should only be used internally
 
        returns nothing
        '''
        self.rpmbuild('-ba', package, profile)

    def build_source_rpm(self, package, profile=None):
        '''Builds an source rpm on the local system using rpmbuild
 
        This method is necessary to build SRPMs for many other modules.
        The user may find that certain dist related macros in the RPM are 
        set to the system wide defaults. The parameter 'profile' is used heavily
        internally to mimic aspects of the Fedora Build system in order 
        override the defaults. Without the assistance of other modules
        that are profile aware, profile makes no sense here.

        package is a directory name to a Package (Directory).
        profile is a Profile object, this parameter should only be used internally
 
        returns nothing
        '''
        self.rpmbuild('-bs', package, profile)

    def rpmbuild(self, param, package, profile=None):
        '''The work horse of building rpms

        Given a directive param for rpmbuild, the package, and a possible
        profile, it runs rpmbuild appropriatly.

        package is a directory name to a Package (Directory).
        profile is a Profile object, this parameter should only be used internally
 
        returns nothing
        '''
        pkg = DirFactory(package)
        log.debug(package)
        log.debug(pkg)
        if profile:
            defines = join_defines(profile.dist_defines,
                                   dir_defines(self.dir))
        else:
            defines = dir_defines(self.dir)
        log.debug('defines are ' + str(defines))
        log.debug('spec file is ' + pkg.spec_file)
        cmd = ['rpmbuild'] + defines + ['-v', param, pkg.spec_file]
        log.debug('cmd is ' + str(cmd))
        with pwd(pkg.dir):
            with log_file('rpmbuild.log') as rpm_out:
                with pwd(join(self.dir, 'SPECS')):
                    p = Popen(cmd, stdout=rpm_out, stderr=rpm_out)
                    log.info('building %s... please wait'
                             % pkg.spec_file)
                    p.wait()
                    log.debug(p.returncode)

    def fetch_rpms(self, target_dir):
        '''fetches all rpm files from the buildroot to another target directory

        As a module author, it is a good idea to use this to clean up
        afterwards. This module pulls all RPMs said module may have made
        as well as any other RPMs from earlier incantations of other modules.
        Please be courteous to other module authors and run this liberally.

        target_dir is a path to the destination for all the rpms
        '''
        target_dir = abspath(target_dir)
        with pwd(self.dir):
            for path, dirs, files in walk('.'):
                for f in files:
                    if f.endswith('.rpm'):
                        move(join(path, f), join(target_dir, f))

    def fetch_build(self, package):
        '''fetches the built source tree from the execution of rpmbuild for review

        This is usefull to see if rpmbuild did anything funny in execution
        of the spec file. Hopefully you'll never need this. The results
        end up in the top level directory of the given package

        package is a directory name to a Package (Directory).
        '''
        pkg = DirFactory(package)
        with pwd(self.dir):
            source = pkg.cfg['source']
            move(join('BUILD', source), join(pkg.dir, 'results'))

__all__ = ['Build']
