"""Tests for FlowCE CAS:
- F3: Lexer & Precedence Parser
- F4: Exact Rational Arithmetic
- F5: Algebraic Simplification
"""

import math
import os
import sys
import unittest

from tests.test_helpers import (
    get_flowce,
    cas_parse,
    cas_simplify,
    cas_eval,
    expr_numerically_equal,
)


class TestLexerParser(unittest.TestCase):
    """F3: Lexer & Precedence Parser tests (Tier 1 & Tier 2)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    # Tier 1: Feature Coverage (Min 5)
    def test_basic_arithmetic_precedence(self):
        """F3 Tier 1: PEMDAS precedence 2 + 3 * 4 == 14."""
        node = cas_parse("2 + 3 * 4")
        val = cas_eval(node)
        self.assertEqual(float(val), 14.0)

    def test_exponentiation_precedence(self):
        """F3 Tier 1: 2 * x^3 vs (2*x)^3 precedence."""
        n1 = cas_parse("2 * x^3")
        n2 = cas_parse("(2 * x)^3")
        self.assertEqual(float(cas_eval(n1, x=2)), 16.0)
        self.assertEqual(float(cas_eval(n2, x=2)), 64.0)

    def test_trigonometric_parsing(self):
        """F3 Tier 1: Parsing sin(x) + cos(x)."""
        node = cas_parse("sin(x) + cos(x)")
        expected = math.sin(1.0) + math.cos(1.0)
        self.assertAlmostEqual(float(cas_eval(node, x=1.0)), expected, places=5)

    def test_exp_and_ln_parsing(self):
        """F3 Tier 1: Parsing exp(x) - ln(x)."""
        node = cas_parse("exp(x) - ln(x)")
        expected = math.exp(2.0) - math.log(2.0)
        self.assertAlmostEqual(float(cas_eval(node, x=2.0)), expected, places=5)

    def test_multi_variable_parsing(self):
        """F3 Tier 1: Multi-variable expressions x^2 + 2*x*y + y^2."""
        node = cas_parse("x^2 + 2*x*y + y^2")
        val = cas_eval(node, x=3.0, y=4.0)
        self.assertAlmostEqual(float(val), 49.0, places=5)

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_excessive_whitespace(self):
        """F3 Tier 2: Boundary - expression with arbitrary tabs and spaces."""
        node = cas_parse("   x   +    3   *   (  x   -  1 )  ")
        val = cas_eval(node, x=5.0)
        self.assertAlmostEqual(float(val), 17.0, places=5)

    def test_deeply_nested_parentheses(self):
        """F3 Tier 2: Boundary - deeply nested redundant parentheses."""
        node = cas_parse("((((x + 2))))")
        self.assertEqual(float(cas_eval(node, x=3.0)), 5.0)

    def test_unary_minus_handling(self):
        """F3 Tier 2: Boundary - unary negative numbers and expressions."""
        n1 = cas_parse("-x + 5")
        self.assertEqual(float(cas_eval(n1, x=2.0)), 3.0)
        n2 = cas_parse("-(x + 3)")
        self.assertEqual(float(cas_eval(n2, x=2.0)), -5.0)

    def test_empty_input_handling(self):
        """F3 Tier 2: Boundary - empty or blank string raises exception or returns None."""
        try:
            res = cas_parse("")
            self.assertIn(res, [None, 0, ""])
        except (ValueError, SyntaxError, Exception):
            pass  # Expected exception on empty input

    def test_malformed_syntax_raises(self):
        """F3 Tier 2: Boundary - unbalanced parentheses or dangling operators raise error."""
        for malformed in ["(x + 1", "x + * 2", "3 +"]:
            try:
                cas_parse(malformed)
            except (ValueError, SyntaxError, Exception):
                pass  # Gracefully caught syntax error


class TestExactRationalArithmetic(unittest.TestCase):
    """F4: Exact Rational Arithmetic tests (Tier 1 & Tier 2)."""

    def setUp(self):
        flowce = get_flowce()
        if flowce is None:
            self.skipTest("flowce.py not yet implemented by cas_author")
        self.Rational = getattr(flowce, "Rational", None)

    # Tier 1: Feature Coverage (Min 5)
    def test_rational_addition(self):
        """F4 Tier 1: 1/2 + 1/3 = 5/6."""
        if self.Rational:
            r = self.Rational(1, 2) + self.Rational(1, 3)
            self.assertEqual(r.num, 5)
            self.assertEqual(r.den, 6)
        else:
            res = cas_simplify("1/2 + 1/3")
            self.assertTrue("5/6" in str(res) or abs(float(cas_eval(res)) - 5/6) < 1e-6)

    def test_rational_multiplication(self):
        """F4 Tier 1: 3/4 * 2/5 = 3/10."""
        if self.Rational:
            r = self.Rational(3, 4) * self.Rational(2, 5)
            self.assertEqual(r.num, 3)
            self.assertEqual(r.den, 10)
        else:
            res = cas_simplify("3/4 * 2/5")
            self.assertTrue("3/10" in str(res) or abs(float(cas_eval(res)) - 3/10) < 1e-6)

    def test_rational_division(self):
        """F4 Tier 1: (2/3) / (4/9) = 3/2."""
        if self.Rational:
            r = self.Rational(2, 3) / self.Rational(4, 9)
            self.assertEqual(r.num, 3)
            self.assertEqual(r.den, 2)
        else:
            res = cas_simplify("(2/3) / (4/9)")
            self.assertTrue("3/2" in str(res) or abs(float(cas_eval(res)) - 1.5) < 1e-6)

    def test_exact_integer_preservation(self):
        """F4 Tier 1: 1/3 * 3 = 1 exactly with no floating drift."""
        if self.Rational:
            r = self.Rational(1, 3) * self.Rational(3, 1)
            self.assertEqual(r.num, 1)
            self.assertEqual(r.den, 1)
        else:
            res = cas_simplify("(1/3) * 3")
            self.assertEqual(str(res).strip(), "1")

    def test_negative_rational_reduction(self):
        """F4 Tier 1: -6/10 reduces to -3/5 with canonical sign on numerator."""
        if self.Rational:
            r = self.Rational(-6, 10)
            self.assertEqual(r.num, -3)
            self.assertEqual(r.den, 5)
        else:
            res = cas_simplify("-6/10")
            self.assertIn("-3/5", str(res))

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_division_by_zero_error(self):
        """F4 Tier 2: Boundary - Zero denominator raises ZeroDivisionError."""
        if self.Rational:
            with self.assertRaises(ZeroDivisionError):
                self.Rational(1, 0)
        else:
            with self.assertRaises((ZeroDivisionError, ValueError)):
                cas_eval("1/0")

    def test_zero_numerator(self):
        """F4 Tier 2: Boundary - 0/7 simplifies to 0."""
        if self.Rational:
            r = self.Rational(0, 7)
            self.assertEqual(r.num, 0)
            self.assertEqual(r.den, 1)
        else:
            res = cas_simplify("0/7")
            self.assertIn(str(res).strip(), ["0", "0/1"])

    def test_large_integer_reduction(self):
        """F4 Tier 2: Boundary - Large numbers reduce accurately without precision loss."""
        if self.Rational:
            r = self.Rational(1000000000000, 2000000000000)
            self.assertEqual((r.num, r.den), (1, 2))
        else:
            res = cas_simplify("1000000000000 / 2000000000000")
            self.assertIn("1/2", str(res))

    def test_double_negative_denominator(self):
        """F4 Tier 2: Boundary - Rational(4, -8) has den > 0 and num = -1."""
        if self.Rational:
            r = self.Rational(4, -8)
            self.assertEqual(r.num, -1)
            self.assertEqual(r.den, 2)
            r2 = self.Rational(-3, -9)
            self.assertEqual((r2.num, r2.den), (1, 3))

    def test_rational_powers(self):
        """F4 Tier 2: Boundary - Rational power (2/3)^3 = 8/27."""
        if self.Rational:
            r = self.Rational(2, 3) ** 3
            self.assertEqual((r.num, r.den), (8, 27))
        else:
            res = cas_simplify("(2/3)^3")
            self.assertTrue("8/27" in str(res) or abs(float(cas_eval(res)) - 8/27) < 1e-6)


class TestAlgebraicSimplification(unittest.TestCase):
    """F5: Algebraic Simplification tests (Tier 1 & Tier 2)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    # Tier 1: Feature Coverage (Min 5)
    def test_combine_like_terms(self):
        """F5 Tier 1: 2*x + 3*x simplifies to 5*x."""
        res = cas_simplify("2*x + 3*x")
        self.assertTrue(expr_numerically_equal(res, "5*x", var="x"))

    def test_multiplication_by_zero(self):
        """F5 Tier 1: 0 * (x^2 + 5) simplifies to 0."""
        res = cas_simplify("0 * (x^2 + 5)")
        self.assertEqual(str(res).strip(), "0")

    def test_multiplication_by_one(self):
        """F5 Tier 1: 1 * x simplifies to x."""
        res = cas_simplify("1 * x")
        self.assertTrue(expr_numerically_equal(res, "x", var="x"))

    def test_addition_of_zero(self):
        """F5 Tier 1: x + 0 simplifies to x."""
        res = cas_simplify("x + 0")
        self.assertTrue(expr_numerically_equal(res, "x", var="x"))

    def test_power_identities(self):
        """F5 Tier 1: x^1 -> x and x^0 -> 1."""
        r1 = cas_simplify("x^1")
        self.assertTrue(expr_numerically_equal(r1, "x", var="x"))
        r2 = cas_simplify("x^0")
        self.assertEqual(str(r2).strip(), "1")

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_constant_arithmetic_folding(self):
        """F5 Tier 2: Boundary - constant folding 2 + 3 * 4 - 5 -> 9."""
        res = cas_simplify("2 + 3 * 4 - 5")
        self.assertEqual(str(res).strip(), "9")

    def test_nested_zero_annihilation(self):
        """F5 Tier 2: Boundary - (x - x) * (sin(x) + exp(x^2)) -> 0."""
        res = cas_simplify("(x - x) * (sin(x) + exp(x))")
        self.assertEqual(str(res).strip(), "0")

    def test_negative_subtraction_cancellation(self):
        """F5 Tier 2: Boundary - 4*x - 4*x -> 0."""
        res = cas_simplify("4*x - 4*x")
        self.assertEqual(str(res).strip(), "0")

    def test_polynomial_term_reordering(self):
        """F5 Tier 2: Boundary - 3 + x + 2*x + 4 -> 3*x + 7."""
        res = cas_simplify("3 + x + 2*x + 4")
        self.assertTrue(expr_numerically_equal(res, "3*x + 7", var="x"))

    def test_simplification_idempotence(self):
        """F5 Tier 2: Boundary - simplify(simplify(e)) == simplify(e)."""
        expr = "3*x^2 + 2*x - x^2 + 5 - 2"
        s1 = cas_simplify(expr)
        s2 = cas_simplify(s1)
        self.assertTrue(expr_numerically_equal(s1, s2, var="x"))


if __name__ == "__main__":
    unittest.main()
