"""Tests for FlowCE CAS:
- F8: Symbolic & Definite Integration and Riemann Sum Approximation
"""

import math
import os
import sys
import unittest

from tests.test_helpers import (
    get_flowce,
    cas_diff,
    cas_integrate,
    cas_riemann,
    cas_eval,
    expr_numerically_equal,
)


class TestSymbolicDefiniteIntegration(unittest.TestCase):
    """F8: Symbolic & Definite Integration tests (Tier 1 & Tier 2)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    # Tier 1: Feature Coverage (Min 5)
    def test_power_rule_integration(self):
        """F8 Tier 1: int(x^2 dx) = (1/3)*x^3 and int(x^4 dx) = (1/5)*x^5."""
        res = cas_integrate("x^2", "x")
        self.assertTrue(expr_numerically_equal(cas_diff(res, "x"), "x^2", var="x"))

        res2 = cas_integrate("x^4", "x")
        self.assertTrue(expr_numerically_equal(cas_diff(res2, "x"), "x^4", var="x"))

    def test_polynomial_integration(self):
        """F8 Tier 1: int(3*x^2 + 2*x + 1 dx) = x^3 + x^2 + x."""
        res = cas_integrate("3*x^2 + 2*x + 1", "x")
        self.assertTrue(expr_numerically_equal(cas_diff(res, "x"), "3*x^2 + 2*x + 1", var="x"))

    def test_trigonometric_integration(self):
        """F8 Tier 1: int(cos(x) dx) = sin(x) and int(sin(x) dx) = -cos(x)."""
        res_cos = cas_integrate("cos(x)", "x")
        self.assertTrue(expr_numerically_equal(cas_diff(res_cos, "x"), "cos(x)", var="x"))

        res_sin = cas_integrate("sin(x)", "x")
        self.assertTrue(expr_numerically_equal(cas_diff(res_sin, "x"), "sin(x)", var="x"))

    def test_exponential_integration(self):
        """F8 Tier 1: int(exp(x) dx) = exp(x)."""
        res = cas_integrate("exp(x)", "x")
        self.assertTrue(expr_numerically_equal(cas_diff(res, "x"), "exp(x)", var="x"))

    def test_definite_integral_polynomial(self):
        """F8 Tier 1: int_0^2 (3*x^2 dx) = [x^3]_0^2 = 8."""
        val = cas_integrate("3*x^2", "x", 0, 2)
        self.assertAlmostEqual(float(val), 8.0, places=4)

    def test_definite_integral_trig(self):
        """F8 Tier 1: int_0^pi (sin(x) dx) = [-cos(x)]_0^pi = 2."""
        val = cas_integrate("sin(x)", "x", 0, math.pi)
        self.assertAlmostEqual(float(val), 2.0, places=3)

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_constant_integration(self):
        """F8 Tier 2: Boundary - int(7 dx) = 7*x."""
        res = cas_integrate("7", "x")
        self.assertTrue(expr_numerically_equal(cas_diff(res, "x"), "7", var="x"))

    def test_definite_integral_same_limits(self):
        """F8 Tier 2: Boundary - int_a^a f(x) dx = 0."""
        val = cas_integrate("x^3 + sin(x)", "x", 4.5, 4.5)
        self.assertAlmostEqual(float(val), 0.0, places=5)

    def test_logarithmic_integration(self):
        """F8 Tier 2: Boundary - int(1/x dx) = ln(x)."""
        res = cas_integrate("1/x", "x")
        self.assertTrue(expr_numerically_equal(cas_diff(res, "x"), "1/x", var="x", points=[1.5, 2.5, 3.5]))

    def test_riemann_sum_approximation(self):
        """F8 Tier 2: Boundary - Riemann sum of x^2 from 0 to 1 with n=100 converges near 1/3."""
        approx = cas_riemann("x^2", "x", 0, 1, n=100, method="midpoint")
        self.assertAlmostEqual(float(approx), 1.0 / 3.0, delta=0.01)

    def test_fundamental_theorem_of_calculus(self):
        """F8 Tier 2: Boundary - d/dx(int(f(x) dx)) == f(x) for x^3 - 5*x."""
        f_expr = "x^3 - 5*x"
        F_expr = cas_integrate(f_expr, "x")
        derivative = cas_diff(F_expr, "x")
        self.assertTrue(expr_numerically_equal(derivative, f_expr, var="x"))

    def test_definite_integral_reversed_limits(self):
        """F8 Tier 2: Boundary - int_b^a f(x) dx = -int_a^b f(x) dx."""
        v1 = cas_integrate("x^2", "x", 1, 3)
        v2 = cas_integrate("x^2", "x", 3, 1)
        self.assertAlmostEqual(float(v1), -float(v2), places=4)


if __name__ == "__main__":
    unittest.main()
