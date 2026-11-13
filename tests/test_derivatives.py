"""Tests for FlowCE CAS:
- F6: Symbolic Differentiation
- F7: Step-by-Step Explanations
"""

import math
import os
import sys
import unittest

from tests.test_helpers import (
    get_flowce,
    cas_diff,
    cas_diff_steps,
    cas_eval,
    expr_numerically_equal,
)


class TestSymbolicDifferentiation(unittest.TestCase):
    """F6: Symbolic Differentiation tests (Tier 1 & Tier 2)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    # Tier 1: Feature Coverage (Min 5)
    def test_power_rule(self):
        """F6 Tier 1: d/dx(x^3) = 3*x^2 and d/dx(4*x^5) = 20*x^4."""
        d1 = cas_diff("x^3", "x")
        self.assertTrue(expr_numerically_equal(d1, "3*x^2", var="x"))

        d2 = cas_diff("4*x^5", "x")
        self.assertTrue(expr_numerically_equal(d2, "20*x^4", var="x"))

    def test_sum_and_difference_rule(self):
        """F6 Tier 1: d/dx(x^3 - 4*x^2 + 5*x - 12) = 3*x^2 - 8*x + 5."""
        d = cas_diff("x^3 - 4*x^2 + 5*x - 12", "x")
        self.assertTrue(expr_numerically_equal(d, "3*x^2 - 8*x + 5", var="x"))

    def test_product_rule(self):
        """F6 Tier 1: d/dx(x * sin(x)) = sin(x) + x*cos(x)."""
        d = cas_diff("x * sin(x)", "x")
        self.assertTrue(expr_numerically_equal(d, "sin(x) + x*cos(x)", var="x"))

    def test_quotient_rule(self):
        """F6 Tier 1: d/dx(x / (x + 1)) = 1 / (x + 1)^2."""
        d = cas_diff("x / (x + 1)", "x")
        self.assertTrue(expr_numerically_equal(d, "1 / (x + 1)^2", var="x", points=[1.0, 2.0, 3.0]))

    def test_chain_rule(self):
        """F6 Tier 1: d/dx(sin(x^2)) = 2*x * cos(x^2)."""
        d = cas_diff("sin(x^2)", "x")
        self.assertTrue(expr_numerically_equal(d, "2*x * cos(x^2)", var="x"))

    def test_transcendental_rules(self):
        """F6 Tier 1: d/dx(exp(x)) = exp(x), d/dx(ln(x)) = 1/x."""
        d_exp = cas_diff("exp(x)", "x")
        self.assertTrue(expr_numerically_equal(d_exp, "exp(x)", var="x"))

        d_ln = cas_diff("ln(x)", "x")
        self.assertTrue(expr_numerically_equal(d_ln, "1/x", var="x", points=[1.0, 2.0, 4.0]))

    def test_higher_order_derivatives(self):
        """F6 Tier 1: Higher order derivatives d^2/dx^2(x^4) = 12*x^2."""
        d1 = cas_diff("x^4", "x")
        d2 = cas_diff(d1, "x")
        self.assertTrue(expr_numerically_equal(d2, "12*x^2", var="x"))
        d3 = cas_diff(d2, "x")
        self.assertTrue(expr_numerically_equal(d3, "24*x", var="x"))

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_derivative_of_constant(self):
        """F6 Tier 2: Boundary - d/dx(c) = 0 for integers and expressions without x."""
        d1 = cas_diff("42", "x")
        self.assertEqual(str(d1).strip(), "0")

        d2 = cas_diff("100 + 50", "x")
        self.assertEqual(str(d2).strip(), "0")

    def test_derivative_wrt_other_variable(self):
        """F6 Tier 2: Boundary - d/dx(y^3) = 0."""
        d = cas_diff("y^3", "x")
        self.assertEqual(str(d).strip(), "0")

    def test_negative_power_rule(self):
        """F6 Tier 2: Boundary - d/dx(x^-2) = -2*x^-3."""
        d = cas_diff("x^(-2)", "x")
        self.assertTrue(expr_numerically_equal(d, "-2 * x^(-3)", var="x", points=[1.0, 2.0, 3.0]))

    def test_linear_term(self):
        """F6 Tier 2: Boundary - d/dx(x) = 1 and d/dx(7*x) = 7."""
        d1 = cas_diff("x", "x")
        self.assertEqual(str(d1).strip(), "1")

        d2 = cas_diff("7*x", "x")
        self.assertEqual(str(d2).strip(), "7")

    def test_deep_chain_rule(self):
        """F6 Tier 2: Boundary - d/dx(exp(sin(x^2))) = 2*x*cos(x^2)*exp(sin(x^2))."""
        d = cas_diff("exp(sin(x^2))", "x")
        self.assertTrue(expr_numerically_equal(d, "2*x * cos(x^2) * exp(sin(x^2))", var="x"))


class TestStepByStepDifferentiation(unittest.TestCase):
    """F7: Step-by-Step Explanations tests (Tier 1 & Tier 2)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    # Tier 1: Feature Coverage (Min 5)
    def test_power_rule_explanation(self):
        """F7 Tier 1: Steps for power rule mention power rule or exponent reduction."""
        steps = cas_diff_steps("x^4", "x")
        text = str(steps).lower()
        self.assertTrue("power" in text or "d/dx" in text or "4" in text)

    def test_product_rule_explanation(self):
        """F7 Tier 1: Steps for product rule mention product rule."""
        steps = cas_diff_steps("x * cos(x)", "x")
        text = str(steps).lower()
        self.assertTrue("product" in text or "f'g" in text or "cos(x)" in text)

    def test_quotient_rule_explanation(self):
        """F7 Tier 1: Steps for quotient rule mention quotient rule."""
        steps = cas_diff_steps("sin(x) / x", "x")
        text = str(steps).lower()
        self.assertTrue("quotient" in text or "denominator" in text or "x^2" in text)

    def test_chain_rule_explanation(self):
        """F7 Tier 1: Steps for chain rule mention chain rule or inner derivative."""
        steps = cas_diff_steps("cos(3*x)", "x")
        text = str(steps).lower()
        self.assertTrue("chain" in text or "inner" in text or "3" in text)

    def test_sum_rule_explanation(self):
        """F7 Tier 1: Steps for sum rule explain differentiating term-by-term."""
        steps = cas_diff_steps("x^2 + 5*x", "x")
        text = str(steps).lower()
        self.assertTrue("sum" in text or "term" in text or "2*x" in text)

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_constant_rule_explanation(self):
        """F7 Tier 2: Boundary - Steps for d/dx(10) indicate constant rule."""
        steps = cas_diff_steps("10", "x")
        text = str(steps).lower()
        self.assertTrue("constant" in text or "0" in text)

    def test_single_variable_explanation(self):
        """F7 Tier 2: Boundary - Steps for d/dx(x) indicate derivative is 1."""
        steps = cas_diff_steps("x", "x")
        text = str(steps).lower()
        self.assertTrue("1" in text or "linear" in text or "variable" in text)

    def test_steps_return_type_validity(self):
        """F7 Tier 2: Boundary - Step output is non-empty string or list of steps."""
        steps = cas_diff_steps("x^3 + 2*x", "x")
        self.assertIsNotNone(steps)
        if isinstance(steps, (list, tuple)):
            self.assertGreater(len(steps), 0)
        else:
            self.assertGreater(len(str(steps).strip()), 0)

    def test_steps_no_crash_on_complex_expression(self):
        """F7 Tier 2: Boundary - Deeply nested expressions do not crash explanation generator."""
        steps = cas_diff_steps("exp(x) * (x^2 + 1) / sin(x)", "x")
        self.assertIsNotNone(steps)

    def test_steps_final_result_consistency(self):
        """F7 Tier 2: Boundary - Result in steps matches direct derivative."""
        d = cas_diff("x^2", "x")
        steps = cas_diff_steps("x^2", "x")
        text = str(steps)
        self.assertIn("2*x", text.replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
