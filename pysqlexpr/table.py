import re
from typing import ClassVar

from pysqlexpr.identifier import Identifier

_sql_quoted_str_table = str.maketrans(
    {
        "\\": "\\\\",
        "'": "\\'",
        '"': '\\"',
        "\0": "\\0",
        "\b": "\\b",
        "\f": "\\f",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
    }
)


def sql_quoted_string(text: str) -> str:
    if re.search(r"[\\\0\b\f\n\r\t]", text):
        text = text.translate(_sql_quoted_str_table)
    elif "'" in text:
        text = text.replace("'", "''")
    return f"'{text}'"


class DataType:
    __slots__ = ()

    name: ClassVar[str] = "<NULL>"

    def __eq__(self, op: object) -> bool:
        return isinstance(op, DataType) and self.name == op.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name


class BooleanType(DataType):
    name: ClassVar[str] = "BOOLEAN"


class NumberType(DataType):
    __slots__ = ("precision", "scale")

    precision: int
    scale: int

    name: ClassVar[str] = "NUMBER"

    def __init__(self, precision: int | None = None, scale: int | None = None) -> None:
        if precision is not None:
            self.precision = precision
        else:
            self.precision = 38
        if scale is not None:
            self.scale = scale
        else:
            self.scale = 0

    def __eq__(self, op: object) -> bool:
        return (
            isinstance(op, NumberType)
            and self.precision == op.precision
            and self.scale == op.scale
        )

    def __hash__(self) -> int:
        return hash((self.name, self.precision, self.scale))

    def __str__(self) -> str:
        return f"{self.name}({self.precision}, {self.scale})"


class FloatType(DataType):
    name: ClassVar[str] = "FLOAT"


class _LengthType(DataType):
    "A type that has a length property."

    __slots__ = ("length",)

    length: int

    def __init__(self, length: int | None, default: int) -> None:
        if length is not None:
            self.length = length
        else:
            self.length = default

    def __eq__(self, op: object) -> bool:
        return isinstance(op, _LengthType) and self.length == op.length

    def __hash__(self) -> int:
        return hash((self.name, self.length))

    def __str__(self) -> str:
        return f"{self.name}({self.length})"


class StringType(_LengthType):
    name: ClassVar[str] = "STRING"

    def __init__(self, length: int | None = None) -> None:
        super().__init__(length, 16777216)


class BinaryType(_LengthType):
    name: ClassVar[str] = "BINARY"

    def __init__(self, length: int | None = None) -> None:
        super().__init__(length, 8388608)


class DateType(DataType):
    name: ClassVar[str] = "DATE"


class _PrecisionType(DataType):
    "A type that has a precision property."

    __slots__ = ("precision",)

    precision: int

    def __init__(self, precision: int | None = None) -> None:
        if precision is not None:
            self.precision = precision
        else:
            self.precision = 9

    def __eq__(self, op: object) -> bool:
        return isinstance(op, _PrecisionType) and self.precision == op.precision

    def __hash__(self) -> int:
        return hash((self.name, self.precision))

    def __str__(self) -> str:
        return f"{self.name}({self.precision})"


class TimeType(_PrecisionType):
    name: ClassVar[str] = "TIME"


class DateTimeType(_PrecisionType):
    name: ClassVar[str] = "DATETIME"


class VariantType(DataType):
    name: ClassVar[str] = "VARIANT"


class ArrayType(DataType):
    name: ClassVar[str] = "ARRAY"


class ObjectType(DataType):
    name: ClassVar[str] = "OBJECT"


BOOLEAN = BooleanType()
INTEGER = NumberType(38, 0)
NUMBER = NumberType()
FLOAT = FloatType()
STRING = StringType()
BINARY = BinaryType()
DATE = DateType()
TIME = TimeType()
DATETIME = DateTimeType()
VARIANT = VariantType()
ARRAY = ArrayType()
OBJECT = ObjectType()


class Column:
    __slots__ = ("name", "data_type", "nullable", "default", "description")

    name: Identifier
    data_type: DataType
    nullable: bool
    default: str | None
    description: str | None

    def __init__(
        self,
        name: str,
        type: DataType,
        *,
        nullable: bool = True,
        default: str | None = None,
        description: str | None = None,
    ) -> None:
        self.name = Identifier(name)
        self.data_type = type
        self.nullable = nullable
        self.default = default
        self.description = description

    @property
    def default_expr(self) -> str:
        if self.default is None:
            raise ValueError("default value is NULL")

        if isinstance(self.data_type, DateTimeType):
            m = re.match(
                r"^'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})'$",
                self.default,
            )
            if m:
                return f"TIMESTAMP {self.default}"

        return self.default

    @property
    def column_spec(self) -> str:
        return f"{self.name} {self.data_spec}"

    @property
    def data_spec(self) -> str:
        nullable = " NOT NULL" if not self.nullable else ""
        default = f" DEFAULT {self.default_expr}" if self.default is not None else ""
        description = f" COMMENT {self.comment}" if self.description is not None else ""
        return f"{self.data_type}{nullable}{default}{description}"

    @property
    def comment(self) -> str | None:
        if self.description is not None:
            return sql_quoted_string(self.description)
        else:
            return None

    def __str__(self) -> str:
        return self.column_spec


class Table:
    __slots__ = ("name", "columns", "description")

    name: Identifier
    columns: list[Column]
    description: str | None

    def __init__(
        self, name: str, columns: list[Column], *, description: str | None = None
    ) -> None:
        self.name = Identifier(name)
        self.columns = columns
        self.description = description

    def as_stmt(self, *, replace: bool = False) -> str:
        """
        Emits a SQL statement for creating the table.

        :param replace: True for `CREATE OR REPLACE`. False for `CREATE`.
        """

        definitions = ",\n".join(str(c) for c in self.columns)
        comment = (
            f"\nCOMMENT = {sql_quoted_string(self.description)}"
            if self.description
            else ""
        )
        or_replace = " OR REPLACE" if replace else ""
        return f"CREATE{or_replace} TABLE {self.name} (\n{definitions}\n){comment};"

    def __str__(self) -> str:
        """
        Emits a SQL statement for creating the table.
        """

        return self.as_stmt()
