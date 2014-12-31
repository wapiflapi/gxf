#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import string

# This provides 446 kb and is easily recognizable.
dfltalphabet = bytes(string.ascii_lowercase, "utf8")
dfltlength = 4

class DeBruijn(object):

    def __init__(self, a=dfltalphabet, n=dfltlength):
        self.k = len(a)
        self.a = a
        self.n = n

    def __iter__(self):

        a = [0] * self.k * self.n

        def db(t, p):
            if t > self.n:
                if self.n % p == 0:
                    for c in a[1:p+1]:
                        yield self.a[c]
            else:
                a[t] = a[t - p]
                yield from db(t + 1, p)
                for j in range(a[t - p] + 1, self.k):
                    a[t] = j
                    yield from db(t + 1, t)

        yield from db(1, 1)

    def cycle(self):
        while True:
            yield from self

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.start, index.stop, index.step
        else:
            start, stop, step = index, index + 1, 1

        return bytearray(itertools.islice(self.cycle(), start, stop, step))

    def offsets(self, x):

        x = list(x)

        if any(c not in self.a for c in x):
            raise ValueError("subsequence elements not a subset of alphabet")

        start = []
        window = []

        # We also want to check the overlap.
        for i, c in enumerate(self[:self.k**self.n+len(x)]):
            if len(window) >= len(x):
                del window[0]
            window.append(c)
            if window == x:
                yield i - len(window) + 1
                if len(x) >= self.n:
                    # We won't find anything else.
                    break
