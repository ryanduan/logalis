#!/usr/bin/python
#-*- coding: utf-8 -*-
# Author: Ryan

from os import stat
from os.path import exists, getsize
import glob
from datetime import datetime

class Readlog(object):
    """
    Creates an iterable object that returns only unread lines.
    """
    def __init__(self, filename, offset_file=None, paranoid=False):
        self.filename = filename
        self.paranoid = paranoid
        self._offset_file = offset_file or "%s.offset" % self.filename
        self._offset_file_inode = 0
        self._offset = 0
        self._fh = None
        self._rotated_logfile = None

        # if offset file exists and non-empty, open and parse it
        if exists(self._offset_file) and getsize(self._offset_file):
            offset_fh = open(self._offset_file, "r")
            (self._offset_file_inode, self._offset) = \
                [int(line.strip()) for line in offset_fh]
            offset_fh.close()
            if self._offset_file_inode != stat(self.filename).st_ino:
                # The inode has changed, so the file might have been rotated.
                # Look for the rotated file and process that if we find it.
                self._rotated_logfile = self._determine_rotated_logfile()

    def __del__(self):
        if self._filehandle():
            self._filehandle().close()

    def __iter__(self):
        return self

    def next(self):
        """
        Return the next line in the file, updating the offset.
        """
        try:
            line = next(self._filehandle())
        except StopIteration:
            # we've reached the end of the file; if we're processing the
            # rotated log file, we can continue with the actual file; otherwise
            # update the offset file
            if self._rotated_logfile:
                self._rotated_logfile = None
                self._fh.close()
                self._offset = 0
                # open up current logfile and continue
                try:
                    line = next(self._filehandle())
                except StopIteration:  # oops, empty file
                    self._update_offset_file()
                    raise
            else:
                self._update_offset_file()
                raise

        if self.paranoid:
            self._update_offset_file()

        return line

    def _filehandle(self):
        """
        Return a filehandle to the file being tailed, with the position set
        to the current offset.
        """
        if not self._fh or self._fh.closed:
            filename = self._rotated_logfile or self.filename
            self._fh = open(filename, "r")
            self._fh.seek(self._offset)

        return self._fh

    def _update_offset_file(self):
        """
        Update the offset file with the current inode and offset.
        """
        offset = self._filehandle().tell()
        inode = stat(self.filename).st_ino
        fh = open(self._offset_file, "w")
        fh.write("%s\n%s\n" % (inode, offset))
        fh.close()

    def _determine_rotated_logfile(self):
        """
        We suspect the logfile has been rotated, so try to guess what the
        rotated filename is, and return it.
        """
        rotated_filename = self._check_rotated_filename_candidates()
        if (rotated_filename and exists(rotated_filename) and
            stat(rotated_filename).st_ino == self._offset_file_inode):
            return rotated_filename
        else:
            return None

    def _check_rotated_filename_candidates(self):
        """
        Check for various rotated logfile filename patterns and return the first
        match we find.
        """
        # savelog(8)
        candidate = "%s.0" % self.filename
        if (exists(candidate) and exists("%s.1.gz" % self.filename) and
            (stat(candidate).st_mtime > stat("%s.1.gz" % self.filename).st_mtime)):
            return candidate

        # logrotate(8)
        candidate = "%s.1" % self.filename
        if exists(candidate):
            return candidate

        # dateext rotation scheme
        candidates = glob.glob("%s-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]" % self.filename)
        if candidates:
            candidates.sort()
            return candidates[-1]  # return most recent

        # for TimedRotatingFileHandler
        candidates = glob.glob("%s.[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]" % self.filename)
        if candidates:
            candidates.sort()
            return candidates[-1]  # return most recent

        # no match
        return None

def analysislog(logs):
    timenow = datetime.now()
    error_num = 0
    warning_num = 0
    info_num = 0
#    d_n = 0
    errors = []
#    debugs = []
    for log in logs:
        if 'INFO' in log:
            info_num += 1
        elif 'WARNING' in log:
            warning_num += 1
#        elif 'DEBUG' in log:
#            d_n += 1
#            debugs.append(log)
        else:
            if 'ERROR' in log:
                error_num += 1
                errors.append(log)
            errors.append(log)
#    return (timenow, info_num, warning_num, error_num, d_n, errors, debugs)
    return (timenow, info_num, warning_num, error_num, errors)

if __name__ == "__main__":
    import datetime
    print datetime.datetime.now()
    logs = Readlog("/home/ryan/testoflog/test01.log")
    print "readlog"
    loginfo = analysislog(logs)
    print loginfo

