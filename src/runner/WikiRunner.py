#!/usr/bin/env python
"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""
import sys
from fit.FileRunner import FileRunner
from fit.Parse import Parse

class WikiRunner(FileRunner):
    def __call__(self):
        try:
            tags = ("wiki", "table", "tr", "td")
            self.tables = Parse(self.input, tags)#look for wiki tag enclosing tables
            self.fixture.doTables(self.tables.parts)#only do tables within that tag
        except Exception, e:
            self.exception(e)
        self.output.write(str(self.tables))
        self.exit()

    run = __call__

if __name__ == '__main__':
    WikiRunner(sys.argv).run()
