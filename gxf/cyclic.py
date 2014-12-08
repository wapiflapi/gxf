#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools

class debruijn(object):

    def __init__(self, a, n):
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

    def offsets(self, x):

        x = list(x)
        window = []

        for i, c in enumerate(self):
            if len(window) >= len(x):
                del window[0]
            window.append(c)
            if window == x:
                yield i - len(window) + 1

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.start, index.stop, index.step
        else:
            start, stop, step = index, index + 1, 1
        return list(itertools.islice(self.cycle(), start, stop, step))

