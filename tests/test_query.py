"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

import unittest

from pysqlexpr.boolean import ReturnsBool
from pysqlexpr.query import Column, FromExpr, Join, LateralJoin, Query, SourceExpr


class TestQuery(unittest.TestCase):
    def assertPackedEqual(self, expr: SourceExpr, text: str) -> None:
        self.assertEqual(expr.packed(), text)

    def assertSpaciousEqual(self, expr: SourceExpr, lines: list[str]) -> None:
        self.assertEqual(expr.spacious(), "\n".join(lines))

    def test_hash(self) -> None:
        s: set[Column] = set()
        s.add(Column("a", name="alias"))
        s.add(Column("b"))
        s.add(Column("c"))
        self.assertIn(Column("a", name="alias"), s)
        self.assertIn(Column("b"), s)
        self.assertIn(Column("c"), s)

    def test_where(self) -> None:
        query = Query(
            source=FromExpr("source"),
            columns=[Column("a", name="alias"), Column("b"), Column("c")],
            where=ReturnsBool("a > 1") & ReturnsBool("b IS NOT NULL"),
        )
        self.assertEqual(
            query,
            Query(
                source=FromExpr("source"),
                columns=[Column("a", name="alias"), Column("b"), Column("c")],
                where=ReturnsBool("a > 1") & ReturnsBool("b IS NOT NULL"),
            ),
        )
        self.assertPackedEqual(
            query, "SELECT a AS alias, b, c FROM source WHERE (a > 1 AND b IS NOT NULL)"
        )
        self.assertSpaciousEqual(
            query,
            [
                "SELECT",
                "    a AS alias,",
                "    b,",
                "    c",
                "FROM",
                "    source",
                "WHERE",
                "    (a > 1 AND b IS NOT NULL)",
            ],
        )

    def test_group_by(self) -> None:
        query = Query(
            source=FromExpr("source"),
            columns=[Column("a", name="alias"), Column("b"), Column("c")],
            group_by=["a", "b"],
        )
        self.assertPackedEqual(
            query, "SELECT a AS alias, b, c FROM source GROUP BY a, b"
        )
        self.assertSpaciousEqual(
            query,
            [
                "SELECT",
                "    a AS alias,",
                "    b,",
                "    c",
                "FROM",
                "    source",
                "GROUP BY a, b",
            ],
        )

    def test_join(self) -> None:
        flatten_expr = FromExpr(
            "FLATTEN(INPUT => a.phone_numbers)",
            name="p",
        )
        address_table = FromExpr("address", name="a")
        country_table = FromExpr("country", name="c")
        source_expr = Join(
            LateralJoin(
                address_table,
                flatten_expr,
            ),
            country_table,
            ReturnsBool("a.country_id = c.id"),
        )
        query = Query(
            source=source_expr,
            columns=[Column("a.zip"), Column("c.name"), Column("p.value")],
        )
        self.assertSpaciousEqual(
            query,
            [
                "SELECT",
                "    a.zip,",
                "    c.name,",
                "    p.value",
                "FROM",
                "    address AS a INNER JOIN LATERAL FLATTEN(INPUT => a.phone_numbers) AS p",
                "        INNER JOIN country AS c",
                "            ON a.country_id = c.id",
            ],
        )


if __name__ == "__main__":
    unittest.main()
