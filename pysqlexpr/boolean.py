"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

import abc
from typing import ClassVar, Iterable, NoReturn, final

from .indentation import Printable, indent
from .typing import override


class BoolExpr(abc.ABC, Printable):
    "A Boolean expression that yields TRUE, FALSE or NULL."

    __slots__ = ()

    @abc.abstractmethod
    def __and__(self, op: "BoolExpr") -> "BoolExpr": ...

    @abc.abstractmethod
    def __or__(self, op: "BoolExpr") -> "BoolExpr": ...

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

    def __eq__(self, op: object) -> bool:
        return isinstance(op, ReturnsBool) and self.expr == op.expr

    def __hash__(self) -> int:
        return hash(self.expr)

    @override
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

    @override
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

    @override
    def packed(self) -> str:
        return self.expr

    @override
    def spacious(self) -> str:
        return self.expr


class LogicalExpr(BoolExpr):
    "An expression that yields the Boolean result of a conjunction (logical AND) or disjunction (logical OR)."

    __slots__ = ("operands",)

    name: ClassVar[str] = "logical expression"
    operator: ClassVar[str] = "[op]"

    operands: tuple[BoolExpr, ...]

    def __init__(self, ops: Iterable[BoolExpr]) -> None:
        self.operands = tuple(ops)

    def __eq__(self, op: object) -> bool:
        return (
            isinstance(op, LogicalExpr)
            and self.operator == op.operator
            and self.operands == op.operands
        )

    def __hash__(self) -> int:
        return hash((self.operator, self.operands))

    def __len__(self) -> int:
        return len(self.operands)

    def unwrap(self) -> BoolExpr:
        if len(self.operands) == 1:
            return self.operands[0]
        else:
            return self

    def _check(self) -> None:
        "Verifies if the logical expression is valid."

        if len(self.operands) == 0:
            raise ValueError(f"empty {self.name}")

    def packed(self) -> str:
        "Produces a compact single-line representation of the logical expression."

        self._check()
        return (
            "(" + f" {self.operator} ".join(op.packed() for op in self.operands) + ")"
        )

    def spacious(self) -> str:
        "Produces an expanded multi-line representation of the logical expression."

        self._check()
        return (
            "(\n"
            + f"\n{self.operator}\n".join(indent(op.spacious()) for op in self.operands)
            + "\n)"
        )


@final
class ConjExpr(LogicalExpr):
    "An expression that yields the Boolean result of a conjunction (logical AND)."

    name: ClassVar[str] = "conjunction"
    operator: ClassVar[str] = "AND"

    @override
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

    @override
    def __or__(self, op: BoolExpr) -> "DisjExpr":
        return DisjExpr([self, op])


@final
class DisjExpr(LogicalExpr):
    "An expression that yields the Boolean result of a disjunction (logical OR)."

    name: ClassVar[str] = "disjunction"
    operator: ClassVar[str] = "OR"

    @override
    def __and__(self, op: BoolExpr) -> "ConjExpr":
        return ConjExpr([self, op])

    @override
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
