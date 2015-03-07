"""Fake cursor interface.
"""
import contextlib


class FakeCursor(object):
    """Fake MySQL cursor object."""

    def callproc(self, procname, args=()):
        pass

    def close(self): pass

    def execute(self, operation, params=None, multi=False):
        pass

    def executemany(self, operation, seq_params):
        pass

    def fetchall(self):
        pass

    def fetchmany(self, size=None):
        pass

    def fetchone(self): pass

    def fetchwarnings(self):
        pass

    def getlastrowid(self):
        pass

    def next(self):
        pass

    def nextset(self):
        pass

    def reset(self): pass

    def setinputsizes(self, sizes):
        pass

    def setoutputsizes(self, sizes):
        pass

    def stored_results(self):
        pass

    def __iter__(self):
        pass

    description = property()
    column_names = property()
    lastrowid = property()
    rowcount = property()
    statement = property()
    with_rows = property()


class WithCursor(object):
    def __init__(self, cursor_mock):
        self._cursor_mock = cursor_mock

    def __enter__(self):
        return self._cursor_mock

    def __exit__(self, exc_type, exc_val, exc_tb):
        return
