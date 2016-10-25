#!/usr/bin/env python
"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

# 2003-07-23. Moved exit statement per java changes 2002-10-04

import string, re, time, sys, os, stat
from fit.Parse import Parse
from fit.Fixture import Fixture

class FileRunner:
    input = None
    tables = None
    fixture = Fixture()
    output = None
    outfile = None

    def __init__(self,argv):
        if len(argv) != 3:
            sys.stderr.write(
                "usage: python FileRunner.py input-file output-file\n")
            sys.exit(-1)
        infile = open(argv[1],'r')
        modtime = time.ctime(os.fstat(infile.fileno())[stat.ST_MTIME])
        self.outfile = open(argv[2],'w')
        self.fixture.summary["input file"] = os.path.abspath(argv[1])
        self.fixture.summary["input update"] = modtime
        self.fixture.summary["output file"] = os.path.abspath(argv[2])
        self.input = infile.read()
        infile.close()
        self.output = self.outfile

    def __call__(self):
        try:
            self.tables = Parse(self.input)
            self.fixture.doTables(self.tables)
        except Exception, e:
            self.exception(e)
        self.output.write(str(self.tables))
        self.exit()
        sys.exit(self.fixture.counts.wrong + self.fixture.counts.exceptions)
       
    run = __call__

    def exception(self,e):
        tables = Parse(tag="body",
                       body="Unable to parse input. Input ignored.",
                       parts=None,
                       more=None)
        Fixture.exception(self.fixture, tables, e)

    def exit(self):
        self.outfile.close()
        sys.stderr.write(self.fixture.counts.toString()+'\n')
    
if __name__ == '__main__':
    FileRunner(sys.argv).run()
