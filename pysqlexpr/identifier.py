"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

from typing import ClassVar, final


@final
class Identifier:
    """
    An identifier in a Snowflake SQL expression.

    This class helps avoid parse errors when the schema, table or column identifier is a reserved or limited word.
    We take a moderately conservative approach: we exclude all reserved and limited keywords except those that cannot
    be used as an identifier in a `SHOW` command.

    Accessors in a VARIANT path expression are always quoted when converted into a string. Components of a path should
    be separated by a forward slash (`/`) and are translated into Snowflake colon (`:`).
    """

    __slots__ = ("identifier", "path")

    keywords: ClassVar[list[str]]
    identifier: str
    path: str | None

    def __init__(self, identifier: str, *, path: str | None = None):
        self.identifier = identifier
        self.path = path

    @property
    def raw(self) -> str:
        return self.identifier

    def __repr__(self) -> str:
        identifier = (
            f"{self.identifier}_"
            if self.identifier.upper() in self.keywords
            else self.identifier
        )
        path = (
            ":"
            + ":".join(
                '"' + component.replace('"', '""') + '"'
                for component in self.path.split("/")
            )
            if self.path is not None
            else ""
        )
        return identifier + path


# fmt: off
Identifier.keywords = [
    "ALL", "ALTER", "AND", "ANY", "AS", "BETWEEN", "BY", "CASE", "CAST", "CHECK", "COLUMN", "CONNECT", "CONSTRAINT",
    "CREATE", "CROSS", "CURRENT", "DELETE", "DISTINCT", "DROP", "ELSE", "EXISTS", "FALSE", "FOLLOWING", "FOR", "FROM",
    "FULL", "GRANT", "GROUP", "HAVING", "ILIKE", "IN", "INCREMENT", "INNER", "INSERT", "INTERSECT", "INTO", "IS",
    "JOIN", "LATERAL", "LEFT", "LIKE", "LOCALTIME", "LOCALTIMESTAMP", "MINUS", "NATURAL", "NOT", "NULL", "OF", "ON",
    "OR", "ORDER", "QUALIFY", "REGEXP", "REVOKE", "RIGHT", "RLIKE", "ROW", "ROWS", "SAMPLE", "SELECT", "SET", "SOME",
    "START", "TABLE", "TABLESAMPLE", "THEN", "TO", "TRIGGER", "TRUE", "UNION", "UNIQUE", "UPDATE", "USING", "VALUES",
    "WHEN", "WHENEVER", "WHERE", "WITH"]
# fmt: on
