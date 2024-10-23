"""
pysqlexpr: Expressive SQL for Python

:see: https://github.com/hunyadi/pysqlexpr
"""

import unittest

from pysqlexpr.boolean import BoolExpr, ReturnsBool


class TestBoolean(unittest.TestCase):
    def assertSqlEqual(self, expr: BoolExpr, text: str) -> None:
        self.assertEqual(str(expr), text)

    def test_logical(self) -> None:
        E = ReturnsBool

        # binary expressions
        self.assertSqlEqual(E("a") & E("b"), "(a AND b)")
        self.assertSqlEqual(E("a") | E("b"), "(a OR b)")

        # homogeneous expressions
        self.assertSqlEqual(E("a") & E("b") & E("c"), "(a AND b AND c)")
        self.assertSqlEqual(E("a") | E("b") | E("c"), "(a OR b OR c)")

        # heterogeneous expressions
        self.assertSqlEqual(E("a") & E("b") | E("c"), "((a AND b) OR c)")
        self.assertSqlEqual(E("a") | E("b") & E("c"), "(a OR (b AND c))")


if __name__ == "__main__":
    unittest.main()
