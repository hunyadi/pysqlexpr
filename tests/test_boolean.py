"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

import unittest

from pysqlexpr.boolean import BoolExpr, ReturnsBool


class TestBoolean(unittest.TestCase):
    def assertDisplayEqual(self, expr: BoolExpr, text: str) -> None:
        self.assertEqual(str(expr), text)

    def assertPackedEqual(self, expr: BoolExpr, text: str) -> None:
        self.assertEqual(expr.packed(), text)

    def assertSpaciousEqual(self, expr: BoolExpr, lines: list[str]) -> None:
        self.assertEqual(expr.spacious(), "\n".join(lines))

    def test_equal(self) -> None:
        E = ReturnsBool
        self.assertEqual(E("a"), E("a"))
        self.assertEqual(E("a") & E("b"), E("a") & E("b"))
        self.assertNotEqual(E("a"), E("b"))
        self.assertNotEqual(E("a") & E("b"), E("a") | E("b"))
        self.assertNotEqual(E("a") & E("a"), E("a") & E("b"))

    def test_hash(self) -> None:
        E = ReturnsBool
        s: set[BoolExpr] = set()
        s.add(E("a") & E("a"))
        s.add(E("a") | E("a"))
        s.add(E("a") & E("b"))
        s.add(E("a") | E("b"))
        self.assertIn(E("a") & E("a"), s)
        self.assertIn(E("a") | E("a"), s)
        self.assertIn(E("a") & E("b"), s)
        self.assertIn(E("a") | E("b"), s)

    def test_logical(self) -> None:
        E = ReturnsBool

        # binary expressions
        self.assertPackedEqual(E("a") & E("b"), "(a AND b)")
        self.assertPackedEqual(E("a") | E("b"), "(a OR b)")

        # homogeneous expressions
        self.assertPackedEqual(E("a") & E("b") & E("c"), "(a AND b AND c)")
        self.assertPackedEqual(E("a") | E("b") | E("c"), "(a OR b OR c)")

        # heterogeneous expressions
        self.assertPackedEqual(E("a") & E("b") | E("c"), "((a AND b) OR c)")
        self.assertPackedEqual(E("a") | E("b") & E("c"), "(a OR (b AND c))")

        # optimal output
        self.assertDisplayEqual(E("a") & E("b") | E("c"), "((a AND b) OR c)")
        self.assertDisplayEqual(E("a") | E("b") & E("c"), "(a OR (b AND c))")

        # spacious output
        self.assertSpaciousEqual(
            E("a") | E("b") & E("c"),
            [
                "(",
                "    a",
                "OR",
                "    (",
                "        b",
                "    AND",
                "        c",
                "    )",
                ")",
            ],
        )


if __name__ == "__main__":
    unittest.main()
