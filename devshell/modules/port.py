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

import tarfile

from os import getcwd
from tempfile import mkdtemp
from contextlib import contextmanager

from devshell.base.base import log
from devshell.base.exceptions import ExecutionException
from devshell.base.factories import DirFactory
from devshell.base.util import pwd, close_later, close_all, rm

from devshell.base.module import Module

from devshell.modules.sourceball import SourceBall
from devshell.modules.build import Build
from devshell.modules.profile import Profile
from devshell.modules.mock import Mock

class Port(Module):
    def __init__(self, package=None):
        if not package:
            package = getcwd()
        self.pkg = DirFactory(package)

    @property
    def sourceball(self):
        raise NotImplementedError

    @property
    def revision_control(self):
        raise NotImplementedError

    @property
    def builder(self):
        raise NotImplementedError

    @property
    def fetcher(self):
        raise NotImplementedError

    def add_sourceball(self, sourceball):
        '''copies a tarball into the package

        tarball is a path to some tarball
        '''
        with pwd(self.pkg.dir):
            pkg_src = self.sourceball('', sourceball)
            pkg_src.set_buildsystem(self.builder._type)
            name = pkg_src.name
            self.pkg.add_source(name)
        return close_later(pkg_src)

    def add_vcs(self, url, tgt, *args):
        '''creates a darcs variant of a cabal package using darcs source

        url is a url to some darcs repo
        tgt is the local name of the darcs repo
        '''
        with pwd(self.pkg.dir):
            pkg_src = self.revision_control(tgt, url, *args)
            pkg_src.set_buildsystem(self.builder._type)
            name = pkg_src.name
            self.pkg.add_source(name)
        return close_later(pkg_src)

    def install_sourceball(self, tarball, target='home', *args):
        '''given a tarball, copy it in and install it
        '''
        pkg_src = self.add_sourceball(tarball)
        self.builder(pkg_src).install_source(target, *args)

    def add_from_release(self, pkg, ver):
        '''get a specific package from hackage

        pkg is the name of the package desired
        ver is the version wanted
        '''
        sb_loc = self.fetcher().url(pkg, ver)
        sb = self.add_sourceball(sb_loc)
        sb.cfg['release_name'] = pkg
        return sb

    def add_latest(self, pkg):
        '''get the latest version of a package from hackage

        pkg is the package desired
        '''
        ver = self.fetcher().latest_version(pkg)
        return self.add_from_release(pkg, ver)

    def install_from_release(self, pkg, ver, target='home', *args):
        '''get and install a specific package from hackage

        pkg is the desired package
        ver is the version wanted
        target is the location to install to, either 'home' or 'root'
        '''
        sb_loc = self.fetcher().url(pkg, ver)
        self.install_sourceball(sb_loc, target, *args)

    def install_latest(self, pkg, target='home', *args):
        '''get and install the latest version of a package from hackage'''
        ver = self.fetcher().latest_version(pkg)
        self.install_from_release(pkg, ver, target, *args)

    def add_upstream(self, pkg, tgt=None, *args):
        if not tgt:
            tgt = pkg
        return self.add_vcs(self.fetcher().vcs_url(pkg), tgt, *args)

    def install_upstream(self, pkg, tgt=None, target='home', *args):
        pkg_src = self.add_upstream(pkg, tgt, *args)
        self.builder(pkg_src).install_source(target)


    def prepare_sourceballs(self, install=False, force=False, *args):
        tmp_dir = mkdtemp()
        pkg_srcen = self.pkg.sources
        pkg_srcen = (DirFactory(pkg_src) for pkg_src in pkg_srcen)
        with self.pkg.in_dir():
            for pkg_src in pkg_srcen:
                with pwd(tmp_dir):
                    sourceball = SourceBall(pkg_src.full_name, pkg_src.sourceball_loc)
                    builder = self.builder(sourceball)
                    builder.prepare(install, force, *args)
                    rm(sourceball.pkg_src_dir)
                    tar_file = tarfile.open(pkg_src.sourceball_loc, 'w:gz')
                    tar_file.add(pkg_src.full_name)
                    tar_file.close()
        rm(tmp_dir)

    def build_source_rpm(self, build, profile):
        builder = Build(build)
        profile = Profile(profile)
        builder.setup_source(self.pkg.dir)
        self.prepare_sourceballs()
        builder.build_source_rpm(self.pkg.dir, profile)
        builder.fetch_rpms(profile.result_dir)


    def build_binary_rpm(self, build, profile):
        mock = Mock(profile, build)
        mock.build(self.pkg.dir)


    def build_rpm(self, build, profile):
        self.build_source_rpm(build, profile)
        self.build_binary_rpm(build, profile)

    def close(self):
        self.pkg.close()
        close_all()
