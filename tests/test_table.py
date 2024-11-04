"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

import unittest

from pysqlexpr.table import (
    DATETIME,
    INTEGER,
    BinaryType,
    Column,
    NumberType,
    StringType,
    Table,
)


class TestTable(unittest.TestCase):
    def test_types(self) -> None:
        self.assertEqual(NumberType(), NumberType())
        self.assertEqual(NumberType(), NumberType(38, 0))
        self.assertEqual(NumberType(9, 3), NumberType(9, 3))
        self.assertNotEqual(NumberType(9, 3), NumberType(9, 6))
        self.assertNotEqual(NumberType(9, 3), NumberType(6, 3))
        self.assertEqual(StringType(), StringType())
        self.assertEqual(BinaryType(), BinaryType())
        self.assertNotEqual(BinaryType(), StringType())

    def test_definition(self) -> None:
        self.maxDiff = None
        table = Table(
            "token",
            columns=[
                Column(
                    "id",
                    INTEGER,
                    nullable=False,
                    description="The unique identifier for a record.",
                ),
                Column("entity_id", INTEGER),
                Column(
                    "expires_at",
                    DATETIME,
                    description="The expiration date/time for this token.",
                ),
                Column(
                    "updated_at",
                    DATETIME,
                    nullable=False,
                    description="Timestamp of when this record was last updated.",
                ),
            ],
            description="Stores access tokens for entities.",
        )

        actual = str(table)
        expected = "\n".join(
            [
                "CREATE TABLE token (",
                "id NUMBER(38, 0) NOT NULL COMMENT 'The unique identifier for a record.',",
                "entity_id NUMBER(38, 0),",
                "expires_at DATETIME(9) COMMENT 'The expiration date/time for this token.',",
                "updated_at DATETIME(9) NOT NULL COMMENT 'Timestamp of when this record was last updated.'",
                ")",
                "COMMENT = 'Stores access tokens for entities.';",
            ]
        )
        self.assertMultiLineEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
