"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

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


class QueryExpr(Printable):
    @override
    def packed(self) -> str:
        "Produces a compact single-line representation of the query expression."

        return str(self)

    @override
    def spacious(self) -> str:
        "Produces an expanded multi-line representation of the query expression."

        return str(self)


class FromExpr(QueryExpr):
    expr: str

    def __init__(self, expr: str) -> None:
        self.expr = expr

    @override
    def packed(self) -> str:
        return self.expr

    @override
    def spacious(self) -> str:
        return self.expr


class Query(QueryExpr):
    source: QueryExpr
    columns: ColumnList

    def __init__(self, source: QueryExpr, columns: list[Column]) -> None:
        self.source = source
        self.columns = ColumnList(*columns)

    @override
    def packed(self) -> str:
        source = self.source.packed()
        if isinstance(self.source, Query):
            source = f"({source})"
        return f"SELECT {self.columns.packed()} FROM {source}"

    @override
    def spacious(self) -> str:
        source = self.source.spacious()
        if isinstance(self.source, Query):
            source = f"(\n{source}\n)"
        return f"SELECT\n{indent(self.columns.spacious())}\nFROM\n{indent(source)}"
