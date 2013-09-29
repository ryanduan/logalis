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
#
import re
import os
import gzip
import stat
import email
import urllib2
import logging

from os.path import join, exists, dirname, isdir
from mailbox import UnixMailbox
from datetime import datetime, timedelta

from devshell.base.vars import DEVSHELL_DIR
from devshell.base.module import Module

log = logging.getLogger(__name__)

class Mail(Module):
    """ A module for searching/viewing mailing lists """

    url = 'https://www.redhat.com/archives/%s/%s'

    def search(self, mailinglist, text):
        """ <list> <text>. Search specific mailing list for given text """
        now = datetime.now()
        while True:
            fetch = True
            filename = now.strftime("%Y-%B") + '.txt.gz'
            try:
                f = urllib2.urlopen(self.url % (mailinglist, filename))
            except urllib2.HTTPError:
                break
            local = join(DEVSHELL_DIR, mailinglist, filename)

            # Don't fetch the mbox if we already have a good local copy
            if exists(local):
                info = os.stat(local)
                if info[stat.ST_SIZE] == int(f.headers.get('Content-Length')):
                    fetch = False
                    log.debug("Using local mbox: %s" % local)
            if fetch:
                if not exists(dirname(local)):
                    os.makedirs(dirname(local))
                mbox = file(local, 'w')
                log.debug("Downloading %s" % local)
                mbox.write(f.read())
                mbox.close()
                f.close()

            self.__search_mbox(local, text)

            # Go back in time
            now = now - timedelta(days=31)

    def __search_mbox(self, mboxfile, text):
        """
            Search a compressed mbox for any specified keywords
        """
        num = 0
        statinfo = os.stat(mboxfile)
        gzmbox = gzip.open(mboxfile)
        mbox = UnixMailbox(gzmbox, email.message_from_file)
        while True:
            msg = mbox.next()
            if not msg: break
            num += 1
            fields = [msg['From'], msg['Subject']] + self.__body(msg)
            for field in fields:
                if re.search(text, field, re.IGNORECASE):
                    id = "%s.%s" % (statinfo[stat.ST_INO], num)
                    print "[%s] %s %s" % (id, msg['From'], msg['Subject'])
                    break
        gzmbox.close()

    def __body(self, msg):
        """
            Recursively gather multipart message bodies
        """
        body = []
        if msg.is_multipart():
            for payload in msg.get_payload():
                for part in payload.walk():
                    body += self.__body(part)
        else:
            body = [msg.get_payload()]
        return body

    def show(self, id):
        """ Show a message with a given ID """
        inode, msgnum = map(int, id.split('.'))
        olddir = os.getcwd()
        os.chdir(DEVSHELL_DIR)
        mboxfile = None
        for dir in filter(isdir, os.listdir('.')):
            for file in os.listdir(dir):
                statinfo = os.stat(join(dir, file))
                if statinfo[stat.ST_INO] == inode:
                    mboxfile = join(dir, file)
                    break
            if mboxfile: break
        if mboxfile:
            gzmbox = gzip.open(mboxfile)
            mbox = UnixMailbox(gzmbox, email.message_from_file)
            num = 0
            while num != msgnum:
                msg = mbox.next()
                num += 1
            self.__print_msg(msg)
        else:
            log.error("Cannot find message %s" % id)
        os.chdir(olddir)

    def __print_msg(self, msg):
        log.info("From: %s" % msg['From'])
        log.info("To: %s" % msg['To'])
        log.info("Subject: %s" % msg['Subject'])
        log.info('\n'.join(self.__body(msg)))

__all__ = ['Mail']
