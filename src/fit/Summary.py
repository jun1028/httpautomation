"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

from fit.Parse import Parse, ParseException
from fit.Fixture import Fixture, Counts

class Summary(Fixture):

    countsKey = "counts"

    def doTable(self, table):
        self.summary[self.countsKey] = self._counts()
        table.parts.more = self.rows(self.summary.keys())

    def rows(self, keys):
        keys.sort()
        if len(keys) > 0:
            key = keys[0]
            result = self.tr(self.td(key,
                             self.td(str(self.summary[key]),
                             None)),
                             self.rows(keys[1:]))
            if key == self.countsKey:
                self.mark(result)
            return result
        else:
            return None

    def tr(self, parts, more):
        return Parse(tag="tr", body=None, parts=parts, more=more)

    def td(self, body, more):
        return Parse(tag="td", body=self.gray(body), parts=None, more=more)

    # isolate real counts object so that we don't count the mark in the summary.
    def mark(self, row):
        official = self.counts
        self.counts = Counts()
        cell = row.parts.more
        if official.wrong + official.exceptions > 0:
            self.wrong(cell)
        else:
            self.right(cell)
        self.counts = official
        