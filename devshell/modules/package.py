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

from os.path import basename, abspath, join
from contextlib import contextmanager

from devshell.base.base import log
from devshell.base.factories import DirFactory
from devshell.base.exceptions import ExecutionException
from devshell.base.util import pwd, copy, move, symlink, rm
from devshell.base.rpm_utils import RPMSpec

from devshell.modules.directory import Directory

class Package(Directory):
    # These two methods are here as examples.
    def load_dir(self, dir):
        super(Package, self).load_dir(dir)
        self._check_sources()

    def make_dir(self, dir):
        super(Package, self).make_dir(dir)
        self._check_sources()

    @contextmanager
    def rpm_obj(self, *args):
        with pwd(self.dir):
            yield RPMSpec(*args)
        
    def _check_sources(self):
        '''necessary to make sure self.sources is a list
        '''
        if 'sources' not in self.cfg:
            self.cfg['sources'] = list()
        elif type(self.sources) is not list:
            log.warn('sources for this package is not a list, overwriting!')
            log.info('sources was, fyi, ' + str(self.sources))
            self.cfg['sources'] = list()

    def add_spec(self, spec_file):
        '''add's a spec file to the package, and sets the canonical package
        name based on the spec file, possibly renaming the spec file to match
        within fedora guidelines'''
        log.debug('spec_file is %s' % spec_file)
        log.debug('spec_file_name is %s' % self.name + '.spec')
        #TODO: get the spec file name, copy
        # Then get the actual package name and set pkg_name to the right one
        spec_file = abspath(spec_file)
        spec_fname = basename(spec_file)
        with pwd(self.dir):
            try:
                copy(spec_file, spec_fname)
                rpm = RPMSpec(spec_fname)
                self.cfg['pkg_name'] = rpm.name()
                if not spec_fname == self.spec_file:
                    move(spec_fname, self.spec_file)
            except IOError, e:
                log.error(str(e))
                raise ExecutionException(e, 'spec-file could not be added')

    @property
    def spec_file(self):
        '''returns the name of the spec file as it should be accordingto
        fedora guidelines, good for double checking'''
        return self.pkg_name + '.spec'

    @property
    def pkg_name(self):
        '''canonical name of the package in a source repository'''
        return self.cfg['pkg_name']

    def set_pkg_name(self, name):
        self.cfg['pkg_name'] = name

    def get_srpm_name(self, profile):
        '''given a profile, determines that the source rpm should be called'''
        with self.rpm_obj(self.spec_file, profile.dist_defines) as rpm:
            ver, rel = rpm.ver_rel()
            return '%s-%s-%s.src.rpm' % (self.pkg_name, ver, rel)

    def ver(self, profile=None):
        '''given a profile, determines the version of the current spec file'''
        with self.rpm_obj(self.spec_file, profile.dist_defines if profile else '') as rpm:
            return rpm.version()

    def set_ver(self, version):
        with self.rpm_obj(self.spec_file) as rpm:
            rpm.set_version(version)

    def set_alphatag(self, alphatag):
        with self.rpm_obj(self.spec_file) as rpm:
            rpm.set_alphatag(alphatag)

    def set_alphatag_pri_src(self):
        self.set_alphatag(self.primary_source_pkg.alphatag)

    def inc_rel(self):
        with self.rpm_obj(self.spec_file) as rpm:
            rpm.increment_release()

    def bump_rel(self, entry, email):
        with self.rpm_obj(self.spec_file) as rpm:
            rpm.bump_release(entry, email)

    @property
    def sources(self):
        return self.cfg['sources']

    def copy_source(self, source_dir):
        source = DirFactory(source_dir)
        target_dir = join(self.dir, source.name)
        if not source.dir == target_dir:
            source.copy(target_dir)
        self.add_source(source_dir)

    def move_source(self, source_dir):
        source = DirFactory(source_dir)
        target_dir = join(self.dir, source.name)
        if not source.dir == target_dir:
            source.move(target_dir)
        self.add_source(source_dir)

    def add_source(self, source_dir):
        source = DirFactory(source_dir)
        if not source.name in self.sources:
            self.cfg['sources'].append(source.name)

    def rem_source(self, source):
        self.cfg['sources'].remove(source)

    def del_source(self, source):
        self.rem_source(source)
        with pwd(self.dir):
            rm(source)

    def set_primary_source(self, source_dir):
        source = DirFactory(source_dir)
        self.add_source(source_dir)
        self.cfg['primary_source'] = source.name
        self.get_spec_from_source(source_dir)

    @property
    def primary_source(self):
        return self.cfg['primary_source']

    @property
    def primary_source_pkg(self):
        return DirFactory(self.primary_source)

    def fetch_sourceballs(self, profile=None, regen=True):
        pkg_srcen = self.sources
        pkg_srcen = (DirFactory(pkg_src) for pkg_src in pkg_srcen)
        self.cfg['sourceballen'] = list()
        with pwd(self.dir):
            for pkg_src in pkg_srcen:
                if regen:
                    pkg_src.setup_sourceball(self.ver(profile))
                symlink(pkg_src.sourceball_loc, pkg_src.sourceball)
                self.cfg['sourceballen'].append(pkg_src.sourceball)
                pkg_src.close()


    @property
    def sourceballen(self):
        return self.cfg['sourceballen']

    def spec_sources(self):
        with self.rpm_obj(self.spec_file) as rpm:
            return rpm.sources()

    def spec_all_sources(self):
        return [basename(source[0]) for source in self.spec_sources()]

    def spec_just_sources(self):
        return [source[0] for source in self.spec_sources() if source[2] == 1]

    def spec_patches(self):
        return [source[0] for source in self.spec_sources() if source[2] == 2]


    @property
    def port(self):
        return self.cfg['port']

    def set_port(self, port):
        #TODO: Check for valid port
        self.cfg['port'] = port

    def get_spec_from_source(self, source_dir, file_name=None):
        source = DirFactory(source_dir)
        if not file_name:
            file_name = join(source.source_dir, self.spec_file)
        else:
            file_name = join(source.source_dir, file_name)
        with self.in_dir():
            symlink(file_name, self.spec_file)

__all__ = ['Package']
