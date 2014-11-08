#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argcomplete import *


class CompletionFinder(CompletionFinder):
    '''
    This fixes three things in argcomplete:
     - When monkey patching the parser don't loose its inheritance.
     - Check if already patched or not in order to avoid (bad) recursion.
     - only ignore non safe actions if autocompleting.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autcompleting = False

    def _get_completions(self, *args, **kwargs):
        self.autocompleting = True
        completions = super()._get_completions(*args, **kwargs)
        self.autocompleting = False
        return completions

    def _patch_argument_parser(self):
        active_parsers = []

        def patch(parser):

            active_parsers.append(parser)

            if isinstance(parser, IntrospectiveArgumentParser):
                return

            parser.__class__ = type(
                "MonkeyPatchedIntrospectiveArgumentParser",
                (IntrospectiveArgumentParser, parser.__class__),
                {})

            for action in parser._actions:

                if hasattr(action, "_orig_class"):
                    continue

                class IntrospectAction(action.__class__):
                    def __call__(self, *args, **kwargs):
                        if not self.autocompleting:
                            self._orig_callable(*args, **kwargs)
                        elif self._orig_class == argparse._SubParsersAction:
                            patch(self._name_parser_map[values[0]])
                            self._orig_callable(*args, **kwargs)
                        elif self._orig_class in safe_actions:
                            self._orig_callable(*args, **kwargs)

                action._orig_class = action.__class__
                action._orig_callable = action.__call__
                action.__class__ = IntrospectAction

        patch(self._parser)
        return active_parsers, argparse.Namespace()
