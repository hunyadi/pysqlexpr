"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

import abc
import textwrap
from typing import ClassVar, Iterable, NoReturn, final

MAX_LEN = 120
PREFIX = "    "


def indent(text: str) -> str:
    "Adds a single level of indentation to the beginning of each line of text."

    return textwrap.indent(text, PREFIX)


class BoolExpr(abc.ABC):
    "A Boolean expression that yields TRUE, FALSE or NULL."

    __slots__ = ()

    @abc.abstractmethod
    def __and__(self, op: "BoolExpr") -> "BoolExpr": ...

    @abc.abstractmethod
    def __or__(self, op: "BoolExpr") -> "BoolExpr": ...

    def collapsed(self) -> str:
        return str(self)

    def expanded(self) -> str:
        return str(self)

    def __bool__(self) -> NoReturn:
        raise TypeError(
            "cannot cast to `bool`, use `&` (instead of `and`) or `|` (instead of `or`) to build composite Boolean expressions"
        )


@final
class ReturnsBool(BoolExpr):
    "An expression that yields a Boolean result such as IS [NOT] NULL, equality test, or a comparison."

    __slots__ = ("expr",)

    expr: str

    def __init__(self, expr: str) -> None:
        self.expr = expr

    def __and__(self, op: BoolExpr) -> "ConjExpr":
        ops: list[BoolExpr] = []
        ops.append(self)
        if isinstance(op, ReturnsBool):
            ops.append(op)
            return ConjExpr(ops)
        elif isinstance(op, ConjExpr):
            ops.extend(op.operands)
            return ConjExpr(ops)
        elif isinstance(op, DisjExpr):
            ops.append(op.unwrap())
            return ConjExpr(ops)
        else:
            raise NotImplementedError("expected: conjunction or disjunction")

    def __or__(self, op: BoolExpr) -> "DisjExpr":
        ops: list[BoolExpr] = []
        ops.append(self)
        if isinstance(op, ReturnsBool):
            ops.append(op)
            return DisjExpr(ops)
        elif isinstance(op, DisjExpr):
            ops.extend(op.operands)
            return DisjExpr(ops)
        elif isinstance(op, ConjExpr):
            ops.append(op.unwrap())
            return DisjExpr(ops)
        else:
            raise NotImplementedError("expected: conjunction or disjunction")

    def __str__(self) -> str:
        return self.expr


class LogicalExpr(BoolExpr):
    "An expression that yields the Boolean result of a conjunction (logical AND) or disjunction (logical OR)."

    __slots__ = ("operands",)

    name: ClassVar[str] = "logical expression"

    operands: list[BoolExpr]

    def __init__(self, ops: list[BoolExpr] | None = None) -> None:
        self.operands = ops or []

    def __len__(self) -> int:
        return len(self.operands)

    def append(self, op: BoolExpr) -> None:
        self.operands.append(op)

    def extend(self, ops: Iterable[BoolExpr]) -> None:
        self.operands.extend(ops)

    def unwrap(self) -> BoolExpr:
        if len(self.operands) == 1:
            return self.operands[0]
        else:
            return self

    def _logical_to_str(self, sep: str) -> str:
        if len(self.operands) == 0:
            raise ValueError(f"empty {self.name}")

        expr = f" {sep} ".join(op.collapsed() for op in self.operands)
        if len(expr) < MAX_LEN:
            return f"({expr})"

        expr = f"\n{sep}\n".join(indent(op.expanded()) for op in self.operands)
        return f"(\n{expr}\n)"


@final
class ConjExpr(LogicalExpr):
    "An expression that yields the Boolean result of a conjunction (logical AND)."

    name: ClassVar[str] = "conjunction"

    def __and__(self, op: BoolExpr) -> "ConjExpr":
        ops: list[BoolExpr] = []
        ops.extend(self.operands)
        if isinstance(op, ReturnsBool):
            ops.append(op)
            return ConjExpr(ops)
        elif isinstance(op, ConjExpr):
            ops.extend(op.operands)
            return ConjExpr(ops)
        elif isinstance(op, DisjExpr):
            ops.append(op.unwrap())
            return ConjExpr(ops)
        else:
            raise NotImplementedError("expected: conjunction or disjunction")

    def __or__(self, op: BoolExpr) -> "DisjExpr":
        return DisjExpr([self, op])

    def __str__(self) -> str:
        return self._logical_to_str("AND")


@final
class DisjExpr(LogicalExpr):
    "An expression that yields the Boolean result of a disjunction (logical OR)."

    name: ClassVar[str] = "disjunction"

    def __and__(self, op: BoolExpr) -> "ConjExpr":
        return ConjExpr([self, op])

    def __or__(self, op: BoolExpr) -> "DisjExpr":
        ops: list[BoolExpr] = []
        ops.extend(self.operands)
        if isinstance(op, ReturnsBool):
            ops.append(op)
            return DisjExpr(ops)
        elif isinstance(op, DisjExpr):
            ops.extend(op.operands)
            return DisjExpr(ops)
        elif isinstance(op, ConjExpr):
            ops.append(op.unwrap())
            return DisjExpr(ops)
        else:
            raise NotImplementedError("expected: conjunction or disjunction")

    def __str__(self) -> str:
        return self._logical_to_str("OR")
