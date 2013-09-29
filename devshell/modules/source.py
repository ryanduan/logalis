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
import os
import commands

from os.path import isdir, join
from devshell.base.vars import FEDORA_DIR
from devshell.base.module import Module


# Hack-filled at the moment.

UPDATE, CLONE, COMMIT, LOG, DIFF = range(5)
scm_cmds = {
    'git' : ('update', 'clone', 'log', 'diff'),
    'hg'  : ('update', 'clone', 'log', 'diff'),
    'cvs' : ('update', 'checkout', 'log', 'diff'),
}
scms = {
    'cvs.fedoraproject.org' : 'cvs -d :ext:cvs.fedoraproject.org:/cvs/pkgs %(command)s %(module)s',
    'git.fedorahosted.org'  : 'git %(command)s ssh+git://git.fedorahosted.org/git/%(module)s',
    'hg.fedorahosted.org'   : 'hg %(command)s ssh://hg.fedorahosted.org//hg/%(module)s',
}


class CannotFindPackage(Exception):
    pass

#FIXME: use this?
class SCM(object):
    cmds = dict(update='update', clone='clone', log='log', diff='diff')

class Source(Module):

    def __init__(self, name, branch='devel'):
        self.name = name
        self.branch = branch
        self.scm = None
        self.__path = None
        self.__checkout()

    def __set_path(self, p):
        """ Set our path and make it our current working directory """
        if isdir(join(p, self.branch)):
            p = join(p, self.branch)
        print p
        self.__path = p
        os.chdir(p)

    def __get_path(self):
        return self.__path

    path = property(__get_path, __set_path)

    def __checkout(self):
        """ Find where this package lives """

        # Look in FEDORA_DIR/<scm>/<pkg>
        for scm in scms.keys():
            scmdir = join(FEDORA_DIR, scm, self.name)
            if isdir(scmdir):
                self.scm = scm
                self.path = scmdir
                return

        # Find this module in our scms
        for scm in scms.keys():
            scmdir = join(FEDORA_DIR, scm)
            if not isdir(scmdir):
                print "Creating %s" % scmdir
                os.mkdir(scmdir)
            os.chdir(scmdir)
            cmd = scms[scm] % {
                    'command' : scm_cmds[scm.split('.')[0]][CLONE],
                    'module'  : self.name
            }
            print "Running %s" % cmd
            status, output = commands.getstatusoutput(cmd)
            if status == 0:
                self.scm = scm
                self.path = join(scmdir, self.name)
                return

        raise CannotFindPackage

    def spec(self):
        """ View the RPM spec file for this project """
        editor = os.getenv('EDITOR', 'vi')
        os.system("%s %s.spec" % (editor, self.name))

    def sh(self):
        """ Drop into a shell """
        os.system("bash")

    def update(self):
        self.scm.update()
        cmd = scms[self.scm] % {
                'command' : scm_cmds[self.scm.split('.')[0]][UPDATE],
                'module'  : '' 
        }
        print "Executing `%s`" % cmd
        status, output = commands.getstatusoutput(cmd)
        print output

    def log(self, item=''):
        """ Show the history of this package """
        cmd = scms[self.scm] % {
                'command' : scm_cmds[self.scm.split('.')[0]][LOG],
                'module'  : item
        }
        print "Executing `%s | less`" % cmd
        os.system("%s | less" % cmd)

    def diff(self, item=''):
        cmd = scms[self.scm] % {
                'command' : scm_cmds[self.scm.split('.')[0]][DIFF],
                'module'  : item
        }
        print "Executing `%s | colordiff | less -R`" % cmd
        os.system("%s | colordiff | less -R" % cmd)

    def build(self):
        raise NotImplementedError

    def srpm(self):
        raise NotImplementedError

    def qa(self):
        raise NotImplementedError

    def audit(self):
        raise NotImplementedError

    def bugs(self):
        raise NotImplementedError

__all__ = ['Source']
