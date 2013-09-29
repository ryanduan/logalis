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

from contextlib import contextmanager
from os import makedirs, getcwd, listdir
from os.path import abspath, split, basename, join
from shutil import copytree
from subprocess import Popen, PIPE
from tempfile import mkdtemp

from devshell.base.base import log
from devshell.base.exceptions import ExecutionException
from devshell.base.util import pwd, copy, move, base_dir, log_file, rm
from devshell.base.vars import DIFF_EXCLUDES_FILE

from devshell.modules.packagesource import PackageSource

# 4's what git uses
# if we go over 4 digits, then weird stuff will happen
# but if we go over 4 digits, we're probably doing packaging wrong
# TODO: decide if this should be a hardcode constant or what
patch_num_len = 4

class SourceBall(PackageSource):
    '''a type of package that is a single sourceball, a spec file, and some patches'''
    def __init__(self, name=None, tarball=''):
        if tarball:
            tmp_dir = mkdtemp()
            with pwd(tmp_dir):
                sourceball_name = copy(tarball, split(tarball)[1])
                log.debug('sourceball_name ' + sourceball_name)
                sourceball = tarfile.open(sourceball_name)
            extract_dir = base_dir(sourceball)
            if name and not name == extract_dir:
                log.debug('hahahahhaah')
                raise ExecutionException("tarball is not target directory")
            if not name:
                name = extract_dir
        super(SourceBall, self).__init__(name)
        if tarball:
            self.cfg['tarball_source'] = tarball
            with pwd(self.parent):
                sourceball.extractall()
            with pwd(self.branches_dir):
                sourceball.extractall()
                move(self.name, self.orig_dir(self.name))
            with pwd(self.pkg_src_dir):
                move(join(tmp_dir, sourceball_name), sourceball_name)
            self.cfg['sourceball'] = sourceball_name
            self.set_cur_to('head')

    def orig_dir(self, dir):
        '''where is the original source kept

        use for making patches against modified source'''
        return dir + '_orig'

    def branch(self, *args):
        if len(args) == 1 and args[0] == 'orig':
            return join(self.branches, self.orig_dir(self.name))

    def set_cur_to(self, *args):
        '''gives source directory

        first parameter, if 'orig' gives the original source, otherwise
        you get the modified source
        '''
        if len(args) == 1 and args[0] == 'head':
            self.cfg['source'] = '.'
        else:
            self.cfg['source'] = self.branch(arg[0])


    @property
    def cur_patch_num(self):
        if len(self.patches):
            return max(int(basename(pfname)[:patch_num_len]) for pfname in self.patches)
        else:
            return 0

    @property
    def next_patch_num(self):
        next =  str(self.cur_patch_num + 1)
        while len(next) < patch_num_len:
            next = '0' + next
        return next

    @contextmanager
    def do_diff(self, src, tgt):
        cmd = ['diff', '-r', '-u', '-X', DIFF_EXCLUDES_FILE,
               src, tgt]
        with pwd(self.pkg_src_dir):
            with log_file('diff.log') as diff_out:
                def command(fd):
                    p = Popen(cmd, stdout=fd, stderr=diff_out)
                    log.info('generating patch %s, please wait...'
                             % fd.name)
                    p.communicate()
                yield command
        
    def generate_patch(self, patch_name):
        prefix = self.next_patch_num + '.'
        patch_name = patch_name + '.patch' if not patch_name.endswith('.patch') else patch_name
        patch_name = prefix + patch_name
        log.debug('patch_name ' + patch_name)
        with self.patches_applied('orig'):
            with self.do_diff(self.branch('orig'), '.') as diff:
                with pwd(self.dir):
                    with file(join(self.pkg_src_dir, patch_name), 'w') as patch_file:
                        diff(patch_file)
            # We have to do this last step because of the context manager
            # it assumes that this last patch has also been applied
            patch_name = join(self.pkg_src_dir, patch_name)
            with pwd(self.branch_dir('orig')):
                self.apply_patch(patch_name)

    @contextmanager
    def patches_applied(self, *args):
        self.apply_patches(*args)
        yield
        self.remove_patches(*args)

    def setup_sourceball(self, ver=''):
        return

    def setup_sourceball_w_patches(self, ver=''):
        raise NotImplementedError

    def clean_orig(self):
        with pwd(self.pkg_src_dir):
            sourceball = tarfile.open(self.sourceball)
        with pwd(self.branches_dir):
            rm(self.orig_dir(self.name))
            sourceball.extractall()
            move(self.name, self.orig_dir(self.name))

    @property
    def patches(self):
        with pwd(self.pkg_src_dir):
            files = [abspath(f) for f in listdir('.') if f.endswith('.patch')]
        return files

    def do_patch(self, patch, cmd):
        with log_file(join(self.pkg_src_dir, 'patch.log')) as patch_log:
            patch_log.write('using patch %s...\n' % basename(patch))
            with file(patch, 'r') as pfile:
                p = Popen(cmd, stdin=pfile,
                          stdout=patch_log, stderr=patch_log)
                log.info('patching %s, please wait....' % basename(patch))
                p.communicate()

    def apply_patch(self, patch):
        self.do_patch(patch, ['patch', '-p0'])

    def remove_patch(self, patch):
        self.do_patch(patch, ['patch', '-p0', '-R'])

    def apply_patches(self, *args):
        with pwd(self.branch(*args)):
            for patch in sorted(self.patches):
                self.apply_patch(patch)

    def remove_patches(self, *args):
        with pwd(self.branch(*args)):
            for patch in list(reversed(self.patches)):
                self.remove_patch(patch)

    def import_other_patch(self, patch_file, patch_level):
        if type(patch_level) is int:
            patch_level = str(patch_level)
        cmd = ['patch', '-p' + patch_level]
        with pwd(self.dir):
            self.do_patch(patch_file, cmd)
        patch_name = basename(patch_file)
        self.generate_patch(patch_name)
    
    def verify_patches(self, *args):
        test_file = join(self.pkg_src_dir, 'test.patch.')
        with self.patches_applied(*args):
            with self.do_diff(self.branch('orig'), '.') as diff:
                with pwd(self.dir):
                    with file(test_file, 'w') as patch_file:
                        diff(patch_file)
        clean = False if len(file(test_file).read()) else True
        log.info('Verified clean patches: ' + str(clean))
        return clean

__all__ = ['SourceBall']
