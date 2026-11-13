"""Tests for FlowCE CAS:
- Tier 3: Cross-Feature Pairwise Combinations (Min 15)
- Tier 4: Real-World AP Calculus & Physics Application Scenarios (Min 6: S1 to S6)
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
    cas_simplify,
    cas_limit,
    cas_series,
    cas_tangent,
    cas_normal,
    cas_eval,
    expr_numerically_equal,
)


class TestCrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Pairwise Cross-Feature Interactions (>= 15 tests)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    def test_pairwise_diff_and_integrate(self):
        """Tier 3: Differentiating an indefinite integral returns original integrand."""
        f_expr = "x^3 + 2*x^2 - 5"
        F_expr = cas_integrate(f_expr, "x")
        dF = cas_diff(F_expr, "x")
        self.assertTrue(expr_numerically_equal(dF, f_expr, var="x"))

    def test_pairwise_integrate_and_diff(self):
        """Tier 3: Integrating the derivative of a polynomial."""
        f_expr = "x^4 - 3*x"
        df = cas_diff(f_expr, "x")
        F = cas_integrate(df, "x")
        self.assertTrue(expr_numerically_equal(F, f_expr, var="x"))

    def test_pairwise_diff_and_simplify(self):
        """Tier 3: Simplifying a product-rule derivative result."""
        # d/dx(x^2 * x^3) = d/dx(x^5) = 5*x^4
        d = cas_diff("x^2 * x^3", "x")
        s = cas_simplify(d)
        self.assertTrue(expr_numerically_equal(s, "5*x^4", var="x"))

    def test_pairwise_integrate_and_simplify(self):
        """Tier 3: Simplifying an integral result with redundant terms."""
        # int(2*x + 3*x) -> int(5*x) -> 2.5*x^2
        F = cas_integrate("2*x + 3*x", "x")
        s = cas_simplify(F)
        self.assertTrue(expr_numerically_equal(s, "2.5*x^2", var="x"))

    def test_pairwise_tangent_on_rational(self):
        """Tier 3: Tangent line to 1/x at x=1 has slope -1 and equation y = -x + 2."""
        t_line = cas_tangent("1/x", 1, "x")
        self.assertTrue(expr_numerically_equal(t_line, "-x + 2", var="x", points=[0.5, 1.0, 2.0]))

    def test_pairwise_tangent_on_exponential(self):
        """Tier 3: Tangent line to exp(x) at x=0 is y = x + 1."""
        t_line = cas_tangent("exp(x)", 0, "x")
        self.assertTrue(expr_numerically_equal(t_line, "x + 1", var="x", points=[0.0, 1.0, 2.0]))

    def test_pairwise_normal_on_trig(self):
        """Tier 3: Normal line to sin(x) at x=0 has slope -1, y = -x."""
        n_line = cas_normal("sin(x)", 0, "x")
        self.assertTrue(expr_numerically_equal(n_line, "-x", var="x", points=[0.0, 1.0, 2.0]))

    def test_pairwise_diff_taylor_series(self):
        """Tier 3: Derivative of sin(x) Taylor series matches cos(x) Taylor series."""
        # sin series: x - x^3/6 -> derivative: 1 - x^2/2
        s_sin = cas_series("sin(x)", "x", 0, order=4)
        ds = cas_diff(s_sin, "x")
        s_cos = cas_series("cos(x)", "x", 0, order=3)
        self.assertTrue(expr_numerically_equal(ds, s_cos, var="x", points=[0.1, 0.2, 0.3]))

    def test_pairwise_integrate_taylor_series(self):
        """Tier 3: Definite integral of Taylor series approximates definite integral of function."""
        # int_0^1 exp(x) dx = e - 1 ~ 1.71828
        s_exp = cas_series("exp(x)", "x", 0, order=5)
        approx_val = cas_integrate(s_exp, "x", 0, 1)
        true_val = math.e - 1.0
        self.assertAlmostEqual(float(approx_val), true_val, delta=0.01)

    def test_pairwise_limit_of_derivative(self):
        """Tier 3: lim_{x->2} d/dx(x^3) = lim_{x->2} 3*x^2 = 12."""
        d = cas_diff("x^3", "x")
        lim_val = cas_limit(d, "x", 2)
        self.assertAlmostEqual(float(lim_val), 12.0, places=4)

    def test_pairwise_riemann_and_definite_integral(self):
        """Tier 3: Riemann sum converges to definite integral as partition count increases."""
        exact = cas_integrate("x^3", "x", 0, 2)
        riemann = cas_riemann("x^3", "x", 0, 2, n=50, method="midpoint")
        self.assertAlmostEqual(float(exact), 4.0, places=4)
        self.assertAlmostEqual(float(riemann), 4.0, delta=0.05)

    def test_pairwise_second_derivative_concavity(self):
        """Tier 3: Second derivative f''(x) determines local extrema concavity."""
        f_expr = "x^3 - 3*x"
        f_prime = cas_diff(f_expr, "x")  # 3*x^2 - 3 -> 0 at x=1
        f_double_prime = cas_diff(f_prime, "x")  # 6*x -> 6 > 0 at x=1 (local min)
        concavity_at_1 = cas_eval(f_double_prime, x=1.0)
        concavity_at_neg1 = cas_eval(f_double_prime, x=-1.0)
        self.assertGreater(float(concavity_at_1), 0.0)
        self.assertLess(float(concavity_at_neg1), 0.0)

    def test_pairwise_limit_difference_quotient(self):
        """Tier 3: Definition of derivative via difference quotient limit."""
        # For f(x) = x^2, (f(2+h) - f(2))/h = ((2+h)^2 - 4)/h = (4+4h+h^2-4)/h = 4 + h -> 4
        diff_quotient = "((2 + h)^2 - 4) / h"
        lim = cas_limit(diff_quotient, "h", 0)
        self.assertAlmostEqual(float(lim), 4.0, places=3)

    def test_pairwise_tangent_line_derivative_equivalence(self):
        """Tier 3: Slope of tangent line at x=c equals d/dx at x=c."""
        f_expr = "x^3 - 2*x"
        c = 3.0
        df = cas_diff(f_expr, "x")
        slope_from_diff = float(cas_eval(df, x=c))
        t_line = cas_tangent(f_expr, c, "x")
        slope_from_tangent = float(cas_eval(t_line, x=c + 1.0)) - float(cas_eval(t_line, x=c))
        self.assertAlmostEqual(slope_from_diff, slope_from_tangent, places=3)

    def test_pairwise_area_integral_with_simplification(self):
        """Tier 3: Area between two functions with integrated simplified difference."""
        f1 = "x^2"
        f2 = "2*x"
        # Area from 0 to 2: int_0^2 (2*x - x^2) dx = [x^2 - x^3/3]_0^2 = 4 - 8/3 = 4/3 ~ 1.333
        diff_expr = cas_simplify("2*x - x^2")
        area = cas_integrate(diff_expr, "x", 0, 2)
        self.assertAlmostEqual(float(area), 4.0 / 3.0, places=3)


class TestRealWorldAPCalculusScenarios(unittest.TestCase):
    """Tier 4: Comprehensive AP Calculus & Physics Application Scenarios (S1 to S6)."""

    def setUp(self):
        if get_flowce() is None:
            self.skipTest("flowce.py not yet implemented by cas_author")

    def test_s1_kinematics_physics_pipeline(self):
        """S1: Kinematics Physics Pipeline.
        Position s(t) = -16*t^2 + 64*t + 80
        Velocity v(t) = s'(t) = -32*t + 64
        Acceleration a(t) = v'(t) = -32
        Max height when v(t) = 0 -> t = 2
        Total displacement from t=0 to t=2: int_0^2 v(t) dt = s(2) - s(0) = 144 - 80 = 64
        """
        s_expr = "-16*t^2 + 64*t + 80"
        v_expr = cas_diff(s_expr, "t")
        a_expr = cas_diff(v_expr, "t")

        self.assertTrue(expr_numerically_equal(v_expr, "-32*t + 64", var="t"))
        self.assertTrue(expr_numerically_equal(a_expr, "-32", var="t"))

        # Velocity is zero at t = 2
        self.assertAlmostEqual(float(cas_eval(v_expr, t=2.0)), 0.0, places=4)

        # Definite integral of velocity over [0, 2]
        displacement = cas_integrate(v_expr, "t", 0, 2)
        self.assertAlmostEqual(float(displacement), 64.0, places=3)

    def test_s2_tangent_and_normal_line_to_curve(self):
        """S2: Tangent & Normal Line to Curve at Point.
        f(x) = x^3 - 4*x at x = 2:
        f(2) = 0
        f'(x) = 3*x^2 - 4 -> f'(2) = 8
        Tangent line: y = 8*(x - 2) = 8*x - 16
        Normal line: y = (-1/8)*(x - 2) = -0.125*x + 0.25
        """
        f_expr = "x^3 - 4*x"
        tangent = cas_tangent(f_expr, 2, "x")
        normal = cas_normal(f_expr, 2, "x")

        # Check values on tangent line
        self.assertAlmostEqual(float(cas_eval(tangent, x=2.0)), 0.0, places=4)
        self.assertAlmostEqual(float(cas_eval(tangent, x=3.0)), 8.0, places=4)

        # Check values on normal line
        self.assertAlmostEqual(float(cas_eval(normal, x=2.0)), 0.0, places=4)
        self.assertAlmostEqual(float(cas_eval(normal, x=10.0)), -1.0, places=4)

    def test_s3_area_between_curves(self):
        """S3: Area Between Two Curves.
        y1 = 2*x, y2 = x^2
        Intersections at x=0 and x=2.
        Area = int_0^2 (2*x - x^2) dx = [x^2 - x^3/3]_0^2 = 4 - 8/3 = 4/3.
        """
        area = cas_integrate("2*x - x^2", "x", 0, 2)
        self.assertAlmostEqual(float(area), 4.0 / 3.0, places=3)

    def test_s4_taylor_polynomial_approximation(self):
        """S4: Taylor Polynomial Approximation of sin(x) at x=0.
        P3(x) = x - x^3/6
        Compare sin(0.5) ~ 0.4794255 to P3(0.5) = 0.5 - 0.125/6 = 0.4791666 (error < 0.001).
        """
        p_series = cas_series("sin(x)", "x", 0, order=4)
        approx = float(cas_eval(p_series, x=0.5))
        exact = math.sin(0.5)
        self.assertAlmostEqual(approx, exact, delta=0.001)

    def test_s5_indeterminate_limits_lhopital(self):
        """S5: Indeterminate Limits via L'Hopital's Rule.
        lim_{x->0} (sin(2*x) / x) = 2
        lim_{x->0} ((1 - cos(x)) / x^2) = 1/2 = 0.5
        """
        lim1 = cas_limit("sin(2*x) / x", "x", 0)
        self.assertAlmostEqual(float(lim1), 2.0, places=3)

        lim2 = cas_limit("(1 - cos(x)) / (x^2)", "x", 0)
        self.assertAlmostEqual(float(lim2), 0.5, places=3)

    def test_s6_optimization_critical_points(self):
        """S6: Optimization Problem (Critical Points and Extrema).
        Volume of open box: V(x) = x * (12 - 2*x)^2 = 4*x^3 - 48*x^2 + 144*x
        V'(x) = 12*x^2 - 96*x + 144 = 12*(x - 2)*(x - 6)
        Critical points at x = 2 and x = 6.
        V''(x) = 24*x - 96.
        At x = 2: V''(2) = -48 < 0 -> Local Maximum!
        At x = 6: V''(6) = +48 > 0 -> Local Minimum!
        Max volume at x = 2 is V(2) = 2 * (8)^2 = 128.
        """
        v_expr = "4*x^3 - 48*x^2 + 144*x"
        v_prime = cas_diff(v_expr, "x")
        v_double_prime = cas_diff(v_prime, "x")

        # Test critical point x = 2
        slope_at_2 = float(cas_eval(v_prime, x=2.0))
        self.assertAlmostEqual(slope_at_2, 0.0, places=4)

        # Test concavity at x = 2
        concavity_at_2 = float(cas_eval(v_double_prime, x=2.0))
        self.assertLess(concavity_at_2, 0.0)

        # Maximum volume calculation
        max_vol = float(cas_eval(v_expr, x=2.0))
        self.assertAlmostEqual(max_vol, 128.0, places=4)


if __name__ == "__main__":
    unittest.main()
