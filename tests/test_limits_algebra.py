"""Tests for FlowCE CAS:
- F9: Limits & Series (L'Hopital's Rule, Taylor / Maclaurin series)
- F10: Tangent & Normal Lines
"""

import math
import os
import sys
import unittest

from tests.test_helpers import (
    get_flowce,
    cas_limit,
    cas_series,
    cas_tangent,
    cas_normal,
    cas_eval,
    expr_numerically_equal,
)


class TestLimitsAndSeries(unittest.TestCase):
    """F9: Limits & Series tests (Tier 1 & Tier 2)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    # Tier 1: Feature Coverage (Min 5)
    def test_direct_substitution_limit(self):
        """F9 Tier 1: lim_{x->2} (x^2 + 3*x) = 10."""
        val = cas_limit("x^2 + 3*x", "x", 2)
        self.assertAlmostEqual(float(val), 10.0, places=4)

    def test_factoring_rational_limit(self):
        """F9 Tier 1: lim_{x->1} (x^2 - 1)/(x - 1) = 2."""
        val = cas_limit("(x^2 - 1) / (x - 1)", "x", 1)
        self.assertAlmostEqual(float(val), 2.0, places=3)

    def test_lhopital_trig_limit(self):
        """F9 Tier 1: lim_{x->0} sin(x)/x = 1 via L'Hopital."""
        val = cas_limit("sin(x) / x", "x", 0)
        self.assertAlmostEqual(float(val), 1.0, places=3)

    def test_maclaurin_series_sin(self):
        """F9 Tier 1: Taylor series for sin(x) at x=0 order 4: x - (1/6)*x^3."""
        s = cas_series("sin(x)", "x", 0, order=4)
        expected = "x - (1/6)*x^3"
        self.assertTrue(expr_numerically_equal(s, expected, var="x", points=[0.1, 0.2, 0.5]))

    def test_maclaurin_series_exp(self):
        """F9 Tier 1: Taylor series for exp(x) at x=0 order 4: 1 + x + (1/2)*x^2 + (1/6)*x^3."""
        s = cas_series("exp(x)", "x", 0, order=4)
        expected = "1 + x + (1/2)*x^2 + (1/6)*x^3"
        self.assertTrue(expr_numerically_equal(s, expected, var="x", points=[0.1, 0.2, 0.5]))

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_limit_of_constant(self):
        """F9 Tier 2: Boundary - lim_{x->5} 42 = 42."""
        val = cas_limit("42", "x", 5)
        self.assertAlmostEqual(float(val), 42.0, places=4)

    def test_lhopital_exp_limit(self):
        """F9 Tier 2: Boundary - lim_{x->0} (exp(x) - 1)/x = 1."""
        val = cas_limit("(exp(x) - 1) / x", "x", 0)
        self.assertAlmostEqual(float(val), 1.0, places=3)

    def test_maclaurin_series_cos(self):
        """F9 Tier 2: Boundary - Taylor series for cos(x) at x=0 order 5: 1 - (1/2)*x^2 + (1/24)*x^4."""
        s = cas_series("cos(x)", "x", 0, order=5)
        expected = "1 - (1/2)*x^2 + (1/24)*x^4"
        self.assertTrue(expr_numerically_equal(s, expected, var="x", points=[0.1, 0.2, 0.5]))

    def test_limit_at_negative_point(self):
        """F9 Tier 2: Boundary - lim_{x->-3} (x^2) = 9."""
        val = cas_limit("x^2", "x", -3)
        self.assertAlmostEqual(float(val), 9.0, places=4)

    def test_maclaurin_order_one(self):
        """F9 Tier 2: Boundary - 1st order Taylor polynomial for f(x) is tangent approximation."""
        s = cas_series("x^3 + 2*x + 5", "x", 0, order=2)
        # Around 0: f(0)=5, f'(0)=2 -> 5 + 2*x
        self.assertTrue(expr_numerically_equal(s, "5 + 2*x", var="x", points=[0.1, 0.2]))


class TestTangentAndNormalLines(unittest.TestCase):
    """F10: Tangent & Normal Lines tests (Tier 1 & Tier 2)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    # Tier 1: Feature Coverage (Min 5)
    def test_tangent_line_parabola(self):
        """F10 Tier 1: Tangent line to y = x^2 at x = 2 is y = 4*x - 4."""
        line = cas_tangent("x^2", 2, "x")
        # At x=2, y should be 4; at x=3, y should be 8
        val_at_2 = cas_eval(line, x=2.0)
        val_at_3 = cas_eval(line, x=3.0)
        self.assertAlmostEqual(float(val_at_2), 4.0, places=4)
        self.assertAlmostEqual(float(val_at_3), 8.0, places=4)

    def test_normal_line_slope(self):
        """F10 Tier 1: Normal line to y = x^2 at x = 2 has slope -1/4."""
        line = cas_normal("x^2", 2, "x")
        # Normal line: y - 4 = -0.25 * (x - 2) -> y = -0.25*x + 4.5
        val_at_2 = cas_eval(line, x=2.0)
        val_at_6 = cas_eval(line, x=6.0)
        self.assertAlmostEqual(float(val_at_2), 4.0, places=4)
        self.assertAlmostEqual(float(val_at_6), 3.0, places=4)

    def test_tangent_line_trig(self):
        """F10 Tier 1: Tangent line to y = sin(x) at x = 0 is y = x."""
        line = cas_tangent("sin(x)", 0, "x")
        self.assertTrue(expr_numerically_equal(line, "x", var="x", points=[0.0, 1.0, 2.0]))

    def test_tangent_cubic_inflection(self):
        """F10 Tier 1: Tangent line to y = x^3 at x = 0 is y = 0."""
        line = cas_tangent("x^3", 0, "x")
        val = cas_eval(line, x=5.0)
        self.assertAlmostEqual(float(val), 0.0, places=4)

    def test_tangent_horizontal_extrema(self):
        """F10 Tier 1: Tangent line to y = x^3 - 3*x at x = 1 is horizontal y = -2."""
        line = cas_tangent("x^3 - 3*x", 1, "x")
        val1 = cas_eval(line, x=1.0)
        val2 = cas_eval(line, x=10.0)
        self.assertAlmostEqual(float(val1), -2.0, places=4)
        self.assertAlmostEqual(float(val2), -2.0, places=4)

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_tangent_passes_through_curve_point(self):
        """F10 Tier 2: Boundary - Tangent line at x=c passes through (c, f(c))."""
        for c in [1.0, 2.5, -1.0]:
            f_expr = "x^2 + 2*x"
            tangent = cas_tangent(f_expr, c, "x")
            f_val = cas_eval(f_expr, x=c)
            t_val = cas_eval(tangent, x=c)
            self.assertAlmostEqual(float(f_val), float(t_val), places=4)

    def test_normal_passes_through_curve_point(self):
        """F10 Tier 2: Boundary - Normal line at x=c passes through (c, f(c))."""
        c = 1.0
        f_expr = "3*x^2 - 1"
        normal = cas_normal(f_expr, c, "x")
        f_val = cas_eval(f_expr, x=c)
        n_val = cas_eval(normal, x=c)
        self.assertAlmostEqual(float(f_val), float(n_val), places=4)

    def test_tangent_at_negative_x(self):
        """F10 Tier 2: Boundary - Tangent line at negative x coordinate."""
        line = cas_tangent("x^2", -2, "x")
        # slope = -4, passes through (-2, 4) -> y - 4 = -4(x + 2) -> y = -4x - 4
        self.assertAlmostEqual(float(cas_eval(line, x=-2.0)), 4.0, places=4)
        self.assertAlmostEqual(float(cas_eval(line, x=0.0)), -4.0, places=4)

    def test_tangent_linear_function(self):
        """F10 Tier 2: Boundary - Tangent to linear function y = 3*x + 5 is identical line."""
        line = cas_tangent("3*x + 5", 4, "x")
        self.assertTrue(expr_numerically_equal(line, "3*x + 5", var="x"))

    def test_tangent_normal_perpendicularity(self):
        """F10 Tier 2: Boundary - Slope product of tangent and normal is -1."""
        f_expr = "x^2 + x"
        c = 2.0
        t_line = cas_tangent(f_expr, c, "x")
        n_line = cas_normal(f_expr, c, "x")
        # Approximate slopes from lines
        m_t = float(cas_eval(t_line, x=1.0)) - float(cas_eval(t_line, x=0.0))
        m_n = float(cas_eval(n_line, x=1.0)) - float(cas_eval(n_line, x=0.0))
        self.assertAlmostEqual(m_t * m_n, -1.0, places=3)


if __name__ == "__main__":
    unittest.main()
