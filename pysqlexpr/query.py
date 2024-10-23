"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""


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


class ColumnList:
    __slots__ = ("columns",)

    columns: list[Column]

    def __init__(self, *columns: Column) -> None:
        self.columns = list(columns)

    def append(self, column: Column) -> None:
        self.columns.append(column)

    def extend(self, columns: list[Column]) -> None:
        self.columns.extend(columns)

    def __str__(self) -> str:
        return ",\n".join(str(c) for c in self.columns)


class QueryExpr:
    pass


class FromExpr(QueryExpr):
    expr: str

    def __init__(self, expr: str) -> None:
        self.expr = expr

    def __str__(self) -> str:
        return f"{self.expr}"


class Query(QueryExpr):
    source: QueryExpr
    columns: ColumnList

    def __init__(self, source: QueryExpr, columns: ColumnList) -> None:
        self.source = source
        self.columns = columns

    def __str__(self) -> str:
        source = (
            f"(\n{self.source}\n)" if isinstance(self.source, Query) else self.source
        )
        return f"SELECT\n{self.columns}\nFROM\n{source}"
