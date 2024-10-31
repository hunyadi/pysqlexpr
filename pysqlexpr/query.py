"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

from typing import ClassVar

from .boolean import BoolExpr
from .indentation import Printable, indent
from .typing import override


class Column:
    __slots__ = ("expr", "name")

    expr: str
    name: str | None

    def __init__(self, expr: str, *, name: str | None = None) -> None:
        self.expr = expr
        self.name = name

    def __str__(self) -> str:
        if self.name:
            return f"{self.expr} AS {self.name}"
        else:
            return self.expr


class ColumnList(Printable):
    __slots__ = ("columns",)

    columns: list[Column]

    def __init__(self, *columns: Column) -> None:
        self.columns = list(columns)

    def append(self, column: Column) -> None:
        self.columns.append(column)

    def extend(self, columns: list[Column]) -> None:
        self.columns.extend(columns)

    @override
    def packed(self) -> str:
        "Produces a compact single-line representation of the column list."

        return ", ".join(str(c) for c in self.columns)

    @override
    def spacious(self) -> str:
        "Produces an expanded multi-line representation of the column list."

        return ",\n".join(str(c) for c in self.columns)


class SourceExpr(Printable):
    __slots__ = ()


class FromExpr(SourceExpr):
    "An expression in the FROM clause."

    __slots__ = ("expr", "name")

    expr: str | SourceExpr
    name: str | None

    def __init__(self, expr: str | SourceExpr, *, name: str | None = None) -> None:
        self.expr = expr
        self.name = name

    @override
    def packed(self) -> str:
        "Produces a compact single-line representation of the source expression."

        if isinstance(self.expr, Query):
            expr = "(" + self.expr.packed() + ")"
        elif isinstance(self.expr, SourceExpr):
            expr = self.expr.packed()
        else:
            expr = self.expr
        if self.name is not None:
            return f"{expr} AS {self.name}"
        else:
            return expr

    @override
    def spacious(self) -> str:
        "Produces an expanded multi-line representation of the source expression."

        if isinstance(self.expr, Query):
            expr = "(" + self.expr.spacious() + ")"
        elif isinstance(self.expr, SourceExpr):
            expr = self.expr.spacious()
        else:
            expr = self.expr
        if self.name is not None:
            return f"{expr} AS {self.name}"
        else:
            return str(expr)


class JoinExpr(SourceExpr):
    "A JOIN expression in the FROM clause."

    __slots__ = ("left", "right", "condition")

    operator: ClassVar[str] = "[op]"

    left: SourceExpr
    right: SourceExpr
    condition: BoolExpr | None

    def __init__(self, left: SourceExpr, right: SourceExpr, condition: BoolExpr):
        self.left = left
        self.right = right
        self.condition = condition

    @override
    def packed(self) -> str:
        "Produces a compact single-line representation of the join expression."

        return f"{self.left} {self.operator} {self.right} ON {self.condition}"

    @override
    def spacious(self) -> str:
        "Produces an expanded multi-line representation of the join expression."

        return f"{self.left}\n    {self.operator} {self.right}\n        ON {self.condition}"


class Join(JoinExpr):
    "An inner join."

    operator: ClassVar[str] = "INNER JOIN"


class LeftJoin(JoinExpr):
    "A left join."

    operator: ClassVar[str] = "LEFT JOIN"


class RightJoin(JoinExpr):
    "A right join."

    operator: ClassVar[str] = "RIGHT JOIN"


class LateralJoin(JoinExpr):
    "A lateral join."

    def __init__(self, left: FromExpr, right: FromExpr):
        self.left = left
        self.right = right
        self.condition = None

    @override
    def packed(self) -> str:
        "Produces a compact single-line representation of the join expression."

        return f"{self.left} INNER JOIN LATERAL {self.right}"

    @override
    def spacious(self) -> str:
        "Produces an expanded multi-line representation of the join expression."

        return f"{self.left}\n    INNER JOIN LATERAL {self.right}"


class Query(SourceExpr):
    "A query or sub-query that yields a table result."

    source: SourceExpr
    columns: ColumnList
    where: BoolExpr | None = None
    group_by: list[str] | None = None

    def __init__(
        self,
        source: SourceExpr,
        columns: list[Column],
        *,
        where: BoolExpr | None = None,
        group_by: list[str] | None = None,
    ) -> None:
        self.source = source
        self.columns = ColumnList(*columns)
        self.where = where
        self.group_by = group_by

    @override
    def packed(self) -> str:
        source = self.source.packed()
        if isinstance(self.source, Query):
            source = f"({source})"
        if self.where is not None:
            where = f" WHERE {self.where.packed()}"
        else:
            where = ""
        if self.group_by is not None:
            group_by = f" GROUP BY {', '.join(self.group_by)}"
        else:
            group_by = ""
        return f"SELECT {self.columns.packed()} FROM {source}{where}{group_by}"

    @override
    def spacious(self) -> str:
        source = self.source.spacious()
        if isinstance(self.source, Query):
            source = f"(\n{source}\n)"
        if self.where is not None:
            where = f"\nWHERE\n{indent(str(self.where))}"
        else:
            where = ""
        if self.group_by is not None:
            group_by = f"\nGROUP BY {', '.join(self.group_by)}"
        else:
            group_by = ""
        return f"SELECT\n{indent(self.columns.spacious())}\nFROM\n{indent(source)}{where}{group_by}"
