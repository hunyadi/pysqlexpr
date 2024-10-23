"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

import unittest

from pysqlexpr.query import Column, FromExpr, Query, QueryExpr


class TestQuery(unittest.TestCase):
    def assertSqlEqual(self, expr: QueryExpr, text: str) -> None:
        self.assertEqual(str(expr), text)

    def test_query(self) -> None:
        query = Query(
            source=FromExpr("source"),
            columns=[Column("a", name="a"), Column("b"), Column("c")],
        )
        self.assertSqlEqual(query, "SELECT a AS a, b, c FROM source")

        # spacious output
        self.assertEqual(
            query.spacious(),
            "\n".join(
                [
                    "SELECT",
                    "    a AS a,",
                    "    b,",
                    "    c",
                    "FROM",
                    "    source",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
