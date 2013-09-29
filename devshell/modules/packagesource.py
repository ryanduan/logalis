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

from contextlib import contextmanager
from os import makedirs
from os.path import join

from devshell.base.factories import BuildSystemFactory
from devshell.base.util import pwd

from devshell.modules.directory import Directory

class PackageSource(Directory):
    def make_dir(self, dir):
        super(PackageSource, self).make_dir(dir)
        with pwd(dir):
            makedirs(self.pkg_src)
            makedirs(self.branches)

    @property
    def pkg_src(self):
        return '.pkg_src'
    
    @property
    def pkg_src_dir(self):
        return join(self.dir, self.pkg_src)

    @contextmanager
    def in_pkg_src_dir(self):
        with pwd(self.pkg_src_dir):
            yield

    @property
    def branches(self):
        return join(self.pkg_src, 'branches')

    @property
    def branches_dir(self):
        return join(self.dir, self.branches)

    @contextmanager
    def in_branches_dir(self):
        with pwd(self.branches_dir):
            yield

    @property
    def sourceball(self):
        return self.cfg['sourceball']
    
    @property
    def sourceball_loc(self):
        return join(self.pkg_src_dir, self.sourceball)

    @property
    def upstream_name(self):
        '''what is the canonical name
        '''
        return self.cfg['upstream_name']

    @property
    def full_name(self):
        return self.cfg['full_name']

    def setup_sourceball(self, ver=''):
        raise NotImplementedError

    def setup_sourceball_w_patches(self, ver=''):
        raise NotImplementedError

    @property
    def source(self):
        '''the name of the directory where the source is being kept currently
        '''
        return self.cfg['source']

    @property
    def source_dir(self):
        '''the absolute pathname of the directory where the source is being kept currently
        '''
        return join(self.dir, self.source)

    @contextmanager
    def src_dir(self, *args):
        '''executes a code block inside a specific branch and or checkout
        '''
        with self.src(*args):
            with self.in_src_dir():
                yield

    @contextmanager
    def in_src_dir(self):
        with pwd(self.source_dir):
            yield

    @contextmanager
    def src(self, *args):
        '''executes a code block with a particular branch or checkout

        if there are no args, this block is executed in the raw
        '''
        if args:
            old_src = self.cfg['source']
            self.set_cur_to(*args)
        yield
        if args:
            self.cfg['source'] = old_src
            self.set_current_src()

    def set_current_src(self):
        raise NotImplementedError

    def set_cur_to(self, *args):
        raise NotImplementedError

    def branch(self, *args):
        raise NotImplementedError

    def branch_dir(self, *args):
        return join(self.dir, self.branch(*args))

    @property
    def buildsystem(self):
        return self.cfg['buildsystem']

    def set_buildsystem(self, buildsystem):
        self.cfg['buildsystem'] = buildsystem

    @property
    def builder(self):
        return BuildSystemFactory(self.buildsystem, self)
