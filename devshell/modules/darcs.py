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

import os
import re

from contextlib import contextmanager
from os import getcwd
from os.path import join, basename, exists
from subprocess import Popen, PIPE

from devshell.base.util import pwd, log, rm, log_file, copy, move
from devshell.modules.revisioncontrol import RevisionControl

hash_re = re.compile(r'hash=\'(\w|-|.*?)\'', re.MULTILINE)
date_re = re.compile(r'date=\'(\d*?)\'', re.MULTILINE)

class Darcs(RevisionControl):
    '''manages single source packages where the primary source is darcs
    '''
    def __init__(self, name=None, url=None, *args):
        if url:
            #split chokes on URLs that end in a /
            url = url[:-1] if url.endswith('/') else url
            tgt = basename(url)
            if not name:
                name = tgt
            self.get(url, tgt, *args)
        super(Darcs, self).__init__(name)
        if url:
            self.cfg['vc_url'] = url
            self.cfg['upstream_name'] = tgt
            self.cfg['source'] = '.'
            with pwd(self.branches_dir):
                self.get(self.dir, 'orig')
            self.set_current_src()


    def get(self, src, tgt, *args):
        '''sets up a branch given arguments, taken from a source with a target

        the idioms of branching in different VCSes vary, and a common
        api for this in devshell has not yet been realized

        currently, this creates a new temporary local branch in darcs
        and sets the source to it
        '''
        with log_file('darcs.log') as darcs_out:
            # NB: args is a tuple, must be converted
            p = Popen(['darcs', 'get'] + list(args) + [src, tgt],
                      stdout = darcs_out, stderr = darcs_out)
            log.info('darcs get %s %s, please wait....' % (src, tgt))
            p.communicate()

    @property
    def vc_url(self):
        '''the url where the source was fetched from originally

        this may be moved to revision control in the future
        '''
        return self.cfg['vc_url']

    def set_current_src(self):
        '''sets the current internal state to reflect the current head

        chances are, the user should rarely mess with this.

        this may change, because rather than using .patch files for rpm
        handling, we may ask the user to commit all the changes to darcs,
        and then have devshell generate .patch files automatically instead
        '''
        with pwd(self.source_dir):
            p = Popen(['darcs', 'changes', '--xml-output', '--last=1'],
                      stdout = PIPE, stderr = PIPE)
            change = p.communicate()[0]
            hash = hash_re.search(change).groups()[0]
            date = date_re.search(change).groups()[0]
            self.cfg['head'] = (hash, date)

    def set_cur_to(self, *args):
        '''passes arbitrary args to darcs get and makes a branch out of it

        this is not really optimal, because it only does things temporary,
        we need to look at as systematic way to handle branching.
        looking at a potential git and a potential cvs module may help
        '''
        if len(args) >= 2 and args[0] == 'new':
            branch_name = args[1]
            args = args[2:]
        else:
            branch_name = ''
        if len(args) == 1 and args[0] == 'head':
            log.debug('doing head')
            self.cfg['source'] = '.'
        elif len(args) == 2 and args[0] == 'branch':
            self.cfg['source'] = join(self.branches, args[1])
        else:
            log.debug('creating new branch')
            index = str(hash(args))
            index_dir = join(self.branches, index)
            with pwd(self.dir):
                if not exists(index_dir):
                    log.debug('index dir should be ' + index_dir)
                    self.get(self.source(), index_dir, *args)
                self.cfg['source'] = index_dir
            if branch_name:
                with pwd(self.branches_dir):
                    self.get(index, branch_name)
        self.set_current_src()

    def set_cur_to_patch(self, hash):
        '''sets the current branch to fork off a particular hash'''
        self.set_cur_to('--to-match', 'hash ' + hash)

    def set_cur_to_tag(self, tag):
        '''sets the current branch to fork off a particular tag'''
        self.set_cur_to('--tag', tag)

    @property
    def date(self):
        '''get's the timestamp of the latest patch on HEAD of the current branch'''
        return self.cfg['head'][1]

    @property
    def hash(self):
        '''gets the hash of the latest patch on HEAD of the current branch'''
        return self.cfg['head'][0]

    def print_date(self):
        '''prints the timestamp of the latest patch on HEAD of the current branch'''
        log.info('The timestamp is ' + self.date)

    def print_hash(self):
        '''prints the hash of the latest patch on HEAD of the current branch'''
        log.info('The hash is ' + self.hash)

    @contextmanager
    def patch(self, hash):
        '''executes a block of code on top a particular patch'''
        with self.src('--to-match', 'hash ' + hash):
            yield

    @contextmanager
    def tag(self, tag):
        '''executes a particular block of code on top of a particular tag'''
        with self.src('--tag', tag):
            yield


    def setup_sourceball(self, ver, delete_old=False):
        '''gets darcs to spit out a sourceball to be used in rpm making by other modules'''
        log.debug('someone set us up the bomb')
        if delete_old:
            with pwd(self.pkg_src_dir):
                rm(self.sourceball)
        name = self.upstream_name
        date = self.date
        full_name = '%s-%s.%sdarcs' % (name, ver, date)
        log.debug('full name is ' + full_name)
        sourceball = full_name + '.tar.gz'
        with pwd(self.source_dir):
            with log_file('darcs.log') as darcs_out:
                log.debug('we get signal')
                p = Popen(['darcs', 'dist', '-d', full_name],
                          stdout=darcs_out, stderr=darcs_out)
                log.info('generating tarball %s.tar.gz, please wait...'
                         % full_name)
                p.communicate()
        with pwd(self.pkg_src_dir):
            move(join(self.source_dir, sourceball), sourceball)
            self.cfg['sourceball'] = sourceball

__all__ = ['Darcs']
