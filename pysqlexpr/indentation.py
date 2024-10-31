"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

import abc
import textwrap

_MAX_LEN = 120
_PREFIX = "    "


def indent(text: str) -> str:
    "Adds a single level of indentation to the beginning of each line of text."

    return textwrap.indent(text, _PREFIX)


class Printable:
    __slots__ = ()

    @abc.abstractmethod
    def packed(self) -> str:
        "Produces a compact single-line representation of the object."
        ...

    @abc.abstractmethod
    def spacious(self) -> str:
        "Produces an expanded multi-line representation of the object."
        ...

    def display(self) -> tuple[bool, str]:
        """
        Chooses an optimal representation of the object.

        :returns: A tuple of whether the output is packed, and the formatted text.
        """

        text = self.packed()
        if len(text) < _MAX_LEN:
            return True, text
        else:
            return False, self.spacious()

    def __str__(self) -> str:
        _, text = self.display()
        return text
