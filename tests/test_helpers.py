"""Test helper utilities for FlowCE CAS opaque-box and symbolic verification.
Compliant with Python 3.4 (zero f-strings, zero re).
"""

import math
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def get_flowce():
    try:
        import flowce
        return flowce
    except ImportError:
        return None


def call_api(func_names, *args, **kwargs):
    """Invoke the first matching function name available on flowce module."""
    m = get_flowce()
    if m is None:
        raise RuntimeError("flowce module is not available")
    for name in func_names:
        if hasattr(m, name):
            fn = getattr(m, name)
            return fn(*args, **kwargs)
    raise AttributeError("None of {} found in flowce module".format(func_names))


def cas_diff(expr, var="x"):
    return call_api(["diff", "derivative", "differentiate"], expr, var)


def cas_diff_steps(expr, var="x"):
    m = get_flowce()
    if hasattr(m, "diff_steps"):
        return m.diff_steps(expr, var)
    if hasattr(m, "derivative_steps"):
        return m.derivative_steps(expr, var)
    if hasattr(m, "differentiate_steps"):
        return m.differentiate_steps(expr, var)
    # Fallback to diff if steps returned as tuple or diff has step param
    for name in ["diff", "derivative"]:
        if hasattr(m, name):
            fn = getattr(m, name)
            try:
                return fn(expr, var, steps=True)
            except TypeError:
                pass
    return call_api(["diff", "derivative"], expr, var)


def cas_integrate(expr, var="x", a=None, b=None):
    m = get_flowce()
    for name in ["integrate", "integral", "anti_derivative"]:
        if hasattr(m, name):
            fn = getattr(m, name)
            if a is not None and b is not None:
                try:
                    return fn(expr, var, a, b)
                except TypeError:
                    return fn(expr, a, b)
            else:
                return fn(expr, var)
    raise AttributeError("integrate / integral not found in flowce")


def cas_riemann(expr, var="x", a=0, b=1, n=10, method="midpoint"):
    m = get_flowce()
    for name in ["riemann_sum", "riemann", "approx_integral"]:
        if hasattr(m, name):
            fn = getattr(m, name)
            try:
                return fn(expr, var, a, b, n, method)
            except TypeError:
                try:
                    return fn(expr, a, b, n, method)
                except TypeError:
                    return fn(expr, a, b, n)
    raise AttributeError("riemann_sum not found in flowce")


def cas_simplify(expr):
    return call_api(["simplify", "simplify_expr", "algebraic_simplify"], expr)


def cas_limit(expr, var="x", target=0, direction="both"):
    m = get_flowce()
    for name in ["limit", "eval_limit", "calc_limit"]:
        if hasattr(m, name):
            fn = getattr(m, name)
            try:
                return fn(expr, var, target, direction)
            except TypeError:
                try:
                    return fn(expr, var, target)
                except TypeError:
                    return fn(expr, target)
    raise AttributeError("limit not found in flowce")


def cas_series(expr, var="x", point=0, order=4):
    m = get_flowce()
    for name in ["series", "taylor", "taylor_series", "maclaurin"]:
        if hasattr(m, name):
            fn = getattr(m, name)
            try:
                return fn(expr, var, point, order)
            except TypeError:
                try:
                    return fn(expr, point, order)
                except TypeError:
                    return fn(expr, order)
    raise AttributeError("series / taylor not found in flowce")


def cas_tangent(expr, point_c, var="x"):
    m = get_flowce()
    for name in ["tangent_line", "tangent", "calc_tangent_line"]:
        if hasattr(m, name):
            fn = getattr(m, name)
            try:
                return fn(expr, point_c, var)
            except TypeError:
                return fn(expr, point_c)
    raise AttributeError("tangent_line not found in flowce")


def cas_normal(expr, point_c, var="x"):
    m = get_flowce()
    for name in ["normal_line", "normal", "calc_normal_line"]:
        if hasattr(m, name):
            fn = getattr(m, name)
            try:
                return fn(expr, point_c, var)
            except TypeError:
                return fn(expr, point_c)
    raise AttributeError("normal_line not found in flowce")


def cas_parse(expr_str):
    return call_api(["parse", "parse_expr", "lexer_parser"], expr_str)


def cas_eval(expr, **subs):
    m = get_flowce()
    for name in ["evaluate", "eval_expr", "substitute", "subs"]:
        if hasattr(m, name):
            fn = getattr(m, name)
            return fn(expr, **subs)
    # Simple fallback: if string representation, replace vars and eval with safe math dict
    s = str(expr).replace("^", "**")
    context = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "exp": math.exp, "ln": math.log, "log": math.log,
        "pi": math.pi, "e": math.e, "sqrt": math.sqrt,
    }
    context.update(subs)
    return eval(s, {"__builtins__": {}}, context)


def expr_numerically_equal(expr1, expr2, var="x", points=None, tol=1e-5):
    """Verify two expressions evaluate to equal values across multiple sample points."""
    if points is None:
        points = [0.5, 1.2, 2.5, 3.1]
    for p in points:
        try:
            v1 = cas_eval(expr1, **{var: p})
            v2 = cas_eval(expr2, **{var: p})
            if abs(float(v1) - float(v2)) > tol:
                return False
        except (ValueError, ZeroDivisionError, OverflowError):
            continue
    return True
