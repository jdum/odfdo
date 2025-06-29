# Copyright 2018-2025 Jérôme Dumonteil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python

import random
import time

from odfdo.table import Row, Table

DEBUG = False
MAXPRINT = 10


class initial_compute:
    def __init__(self, lines=100, cols=100):
        self.lines = lines
        self.cols = cols
        self.rnd_line = self.do_rnd_order(lines)
        self.rnd_col = self.do_rnd_order(cols)
        self.py_table0 = self.populate_order()
        self.py_table = self.populate()
        print("-" * 50)

    def do_rnd_order(self, length):
        random.seed(42)
        order = list(range(length))
        random.shuffle(order)
        return order

    def populate(self):
        random.seed(42)
        base = list(range(self.cols))
        tab = []
        for _dummy in range(self.lines):
            random.shuffle(base)
            tab.append(base[:])
        return tab

    def populate_order(self):
        base = list(range(self.cols))
        tab = []
        for r in range(self.lines):
            tab.append([r * self.cols + base[c] for c in base])
        return tab


class chrono:
    def __init__(self):
        self.t0 = time.time()
        self.t1 = 0.0

    def delta(self):
        self.t1 = time.time()
        print("%.1f sec" % (self.t1 - self.t0))

    def value(self):
        return self.t1 - self.t0

    def ratio(self, base):
        return self.value() / base


def run_append_rows(D):
    print("Test append_row", D.lines, "rows", D.cols, "cols")
    table = Table("Table")
    C = chrono()
    for line in range(D.lines):
        row = Row()
        row.set_values(D.py_table0[line])
        table.append_row(row)
    C.delta()
    print("Size of table :", table.size)
    if DEBUG and table.width <= MAXPRINT and table.height <= MAXPRINT:
        print(table.to_csv(dialect="unix"))
    print("-" * 50)


def run_set_rows(D):
    print("Test random set_row", D.lines, "rows", D.cols, "cols")
    table = Table("Table")
    C = chrono()
    for line in range(D.lines):
        row = Row()
        row.set_values(D.py_table0[line])
        if DEBUG and table.width <= MAXPRINT and table.height <= MAXPRINT:
            print(D.rnd_line[line], "=>", D.py_table0[line])

        table.set_row(D.rnd_line[line], row)
        if DEBUG and table.width <= MAXPRINT and table.height <= MAXPRINT:
            print(table.to_csv(dialect="unix"))

    C.delta()
    print("Size of table :", table.size)
    if DEBUG and table.width <= MAXPRINT and table.height <= MAXPRINT:
        print(table.to_csv(dialect="unix"))
    print("-" * 50)
    return table


def run_swap(D, table_ini):
    print("Test swap rows/cols from table", D.lines, "rows", D.cols, "cols")
    table = Table("swapped", D.lines, D.cols)
    C = chrono()
    for col in range(D.cols):
        values = table_ini.get_column_values(col)
        table.set_row_values(col, values)
    C.delta()
    print("Size of swapped table :", table.size)
    if DEBUG and table.width <= MAXPRINT and table.height <= MAXPRINT:
        print(table.to_csv(dialect="unix"))
    print("-" * 50)


def run_swap_transpose(D, table_ini):
    print("Test swap rows/cols with transpose ", D.lines, "rows", D.cols, "cols")
    if not hasattr(table_ini, "transpose"):
        print("method not available")
        print("-" * 50)
        return
    table = table_ini.clone
    C = chrono()
    table.transpose()
    C.delta()
    print("Size of swapped table :", table.size)
    if DEBUG and table.width <= MAXPRINT and table.height <= MAXPRINT:
        print(table.to_csv(dialect="unix"))
    print("-" * 50)


def run_random_set_value(D):
    print("Test random set_value", D.lines, "rows", D.cols, "cols")
    table = Table("Table")
    cpt = 0
    C = chrono()
    for line in D.rnd_line:
        for col in range(D.cols):
            table.set_value((col, line), cpt)
            cpt += 1
    C.delta()
    print(cpt, "values entered")
    print("Size of table :", table.size)
    if DEBUG and table.width <= MAXPRINT and table.height <= MAXPRINT:
        print(table.to_csv(dialect="unix"))
    print("-" * 50)
    return table


def run_random_get_value(D, table_ini):
    print("Test read random get_value", D.lines, "rows", D.cols, "cols")
    vals = []
    cpt = 0
    C = chrono()
    for line in D.rnd_line:
        for col in D.rnd_col:
            vals.append(table_ini.get_value((col, line)))
            cpt += 1
    C.delta()
    print(cpt, "values read")
    print("-" * 50)


def run_repeated(D):
    print("test random repeated lines", D.lines, "rows", D.cols, "cols")
    table = Table("Table")
    C = chrono()
    for line in range(D.lines):
        row = Row()
        row.set_values([(line * 10 + x) for x in range(D.cols)])
        row.repeated = line
        # if DEBUG:
        #    print D.rnd_line[line], "=>", row.get_values(), row.repeated
        table.set_row(D.rnd_line[line], row)
    C.delta()
    print("Size of table :", table.size)
    if DEBUG and table.width <= MAXPRINT and table.height <= MAXPRINT:
        print(table.to_csv(dialect="unix"))
    print("-" * 50)
    return table


def run_perf_test(rows: int, cols: int) -> None:
    print(f"rows: {rows} cols:{cols}")
    duration = chrono()
    D = initial_compute(lines=rows, cols=cols)
    run_append_rows(D)
    t = run_set_rows(D)
    run_swap(D, t)
    run_swap_transpose(D, t)
    t = run_random_set_value(D)
    run_random_get_value(D, t)
    run_repeated(D)
    duration.delta()
