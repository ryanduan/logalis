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

import re
import rpm
import string
import time

from subprocess import Popen, PIPE
from contextlib import contextmanager
from functools import partial

from devshell.base.base import log
from devshell.base.awk import *

class RPMSpec(object):
    def __init__(self, spec_file, defines=''):
        self.spec_file = spec_file
        self.defines = ''
        self.contents = [x for x in file(spec_file)]

    def query(self, tags):
        return query_specfile(self.spec_file, tags, self.defines)

    def query_one(self, *tags):
        return query_specfile_one(self.spec_file, tags, self.defines)

    def query_one_field(self, field):
        return self.query_one(field)[field]

    def set_contents(self, contents):
        '''we force it to save each time, so commands that query via the shell
        have the most up to date version'''
        self.contents = list(contents)
        self.save()

    def save(self):
        with file(self.spec_file, 'w') as spec:
            spec.writelines(self.contents)

    def version(self):
        return self.query_one_field('version')

    def version_line(self):
        ver_line = [x for x in self.contents if x.startswith('Version:')][0]
        ver_re = re.search(r'Version: (.*)', ver_line)
        return ver_re.groups()[0]

    def set_version(self, version):
        VersionProgram = ReplaceTagProgram('Version', version)
        version_program = VersionProgram()
        self.set_contents(version_program(self.contents))

    def release(self):
        return self.query_one_field('release')

    def rel_line(self):
        rel_line = [x for x in self.contents if x.startswith('Release:')][0]
        rel_re = re.search(r'Release: (.*)', rel_line)
        return rel_re.groups()[0]

    def ver_rel(self):
        ver_rel = self.query_one('version', 'release')
        return (ver_rel['version'], ver_rel['release'])

    def name(self):
        return self.query_one_field('name')

    def evr(self):
        '''code taken from rpmdev-bumpspec'''
        evr = self.query_one('epoch', 'version', 'release')
        if evr['epoch'] != '(none)':
            evr_out = evr['epoch'] + ':'
        else:
            evr_out = ''
        return evr_out + evr['version'] + '-' + evr['release']

    def increment_release(self, rightmost=False):
        Program = BumpReleaseProgram(rightmost)
        program = Program()
        self.set_contents(program(self.contents))

    def set_alphatag(self, alphatag):
        Program = ReplaceMacroProgram('alphatag', alphatag)
        program = Program()
        self.set_contents(program(self.contents))

    def add_changelog(self, entry, email):
        evr = self.evr()
        Program = ChangeLogProgram(evr, entry, email)
        program = Program()
        self.set_contents(program(self.contents))

    def bump_release(self, entry, email, rightmost=False):
        self.increment_release(rightmost)
        self.add_changelog(entry, email)

    def sources(self):
        ts = rpm.TransactionSet()
        spec = ts.parseSpec(self.spec_file)
        return spec.sources()


def format_querytag(tag):
    return "%%%%{%s}" % tag.upper()

def specfile_query_cmd(querytags):
    querytags = " ".join(querytags)
    return 'rpm %%s -q --qf "%s\n" --specfile %%s' % querytags

def query_specfile_one(spec_file, tags, defines=''):
    return query_specfile(spec_file, tags, defines)[0]

def query_specfile(spec_file, tags, defines=''):
    querytags = map(format_querytag, tags)
    querycmd = specfile_query_cmd(querytags)
    results = query_rpm(querycmd, spec_file, defines)
    return map(dict, map(partial(zip, tags), map(partial(string.split, sep=' '), results)))

def query_rpm(cmd, target, defines=''):
    rpm_p = Popen(cmd % (defines, target)
                  , stdout=PIPE, shell=True)
    ret = rpm_p.communicate()[0].strip().split('\n')
    return ret


class Tag(RegexPattern):
    def __init__(self, tag):
        RegexPattern.__init__(self, r'^(?P<key>%s):\s*(?P<value>.*)$' % tag, re.I)


class ReplaceValueHandler(BaseHandler):
    def __init__(self, value):
        self.value = value

    def __call__(self, awk, match, line):
        yield line.replace(match.group('value'), self.value)


class ReplaceAction(ActionOrPrint):
    def __init__(self, pattern, value):
        handler = ReplaceValueHandler(value)
        ActionOrPrint.__init__(self, pattern, handler)


def ReplaceProgram(Pattern, key, value):
    program = AwkProgram()
    program.add_action(ReplaceAction(Pattern(key), value))
    return program


def ReplaceTagProgram(tag, value):
    return ReplaceProgram(Tag, tag, value)


class Macro(RegexPattern):
    def __init__(self, macro):
        RegexPattern.__init__(self, r'^%%global (?P<key>%s) (?P<value>.*?)\n' % macro)


def ReplaceMacroProgram(macro, value):
    return ReplaceProgram(Macro, macro, value)


rpat1 = RegexPattern(r"^Release\s*:\s*(?P<release>\d+.*)", re.I)
rpat2 = RegexPattern(r"^%define\s+rel\s+(?P<release>\d+.*)")
rpat3 = RegexPattern(r"^%define\s+release\s+(?P<release>\d+.*)", re.I)
rpat4 = RegexPattern(r"^Release\s*:\s+%release_func\s+(\d+.*)")
rpat5 = RegexPattern(r"^%define\s+baserelease\s+(\d+.*)")

release_not_pattern = NotPattern(RegexPattern(r"\$Revision:"))
ReleasePattern = OneOfPattern(rpat1, rpat2, rpat3, rpat4, rpat5)
BumpReleasePattern = AndPattern(release_not_pattern, ReleasePattern)

class BumpSpecError(Exception):
    def __init__(self, reason=''):
        self.reason = reason
    pass

class BumpReleaseHandler(object):
    def __init__(self, rightmost=False):
        self.rightmost = rightmost

    def __call__(self, awk, match, line):
        yield line.replace(*self.increase(match))

    def increase(self, match):
        old = match.group('release')  # only the release value
        try:
            if self.rightmost:
                new = self.increaseFallback(old)
            elif old.find('jpp')>0:
                new = self.increaseJPP(old)
            else:
                new = self.increaseMain(old)
        except BumpSpecError, e:
            if e.reason:
                print e.reason
            new = self.increaseFallback(old)
#         if self.verbose:
#             self.debugdiff(old, new)
        # group 0 is the full line that defines the release
        return old, new

    def increaseMain(self, release):
        if release.startswith('0.'):
            relre = re.compile(r'^0\.(?P<rel>\d+)(?P<post>.*)')
            pre = True
        else:
            relre = re.compile(r'^(?P<rel>\d+)(?P<post>.*)')
            pre = False
        relmatch = relre.search(release)
        if not relmatch:  # pattern match failed
            raise BumpSpecError
        value = int(relmatch.group('rel'))
        post = relmatch.group('post')

        if not pre:
            if post.find('rc')>=0:
                raise BumpSpecError('WARNING: Bad pre-release versioning scheme')
            new = `value+1`+post
        else:
            new = '0.'+`value+1`+post
        return new

    def increaseJPP(self, release):
        """Fedora jpackage release versioning scheme"""

        relre = re.compile(r'(?P<prefix>.*)(?P<rel>\d+)(?P<jpp>jpp\.)(?P<post>.*)')
        relmatch = relre.search(release)
        if not relmatch:  # pattern match failed
            raise BumpSpecError

        prefix = relmatch.group('prefix')
        value = int(relmatch.group('rel'))
        jpp = relmatch.group('jpp')
        post = relmatch.group('post')

        newpost = self.increaseMain(post)
        new = prefix+str(value)+jpp+newpost
        return new

    def increaseFallback(self, release):
        """bump at the very-right or add .1 as a last resort"""
        relre = re.compile(r'(?P<prefix>.+\.)(?P<post>\d+$)')
        relmatch = relre.search(release)
        if relmatch:
            prefix = relmatch.group('prefix')
            post = relmatch.group('post')
            new = prefix+self.increaseMain(post)
        else:
            new = release.rstrip()+'.1'
        return new

def BumpReleaseAction(rightmost=False):
    return ActionOrPrint(BumpReleasePattern, BumpReleaseHandler(rightmost))

def BumpReleaseProgram(rightmost=False):
    program = AwkProgram()
    program.add_action(BumpReleaseAction(rightmost))
    return program

ChangeLogPattern = RegexPattern(r"%changelog")

class ChangeLogHandler(BaseHandler):
    def __init__(self, evr, entry, email):
        self.evr = evr
        self.entry = entry
        self.email = email

    def __call__(self, awk, match, line):
        if len(self.evr):
            evrstring = ' - %s' % self.evr
        else:
            evrstring = ''
        yield line
        date = time.strftime("%a %b %d %Y",   time.localtime(time.time()))
        yield "* " + date + " " + self.email + evrstring + "\n"
        yield "- " + self.entry + "\n"
        yield "\n"


def ChangeLogAction(evr, entry, email):
    return ActionOrPrint(ChangeLogPattern, ChangeLogHandler(evr, entry, email))


def ChangeLogProgram(evr, entry, email):
    program = AwkProgram()
    program.add_action(ChangeLogAction(evr, entry, email))
    return program


@contextmanager
def rpm_macros(**keys):
    for key, value in keys.iteritems():
        log.debug('setting...')
        log.debug(key + ' ' + value)
        rpm.addMacro(key, value)
    yield
    for key, value in keys.iteritems():
        rpm.delMacro(key)

__all__ = ['rpm_macros', 'RPMSpec']
