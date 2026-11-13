"""FlowCE Computer Algebra System (CAS) for Texas Instruments TI-84 Plus CE / Evo Python.
MicroPython / CircuitPython (Python 3.4 baseline) compliant:
- Zero f-strings
- Zero regular expressions (no 're' module)
- Zero external dependencies (pure Python standard library)
- Hardware mock integration (ti_system, ti_draw, ti_plotlib, ti_hub) with headless fallback
"""

import math
import sys

# Hardware mocks detection
try:
    import ti_system
    import ti_draw
    import ti_plotlib
    import ti_hub
    HAS_TI = True
except ImportError:
    HAS_TI = False


# ---------------------------------------------------------------------------
# Exact Rational Number Arithmetic
# ---------------------------------------------------------------------------

def gcd(a, b):
    """Compute greatest common divisor of two integers using Euclidean algorithm."""
    a = abs(int(a))
    b = abs(int(b))
    while b != 0:
        a, b = b, a % b
    return a


class Expr(object):
    """Base class for all symbolic expressions in FlowCE CAS."""

    def __add__(self, other):
        return Add(self, to_expr(other))

    def __radd__(self, other):
        return Add(to_expr(other), self)

    def __sub__(self, other):
        return Sub(self, to_expr(other))

    def __rsub__(self, other):
        return Sub(to_expr(other), self)

    def __mul__(self, other):
        return Mul(self, to_expr(other))

    def __rmul__(self, other):
        return Mul(to_expr(other), self)

    def __truediv__(self, other):
        return Div(self, to_expr(other))

    def __rtruediv__(self, other):
        return Div(to_expr(other), self)

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __pow__(self, other):
        return Pow(self, to_expr(other))

    def __rpow__(self, other):
        return Pow(to_expr(other), self)

    def __neg__(self):
        return Mul(Rational(-1, 1), self)

    def __pos__(self):
        return self

    def __abs__(self):
        return Abs(self)

    def diff(self, var="x"):
        return diff(self, var)

    def diff_steps(self, var="x"):
        return diff_steps(self, var)

    def integrate(self, var="x", a=None, b=None):
        return integrate(self, var, a, b)

    def simplify(self):
        return simplify(self)

    def expand(self):
        return expand(self)

    def subs(self, var, val=None):
        if val is None and isinstance(var, dict):
            res = self
            for k, v in var.items():
                res = res.subs(k, v)
            return res
        return self._subs_single(str(var), to_expr(val))

    def _subs_single(self, var_name, val_expr):
        return self

    def evalf(self, subs_dict=None):
        raise NotImplementedError("evalf must be implemented by subclasses")

    def free_symbols(self):
        return set()

    def is_number(self):
        return len(self.free_symbols()) == 0

    @property
    def is_zero(self):
        return False

    @property
    def is_one(self):
        return False


class Rational(Expr):
    """Exact rational number representation (num / den)."""

    def __init__(self, num, den=1):
        if isinstance(num, str) and den == 1:
            s = num.strip()
            if "/" in s:
                parts = s.split("/")
                n = int(parts[0].strip())
                d = int(parts[1].strip())
            elif "." in s:
                parts = s.split(".")
                sign = -1 if parts[0].startswith("-") else 1
                int_part = abs(int(parts[0])) if parts[0] and parts[0] != "-" else 0
                frac_str = parts[1].strip()
                power = 10 ** len(frac_str)
                n = sign * (int_part * power + int(frac_str))
                d = power
            else:
                n = int(s)
                d = 1
        elif isinstance(num, Rational):
            n = num.num
            d = num.den
            if isinstance(den, Rational):
                n *= den.den
                d *= den.num
            else:
                d *= int(den)
        elif isinstance(num, float) and den == 1:
            n, d = num.as_integer_ratio()
        else:
            n = int(num)
            if isinstance(den, Rational):
                n *= den.den
                d = den.num
            else:
                d = int(den)

        if d == 0:
            raise ZeroDivisionError("Rational denominator cannot be zero")

        if d < 0:
            n = -n
            d = -d

        g = gcd(n, d)
        self.num = n // g
        self.den = d // g

    @property
    def is_zero(self):
        return self.num == 0

    @property
    def is_one(self):
        return self.num == 1 and self.den == 1

    @property
    def is_integer(self):
        return self.den == 1

    @property
    def is_negative(self):
        return self.num < 0

    def __add__(self, other):
        if isinstance(other, Rational):
            return Rational(self.num * other.den + other.num * self.den, self.den * other.den)
        if isinstance(other, int):
            return Rational(self.num + other * self.den, self.den)
        if isinstance(other, float):
            return float(self) + other
        if isinstance(other, Expr):
            return Add(self, other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Rational):
            return Rational(self.num * other.den - other.num * self.den, self.den * other.den)
        if isinstance(other, int):
            return Rational(self.num - other * self.den, self.den)
        if isinstance(other, float):
            return float(self) - other
        if isinstance(other, Expr):
            return Sub(self, other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return to_expr(other) - self
        if isinstance(other, Expr):
            return Sub(other, self)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Rational):
            return Rational(self.num * other.num, self.den * other.den)
        if isinstance(other, int):
            return Rational(self.num * other, self.den)
        if isinstance(other, float):
            return float(self) * other
        if isinstance(other, Expr):
            return Mul(self, other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Rational):
            if other.num == 0:
                raise ZeroDivisionError("Rational division by zero")
            return Rational(self.num * other.den, self.den * other.num)
        if isinstance(other, int):
            if other == 0:
                raise ZeroDivisionError("Rational division by zero")
            return Rational(self.num, self.den * other)
        if isinstance(other, float):
            if other == 0.0:
                raise ZeroDivisionError("Rational division by zero")
            return float(self) / other
        if isinstance(other, Expr):
            return Div(self, other)
        return NotImplemented

    def __rtruediv__(self, other):
        if self.num == 0:
            raise ZeroDivisionError("Rational division by zero")
        if isinstance(other, (int, float)):
            return to_expr(other) / self
        if isinstance(other, Expr):
            return Div(other, self)
        return NotImplemented

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __pow__(self, other):
        if isinstance(other, int):
            if other >= 0:
                return Rational(self.num ** other, self.den ** other)
            else:
                p = -other
                if self.num == 0:
                    raise ZeroDivisionError("0 cannot be raised to negative power")
                return Rational(self.den ** p, self.num ** p)
        if isinstance(other, Rational):
            if other.den == 1:
                return self.__pow__(other.num)
            # fractional power
            val = float(self) ** float(other)
            return float_to_rational(val)
        if isinstance(other, float):
            return float(self) ** other
        if isinstance(other, Expr):
            return Pow(self, other)
        return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, (int, float)):
            return to_expr(other) ** self
        if isinstance(other, Expr):
            return Pow(other, self)
        return NotImplemented

    def __neg__(self):
        return Rational(-self.num, self.den)

    def __pos__(self):
        return self

    def __abs__(self):
        return Rational(abs(self.num), self.den)

    def __int__(self):
        return int(self.num // self.den)

    def __float__(self):
        return float(self.num) / float(self.den)

    def __eq__(self, other):
        if isinstance(other, Rational):
            return self.num == other.num and self.den == other.den
        if isinstance(other, int):
            return self.den == 1 and self.num == other
        if isinstance(other, float):
            return float(self) == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, Rational):
            return self.num * other.den < other.num * self.den
        return float(self) < float(other)

    def __le__(self, other):
        if isinstance(other, Rational):
            return self.num * other.den <= other.num * self.den
        return float(self) <= float(other)

    def __gt__(self, other):
        if isinstance(other, Rational):
            return self.num * other.den > other.num * self.den
        return float(self) > float(other)

    def __ge__(self, other):
        if isinstance(other, Rational):
            return self.num * other.den >= other.num * self.den
        return float(self) >= float(other)

    def __hash__(self):
        return hash(("Rational", self.num, self.den))

    def __str__(self):
        if self.den == 1:
            return "%d" % self.num
        return "%d/%d" % (self.num, self.den)

    def __repr__(self):
        return "Rational(%d, %d)" % (self.num, self.den)

    def evalf(self, subs_dict=None):
        return float(self.num) / float(self.den)

    def _subs_single(self, var_name, val_expr):
        return self


Number = Rational
Integer = Rational


def float_to_rational(val, max_den=10000, tol=1e-7):
    """Convert float value to nearest exact Rational."""
    if math.isnan(val) or math.isinf(val):
        return val
    # Check if close to integer
    r = round(val)
    if abs(val - r) < tol:
        return Rational(int(r), 1)
    # Search common small denominators
    sign = -1 if val < 0 else 1
    v = abs(val)
    best_num = round(v)
    best_den = 1
    best_err = abs(v - best_num)
    for d in range(1, max_den + 1):
        n = round(v * d)
        err = abs(v - float(n) / float(d))
        if err < tol:
            return Rational(sign * int(n), d)
        if err < best_err:
            best_err = err
            best_num = n
            best_den = d
    return Rational(sign * int(best_num), best_den)


def to_expr(obj):
    """Coerce a Python object to an Expr."""
    if isinstance(obj, Expr):
        return obj
    if isinstance(obj, int):
        return Rational(obj, 1)
    if isinstance(obj, float):
        if obj.is_integer():
            return Rational(int(obj), 1)
        return float_to_rational(obj)
    if isinstance(obj, str):
        return parse(obj)
    return obj


# ---------------------------------------------------------------------------
# Symbolic AST Nodes
# ---------------------------------------------------------------------------

class Symbol(Expr):
    """Symbolic variable representing mathematical indeterminate (e.g. x, y, t)."""

    def __init__(self, name):
        self.name = str(name).strip()

    def free_symbols(self):
        return {self.name}

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Symbol('%s')" % self.name

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(("Symbol", self.name))

    def _subs_single(self, var_name, val_expr):
        if self.name == var_name:
            return val_expr
        return self

    def evalf(self, subs_dict=None):
        if subs_dict and self.name in subs_dict:
            v = subs_dict[self.name]
            if isinstance(v, Expr):
                return v.evalf(subs_dict)
            return float(v)
        raise ValueError("No substitution value provided for symbol '%s'" % self.name)


def symbols(names_str):
    """Create one or more symbols from whitespace/comma delimited string."""
    cleaned = names_str.replace(",", " ")
    parts = [p.strip() for p in cleaned.split() if p.strip()]
    syms = [Symbol(p) for p in parts]
    if len(syms) == 1:
        return syms[0]
    return tuple(syms)


# Standard predefined symbols
x = Symbol("x")
y = Symbol("y")
t = Symbol("t")
z = Symbol("z")
h = Symbol("h")


class Add(Expr):
    """Addition of terms."""

    def __init__(self, *args):
        flat_args = []
        for a in args:
            node = to_expr(a)
            if isinstance(node, Add):
                flat_args.extend(node.args)
            else:
                flat_args.append(node)
        self.args = tuple(flat_args)

    def free_symbols(self):
        res = set()
        for a in self.args:
            res |= a.free_symbols()
        return res

    def _subs_single(self, var_name, val_expr):
        return Add(*[a._subs_single(var_name, val_expr) for a in self.args])

    def evalf(self, subs_dict=None):
        return sum(a.evalf(subs_dict) for a in self.args)

    def __str__(self):
        if not self.args:
            return "0"
        parts = []
        for i, a in enumerate(self.args):
            s = str(a)
            if i > 0 and not s.startswith("-"):
                parts.append("+")
                parts.append(s)
            elif i > 0 and s.startswith("-"):
                parts.append("-")
                parts.append(s[1:].strip())
            else:
                parts.append(s)
        return " ".join(parts)

    def __repr__(self):
        return "Add(%s)" % ", ".join(repr(a) for a in self.args)

    def __eq__(self, other):
        if isinstance(other, Add):
            return self.args == other.args
        return False

    def __hash__(self):
        return hash(("Add", self.args))


class Sub(Expr):
    """Subtraction of two terms."""

    def __init__(self, left, right):
        self.left = to_expr(left)
        self.right = to_expr(right)
        self.args = (self.left, self.right)

    def free_symbols(self):
        return self.left.free_symbols() | self.right.free_symbols()

    def _subs_single(self, var_name, val_expr):
        return Sub(self.left._subs_single(var_name, val_expr), self.right._subs_single(var_name, val_expr))

    def evalf(self, subs_dict=None):
        return self.left.evalf(subs_dict) - self.right.evalf(subs_dict)

    def __str__(self):
        s_left = str(self.left)
        s_right = str(self.right)
        if isinstance(self.right, (Add, Sub)):
            s_right = "(%s)" % s_right
        return "%s - %s" % (s_left, s_right)

    def __repr__(self):
        return "Sub(%s, %s)" % (repr(self.left), repr(self.right))

    def __eq__(self, other):
        if isinstance(other, Sub):
            return self.left == other.left and self.right == other.right
        return False

    def __hash__(self):
        return hash(("Sub", self.left, self.right))


class Mul(Expr):
    """Multiplication of factors."""

    def __init__(self, *args):
        flat_args = []
        for a in args:
            node = to_expr(a)
            if isinstance(node, Mul):
                flat_args.extend(node.args)
            else:
                flat_args.append(node)
        self.args = tuple(flat_args)

    def free_symbols(self):
        res = set()
        for a in self.args:
            res |= a.free_symbols()
        return res

    def _subs_single(self, var_name, val_expr):
        return Mul(*[a._subs_single(var_name, val_expr) for a in self.args])

    def evalf(self, subs_dict=None):
        val = 1.0
        for a in self.args:
            val *= a.evalf(subs_dict)
        return val

    def __str__(self):
        if not self.args:
            return "1"
        # Special case: -1 * something
        if len(self.args) == 2 and self.args[0] == Rational(-1, 1):
            s = str(self.args[1])
            if isinstance(self.args[1], (Add, Sub)):
                return "-(%s)" % s
            return "-%s" % s
        parts = []
        for a in self.args:
            s = str(a)
            if isinstance(a, (Add, Sub)):
                parts.append("(%s)" % s)
            else:
                parts.append(s)
        return "*".join(parts)

    def __repr__(self):
        return "Mul(%s)" % ", ".join(repr(a) for a in self.args)

    def __eq__(self, other):
        if isinstance(other, Mul):
            return self.args == other.args
        return False

    def __hash__(self):
        return hash(("Mul", self.args))


class Div(Expr):
    """Division of numerator by denominator."""

    def __init__(self, num, den):
        self.num = to_expr(num)
        self.den = to_expr(den)
        self.args = (self.num, self.den)

    def free_symbols(self):
        return self.num.free_symbols() | self.den.free_symbols()

    def _subs_single(self, var_name, val_expr):
        return Div(self.num._subs_single(var_name, val_expr), self.den._subs_single(var_name, val_expr))

    def evalf(self, subs_dict=None):
        d = self.den.evalf(subs_dict)
        if d == 0:
            raise ZeroDivisionError("Division by zero in evalf")
        return self.num.evalf(subs_dict) / d

    def __str__(self):
        s_num = str(self.num)
        s_den = str(self.den)
        if isinstance(self.num, (Add, Sub)):
            s_num = "(%s)" % s_num
        if isinstance(self.den, (Add, Sub, Mul, Div, Pow)):
            s_den = "(%s)" % s_den
        return "%s / %s" % (s_num, s_den)

    def __repr__(self):
        return "Div(%s, %s)" % (repr(self.num), repr(self.den))

    def __eq__(self, other):
        if isinstance(other, Div):
            return self.num == other.num and self.den == other.den
        return False

    def __hash__(self):
        return hash(("Div", self.num, self.den))


class Pow(Expr):
    """Base raised to exponent power."""

    def __init__(self, base, exp):
        self.base = to_expr(base)
        self.exp = to_expr(exp)
        self.args = (self.base, self.exp)

    def free_symbols(self):
        return self.base.free_symbols() | self.exp.free_symbols()

    def _subs_single(self, var_name, val_expr):
        return Pow(self.base._subs_single(var_name, val_expr), self.exp._subs_single(var_name, val_expr))

    def evalf(self, subs_dict=None):
        b = self.base.evalf(subs_dict)
        e = self.exp.evalf(subs_dict)
        return b ** e

    def __str__(self):
        s_base = str(self.base)
        s_exp = str(self.exp)
        if isinstance(self.base, (Add, Sub, Mul, Div, Pow)):
            s_base = "(%s)" % s_base
        if isinstance(self.exp, (Add, Sub, Mul, Div)):
            s_exp = "(%s)" % s_exp
        elif isinstance(self.exp, Rational) and (self.exp.num < 0 or self.exp.den != 1):
            s_exp = "(%s)" % s_exp
        return "%s^%s" % (s_base, s_exp)

    def __repr__(self):
        return "Pow(%s, %s)" % (repr(self.base), repr(self.exp))

    def __eq__(self, other):
        if isinstance(other, Pow):
            return self.base == other.base and self.exp == other.exp
        return False

    def __hash__(self):
        return hash(("Pow", self.base, self.exp))


class Function(Expr):
    """Base class for mathematical functions."""

    def __init__(self, name, arg):
        self.name = name
        self.arg = to_expr(arg)
        self.args = (self.arg,)

    def free_symbols(self):
        return self.arg.free_symbols()

    def _subs_single(self, var_name, val_expr):
        return self.__class__(self.arg._subs_single(var_name, val_expr))

    def __str__(self):
        return "%s(%s)" % (self.name, str(self.arg))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.arg))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.arg == other.arg
        return False

    def __hash__(self):
        return hash((self.__class__.__name__, self.arg))


class Sin(Function):
    def __init__(self, arg):
        super(Sin, self).__init__("sin", arg)

    def evalf(self, subs_dict=None):
        return math.sin(self.arg.evalf(subs_dict))


class Cos(Function):
    def __init__(self, arg):
        super(Cos, self).__init__("cos", arg)

    def evalf(self, subs_dict=None):
        return math.cos(self.arg.evalf(subs_dict))


class Tan(Function):
    def __init__(self, arg):
        super(Tan, self).__init__("tan", arg)

    def evalf(self, subs_dict=None):
        return math.tan(self.arg.evalf(subs_dict))


class Sec(Function):
    def __init__(self, arg):
        super(Sec, self).__init__("sec", arg)

    def evalf(self, subs_dict=None):
        c = math.cos(self.arg.evalf(subs_dict))
        return 1.0 / c


class Csc(Function):
    def __init__(self, arg):
        super(Csc, self).__init__("csc", arg)

    def evalf(self, subs_dict=None):
        s = math.sin(self.arg.evalf(subs_dict))
        return 1.0 / s


class Cot(Function):
    def __init__(self, arg):
        super(Cot, self).__init__("cot", arg)

    def evalf(self, subs_dict=None):
        t = math.tan(self.arg.evalf(subs_dict))
        return 1.0 / t


class Asin(Function):
    def __init__(self, arg):
        super(Asin, self).__init__("asin", arg)

    def evalf(self, subs_dict=None):
        return math.asin(self.arg.evalf(subs_dict))


class Acos(Function):
    def __init__(self, arg):
        super(Acos, self).__init__("acos", arg)

    def evalf(self, subs_dict=None):
        return math.acos(self.arg.evalf(subs_dict))


class Atan(Function):
    def __init__(self, arg):
        super(Atan, self).__init__("atan", arg)

    def evalf(self, subs_dict=None):
        return math.atan(self.arg.evalf(subs_dict))


class Exp(Function):
    def __init__(self, arg):
        super(Exp, self).__init__("exp", arg)

    def evalf(self, subs_dict=None):
        return math.exp(self.arg.evalf(subs_dict))


class Ln(Function):
    def __init__(self, arg):
        super(Ln, self).__init__("ln", arg)

    def evalf(self, subs_dict=None):
        v = self.arg.evalf(subs_dict)
        if v <= 0:
            raise ValueError("Math domain error: ln(x) for non-positive argument")
        return math.log(v)


class Log(Function):
    def __init__(self, arg, base=None):
        super(Log, self).__init__("log", arg)
        self.base = to_expr(base) if base is not None else None
        if self.base is not None:
            self.args = (self.arg, self.base)

    def evalf(self, subs_dict=None):
        v = self.arg.evalf(subs_dict)
        if self.base is not None:
            b = self.base.evalf(subs_dict)
            return math.log(v, b)
        return math.log(v)

    def __str__(self):
        if self.base is not None:
            return "log(%s, %s)" % (str(self.arg), str(self.base))
        return "log(%s)" % str(self.arg)


class Sqrt(Function):
    def __init__(self, arg):
        super(Sqrt, self).__init__("sqrt", arg)

    def evalf(self, subs_dict=None):
        v = self.arg.evalf(subs_dict)
        return math.sqrt(v)


class Abs(Function):
    def __init__(self, arg):
        super(Abs, self).__init__("abs", arg)

    def evalf(self, subs_dict=None):
        return abs(self.arg.evalf(subs_dict))


# Shorthand constructors
sin = Sin
cos = Cos
tan = Tan
sec = Sec
csc = Csc
cot = Cot
asin = Asin
acos = Acos
atan = Atan
exp = Exp
ln = Ln
log = Log
sqrt = Sqrt
abs_ = Abs

pi = Symbol("pi")
e = Symbol("e")


# ---------------------------------------------------------------------------
# Lexer and Parser (Pure Python, Zero RE)
# ---------------------------------------------------------------------------

KNOWN_FUNCTIONS = {
    "sin": Sin,
    "cos": Cos,
    "tan": Tan,
    "sec": Sec,
    "csc": Csc,
    "cot": Cot,
    "asin": Asin,
    "acos": Acos,
    "atan": Atan,
    "exp": Exp,
    "ln": Ln,
    "log": Log,
    "sqrt": Sqrt,
    "abs": Abs,
}

KNOWN_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def _tokenize(s):
    """Scan string into token tuples (TYPE, VALUE) without using regular expressions."""
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c.isdigit() or (c == "." and i + 1 < n and s[i + 1].isdigit()):
            start = i
            has_dot = (c == ".")
            i += 1
            while i < n and (s[i].isdigit() or (s[i] == "." and not has_dot)):
                if s[i] == ".":
                    has_dot = True
                i += 1
            # Optional scientific exponent
            if i < n and s[i] in "eE" and i + 1 < n:
                offset = 1
                if s[i + offset] in "+-":
                    offset += 1
                if i + offset < n and s[i + offset].isdigit():
                    i += offset
                    while i < n and s[i].isdigit():
                        i += 1
            tokens.append(("NUM", s[start:i]))
            continue
        if c.isalpha() or c == "_":
            start = i
            i += 1
            while i < n and (s[i].isalnum() or s[i] == "_"):
                i += 1
            tokens.append(("ID", s[start:i]))
            continue
        if c == "*" and i + 1 < n and s[i + 1] == "*":
            tokens.append(("OP", "^"))
            i += 2
            continue
        if c in "+-*/^(),":
            tokens.append(("OP", c))
            i += 1
            continue
        # Unknown character - raise syntax error
        raise SyntaxError("Unexpected character: '%s' at position %d" % (c, i))
    return tokens


def _insert_implicit_multiplication(tokens):
    """Insert '*' tokens where multiplication is implied (e.g. 2x, 2(x+1), (x+1)(x-1))."""
    if not tokens:
        return []
    result = []
    for i in range(len(tokens)):
        result.append(tokens[i])
        if i + 1 < len(tokens):
            t1_type, t1_val = tokens[i]
            t2_type, t2_val = tokens[i + 1]

            t1_can_multiply = (
                (t1_type == "NUM") or
                (t1_type == "OP" and t1_val == ")") or
                (t1_type == "ID" and t1_val.lower() not in KNOWN_FUNCTIONS)
            )

            t2_can_be_multiplied = (
                (t2_type == "NUM") or
                (t2_type == "ID") or
                (t2_type == "OP" and t2_val == "(")
            )

            if t1_can_multiply and t2_can_be_multiplied:
                result.append(("OP", "*"))
    return result


class _Parser(object):
    """Precedence recursive descent parser for mathematical expressions."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ("EOF", "")

    def get(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse_expression(self, min_prec=1):
        """Parse binary operators using precedence climbing."""
        left = self.parse_primary()

        while True:
            tok = self.peek()
            if tok[0] != "OP":
                break
            op = tok[1]
            prec = self._get_prec(op)
            if prec < min_prec:
                break
            self.get()  # consume operator

            # Exponentiation is right-associative
            next_min_prec = prec if op == "^" else prec + 1
            right = self.parse_expression(next_min_prec)

            if op == "+":
                left = Add(left, right)
            elif op == "-":
                left = Sub(left, right)
            elif op == "*":
                left = Mul(left, right)
            elif op == "/":
                left = Div(left, right)
            elif op == "^":
                left = Pow(left, right)

        return left

    def _get_prec(self, op):
        if op in ("+", "-"):
            return 1
        if op in ("*", "/"):
            return 2
        if op == "^":
            return 4
        return 0

    def parse_primary(self):
        tok = self.peek()

        # Unary + or -
        if tok[0] == "OP" and tok[1] == "+":
            self.get()
            return self.parse_primary()
        if tok[0] == "OP" and tok[1] == "-":
            self.get()
            node = self.parse_expression(min_prec=3)
            return Mul(Rational(-1, 1), node)

        # Number literal
        if tok[0] == "NUM":
            self.get()
            return Rational(tok[1])

        # Parenthesized expression
        if tok[0] == "OP" and tok[1] == "(":
            self.get()
            expr = self.parse_expression(min_prec=1)
            closing = self.get()
            if closing[0] != "OP" or closing[1] != ")":
                raise SyntaxError("Expected ')' to close parenthesis")
            return expr

        # Identifier or function call
        if tok[0] == "ID":
            self.get()
            name = tok[1]
            lower_name = name.lower()

            # Function call: identifier followed by '('
            next_tok = self.peek()
            if next_tok[0] == "OP" and next_tok[1] == "(":
                self.get()  # consume '('
                args = []
                if self.peek() != ("OP", ")"):
                    while True:
                        args.append(self.parse_expression(min_prec=1))
                        if self.peek() == ("OP", ","):
                            self.get()
                        else:
                            break
                closing = self.get()
                if closing[0] != "OP" or closing[1] != ")":
                    raise SyntaxError("Expected ')' closing function arguments for '%s'" % name)

                if lower_name in KNOWN_FUNCTIONS:
                    cls = KNOWN_FUNCTIONS[lower_name]
                    if lower_name == "log" and len(args) == 2:
                        return Log(args[0], args[1])
                    if len(args) != 1:
                        raise ValueError("Function '%s' expects 1 argument, got %d" % (name, len(args)))
                    return cls(args[0])
                else:
                    # Generic function node
                    return Function(name, args[0] if args else Rational(0))

            # Symbolic constant or variable
            if lower_name in KNOWN_CONSTANTS:
                # Keep pi and e as exact symbols for algebraic preservation
                return Symbol(lower_name)

            return Symbol(name)

        raise SyntaxError("Unexpected token in primary expression: %s" % str(tok))


def parse(expr_str):
    """Parse expression string into symbolic AST."""
    if expr_str is None:
        return None
    s = str(expr_str).strip()
    if not s:
        return None
    raw_tokens = _tokenize(s)
    tokens = _insert_implicit_multiplication(raw_tokens)
    parser = _Parser(tokens)
    ast_tree = parser.parse_expression(min_prec=1)
    if parser.pos < len(tokens):
        raise SyntaxError("Dangling tokens after expression at token %s" % str(tokens[parser.pos]))
    return ast_tree


parse_expr = parse
lexer_parser = parse


# ---------------------------------------------------------------------------
# Algebraic Simplification
# ---------------------------------------------------------------------------

def _separate_coeff_and_term(expr):
    """Decompose expression into (Rational coefficient, symbolic kernel)."""
    if isinstance(expr, Rational):
        return expr, Rational(1, 1)
    if isinstance(expr, Mul):
        coeff = Rational(1, 1)
        rest = []
        for a in expr.args:
            if isinstance(a, Rational):
                coeff = coeff * a
            else:
                rest.append(a)
        if not rest:
            return coeff, Rational(1, 1)
        if len(rest) == 1:
            return coeff, rest[0]
        return coeff, Mul(*rest)
    return Rational(1, 1), expr


def simplify(expr):
    """Algebraic simplification: combine constants, like terms, factor cancellations, zero/one rules."""
    expr = to_expr(expr)
    if isinstance(expr, Rational) or isinstance(expr, Symbol):
        return expr

    # Simplify subexpressions recursively
    if isinstance(expr, Add):
        # Flatten and simplify terms
        terms = []
        for a in expr.args:
            s_a = simplify(a)
            if isinstance(s_a, Add):
                terms.extend(s_a.args)
            else:
                terms.append(s_a)

        # Collect constants and group like terms by kernel
        constant_sum = Rational(0, 1)
        term_map = []  # list of [kernel, coeff]

        for t in terms:
            c, k = _separate_coeff_and_term(t)
            if k == Rational(1, 1):
                constant_sum = constant_sum + c
            else:
                # Find matching kernel
                found = False
                for item in term_map:
                    if item[0] == k:
                        item[1] = item[1] + c
                        found = True
                        break
                if not found:
                    term_map.append([k, c])

        res_terms = []
        for k, c in term_map:
            if c.num == 0:
                continue
            if c.num == 1 and c.den == 1:
                res_terms.append(k)
            elif c.num == -1 and c.den == 1:
                res_terms.append(Mul(Rational(-1, 1), k))
            else:
                res_terms.append(Mul(c, k))

        if constant_sum.num != 0 or not res_terms:
            res_terms.append(constant_sum)

        if len(res_terms) == 1:
            return res_terms[0]
        return Add(*res_terms)

    if isinstance(expr, Sub):
        # Convert to Add(left, -right) and simplify
        return simplify(Add(expr.left, Mul(Rational(-1, 1), expr.right)))

    if isinstance(expr, Mul):
        factors = []
        for a in expr.args:
            s_a = simplify(a)
            if isinstance(s_a, Mul):
                factors.extend(s_a.args)
            else:
                factors.append(s_a)

        coeff = Rational(1, 1)
        non_constants = []

        for f in factors:
            if isinstance(f, Rational):
                coeff = coeff * f
            else:
                non_constants.append(f)

        if coeff.num == 0:
            return Rational(0, 1)

        # Group powers with identical base
        base_map = []  # [base, exp_sum]
        for f in non_constants:
            if isinstance(f, Pow):
                b = f.base
                e = f.exp
            else:
                b = f
                e = Rational(1, 1)
            found = False
            for item in base_map:
                if item[0] == b:
                    item[1] = simplify(Add(item[1], e))
                    found = True
                    break
            if not found:
                base_map.append([b, e])

        res_factors = []
        for b, e in base_map:
            if isinstance(e, Rational) and e.is_zero:
                continue
            if isinstance(e, Rational) and e.is_one:
                res_factors.append(b)
            else:
                res_factors.append(Pow(b, e))

        if not res_factors:
            return coeff
        if coeff.is_one:
            if len(res_factors) == 1:
                return res_factors[0]
            return Mul(*res_factors)
        if coeff == Rational(-1, 1) and len(res_factors) == 1:
            return Mul(Rational(-1, 1), res_factors[0])
        return Mul(coeff, *res_factors)

    if isinstance(expr, Div):
        s_num = simplify(expr.num)
        s_den = simplify(expr.den)

        if isinstance(s_den, Rational) and s_den.is_zero:
            raise ZeroDivisionError("Division by zero in simplify")
        if isinstance(s_num, Rational) and s_num.is_zero:
            return Rational(0, 1)
        if isinstance(s_den, Rational) and s_den.is_one:
            return s_num
        if isinstance(s_num, Rational) and isinstance(s_den, Rational):
            return s_num / s_den
        if s_num == s_den:
            return Rational(1, 1)

        # Rational polynomial factor cancellation: (x^2 - 1) / (x - 1) -> x + 1
        # Check if expanding and dividing produces exact polynomial
        try:
            canc = _cancel_rational(s_num, s_den)
            if canc is not None:
                return canc
        except Exception:
            pass

        return Div(s_num, s_den)

    if isinstance(expr, Pow):
        s_base = simplify(expr.base)
        s_exp = simplify(expr.exp)

        if isinstance(s_exp, Rational) and s_exp.is_zero:
            return Rational(1, 1)
        if isinstance(s_exp, Rational) and s_exp.is_one:
            return s_base
        if isinstance(s_base, Rational) and s_base.is_zero:
            return Rational(0, 1)
        if isinstance(s_base, Rational) and s_base.is_one:
            return Rational(1, 1)
        if isinstance(s_base, Rational) and isinstance(s_exp, Rational):
            return s_base ** s_exp
        return Pow(s_base, s_exp)

    if isinstance(expr, Function):
        s_arg = simplify(expr.arg)
        # Standard trigonometric special values
        if isinstance(expr, Sin):
            if isinstance(s_arg, Rational) and s_arg.is_zero:
                return Rational(0, 1)
        elif isinstance(expr, Cos):
            if isinstance(s_arg, Rational) and s_arg.is_zero:
                return Rational(1, 1)
        elif isinstance(expr, Tan):
            if isinstance(s_arg, Rational) and s_arg.is_zero:
                return Rational(0, 1)
        elif isinstance(expr, Exp):
            if isinstance(s_arg, Rational) and s_arg.is_zero:
                return Rational(1, 1)
        elif isinstance(expr, Ln):
            if isinstance(s_arg, Rational) and s_arg.is_one:
                return Rational(0, 1)
        return expr.__class__(s_arg)

    return expr


simplify_expr = simplify
algebraic_simplify = simplify


def _cancel_rational(num, den):
    """Attempt cancellation of polynomial factors for univariate rational functions."""
    syms = num.free_symbols() | den.free_symbols()
    if len(syms) != 1:
        return None
    var = list(syms)[0]
    p_num = _to_poly_coeffs(num, var)
    p_den = _to_poly_coeffs(den, var)
    if p_num is None or p_den is None:
        return None
    q, r = _poly_div(p_num, p_den)
    if all(c.is_zero for c in r):
        # Exact division!
        return _from_poly_coeffs(q, var)
    return None


def _to_poly_coeffs(expr, var):
    """Convert univariate polynomial into list of Rational coefficients [c0, c1, ..., cd]."""
    expr = expand(expr)
    terms = expr.args if isinstance(expr, Add) else (expr,)
    deg_map = {}
    for t in terms:
        c, k = _separate_coeff_and_term(t)
        if k == Rational(1, 1):
            deg = 0
        elif isinstance(k, Symbol) and k.name == var:
            deg = 1
        elif isinstance(k, Pow) and isinstance(k.base, Symbol) and k.base.name == var and isinstance(k.exp, Rational) and k.exp.den == 1 and k.exp.num >= 0:
            deg = k.exp.num
        else:
            return None
        deg_map[deg] = deg_map.get(deg, Rational(0, 1)) + c
    if not deg_map:
        return [Rational(0, 1)]
    max_d = max(deg_map.keys())
    coeffs = [deg_map.get(d, Rational(0, 1)) for d in range(max_d + 1)]
    return coeffs


def _from_poly_coeffs(coeffs, var):
    """Build Expr from list of Rational coefficients."""
    v = Symbol(var)
    terms = []
    for d, c in enumerate(coeffs):
        if c.is_zero:
            continue
        if d == 0:
            terms.append(c)
        elif d == 1:
            if c.is_one:
                terms.append(v)
            elif c == Rational(-1, 1):
                terms.append(Mul(Rational(-1, 1), v))
            else:
                terms.append(Mul(c, v))
        else:
            pow_term = Pow(v, Rational(d, 1))
            if c.is_one:
                terms.append(pow_term)
            elif c == Rational(-1, 1):
                terms.append(Mul(Rational(-1, 1), pow_term))
            else:
                terms.append(Mul(c, pow_term))
    if not terms:
        return Rational(0, 1)
    if len(terms) == 1:
        return terms[0]
    return Add(*terms)


def _poly_div(p, q):
    """Polynomial long division: p / q -> (quotient, remainder)."""
    # Remove leading zeros
    while len(p) > 1 and p[-1].is_zero:
        p.pop()
    while len(q) > 1 and q[-1].is_zero:
        q.pop()
    if q[-1].is_zero:
        raise ZeroDivisionError("Polynomial division by zero")
    d_p = len(p) - 1
    d_q = len(q) - 1
    if d_p < d_q:
        return [Rational(0, 1)], p
    quot = [Rational(0, 1)] * (d_p - d_q + 1)
    rem = list(p)
    for i in range(d_p - d_q, -1, -1):
        lead_rem = rem[i + d_q]
        coeff = lead_rem / q[-1]
        quot[i] = coeff
        for j in range(d_q + 1):
            rem[i + j] = rem[i + j] - coeff * q[j]
    while len(rem) > 1 and rem[-1].is_zero:
        rem.pop()
    return quot, rem


def expand(expr):
    """Expand polynomial products and powers into a sum of terms."""
    expr = to_expr(expr)
    if isinstance(expr, Mul):
        # Distribute multiplication across Add
        args = [expand(a) for a in expr.args]
        current = [Rational(1, 1)]
        for a in args:
            a_terms = a.args if isinstance(a, Add) else (a,)
            next_terms = []
            for c_t in current:
                for a_t in a_terms:
                    next_terms.append(Mul(c_t, a_t))
            current = next_terms
        return simplify(Add(*current))
    if isinstance(expr, Pow) and isinstance(expr.exp, Rational) and expr.exp.den == 1 and expr.exp.num > 1 and expr.exp.num <= 10:
        base = expand(expr.base)
        product = base
        for _ in range(expr.exp.num - 1):
            product = expand(Mul(product, base))
        return product
    if isinstance(expr, Add):
        return simplify(Add(*[expand(a) for a in expr.args]))
    if isinstance(expr, Sub):
        return simplify(Sub(expand(expr.left), expand(expr.right)))
    return expr


# ---------------------------------------------------------------------------
# Symbolic Differentiation & Step-by-Step Explanations
# ---------------------------------------------------------------------------

class StepList(list):
    """List of step strings with formatted multiline representation."""

    def __str__(self):
        return "\n".join(self)

    def __repr__(self):
        return "\n".join(self)


def diff(expr, var="x", steps=False):
    """Compute symbolic derivative of expr with respect to var."""
    expr = to_expr(expr)
    var_str = str(var).strip()

    if steps:
        return diff_steps(expr, var_str)

    res = _diff_node(expr, var_str)
    return simplify(res)


derivative = diff
differentiate = diff


def _diff_node(node, var):
    """Recursive differentiation implementation."""
    if isinstance(node, Rational):
        return Rational(0, 1)

    if isinstance(node, Symbol):
        if node.name == var:
            return Rational(1, 1)
        return Rational(0, 1)

    if isinstance(node, Add):
        return Add(*[_diff_node(a, var) for a in node.args])

    if isinstance(node, Sub):
        return Sub(_diff_node(node.left, var), _diff_node(node.right, var))

    if isinstance(node, Mul):
        # Product rule: (f*g*...)' = sum_i (f * ... * f_i' * ... * g)
        terms = []
        for i in range(len(node.args)):
            prod_factors = []
            for j in range(len(node.args)):
                if i == j:
                    prod_factors.append(_diff_node(node.args[j], var))
                else:
                    prod_factors.append(node.args[j])
            terms.append(Mul(*prod_factors))
        return Add(*terms)

    if isinstance(node, Div):
        # Quotient rule: (u/v)' = (u'*v - u*v') / v^2
        u = node.num
        v = node.den
        du = _diff_node(u, var)
        dv = _diff_node(v, var)
        num = Sub(Mul(du, v), Mul(u, dv))
        den = Pow(v, Rational(2, 1))
        return Div(num, den)

    if isinstance(node, Pow):
        base = node.base
        exp = node.exp
        base_dep = var in base.free_symbols()
        exp_dep = var in exp.free_symbols()

        if not base_dep and not exp_dep:
            return Rational(0, 1)
        if base_dep and not exp_dep:
            # Power rule & chain rule: d/dx(u^n) = n * u^(n-1) * u'
            du = _diff_node(base, var)
            return Mul(exp, Pow(base, Sub(exp, Rational(1, 1))), du)
        if not base_dep and exp_dep:
            # Exponential rule & chain rule: d/dx(a^v) = a^v * ln(a) * v'
            dv = _diff_node(exp, var)
            return Mul(node, Ln(base), dv)
        # General case u^v: d/dx(u^v) = u^v * (v' * ln(u) + v * u' / u)
        du = _diff_node(base, var)
        dv = _diff_node(exp, var)
        return Mul(node, Add(Mul(dv, Ln(base)), Div(Mul(exp, du), base)))

    if isinstance(node, Function):
        arg = node.arg
        d_arg = _diff_node(arg, var)
        if isinstance(node, Sin):
            return Mul(Cos(arg), d_arg)
        if isinstance(node, Cos):
            return Mul(Rational(-1, 1), Sin(arg), d_arg)
        if isinstance(node, Tan):
            return Mul(Pow(Sec(arg), Rational(2, 1)), d_arg)
        if isinstance(node, Sec):
            return Mul(Sec(arg), Tan(arg), d_arg)
        if isinstance(node, Csc):
            return Mul(Rational(-1, 1), Csc(arg), Cot(arg), d_arg)
        if isinstance(node, Cot):
            return Mul(Rational(-1, 1), Pow(Csc(arg), Rational(2, 1)), d_arg)
        if isinstance(node, Exp):
            return Mul(Exp(arg), d_arg)
        if isinstance(node, Ln):
            return Div(d_arg, arg)
        if isinstance(node, Log):
            b = node.base if node.base is not None else Rational(10, 1)
            return Div(d_arg, Mul(arg, Ln(b)))
        if isinstance(node, Sqrt):
            return Div(d_arg, Mul(Rational(2, 1), Sqrt(arg)))
        if isinstance(node, Asin):
            return Div(d_arg, Sqrt(Sub(Rational(1, 1), Pow(arg, Rational(2, 1)))))
        if isinstance(node, Acos):
            return Mul(Rational(-1, 1), Div(d_arg, Sqrt(Sub(Rational(1, 1), Pow(arg, Rational(2, 1))))))
        if isinstance(node, Atan):
            return Div(d_arg, Add(Rational(1, 1), Pow(arg, Rational(2, 1))))

    return Rational(0, 1)


def diff_steps(expr, var="x"):
    """Generate detailed step-by-step calculus differentiation explanation."""
    expr = to_expr(expr)
    var_str = str(var).strip()
    steps = StepList()
    steps.append("1. Differentiating expression with respect to %s: d/d%s [%s]" % (var_str, var_str, str(expr)))

    if isinstance(expr, Rational) or (expr.free_symbols() and var_str not in expr.free_symbols()):
        steps.append("2. Constant rule: d/d%s [c] = 0 for constant expression." % var_str)
        res = Rational(0, 1)
    elif isinstance(expr, Symbol) and expr.name == var_str:
        steps.append("2. Linear variable rule: d/d%s [%s] = 1." % (var_str, var_str))
        res = Rational(1, 1)
    elif isinstance(expr, Add) or isinstance(expr, Sub):
        steps.append("2. Sum / Difference rule: differentiating term-by-term: d/d%s [f +/- g] = f' +/- g'." % var_str)
        for i, t in enumerate(expr.args):
            dt = simplify(_diff_node(t, var_str))
            steps.append("   Term %d: d/d%s [%s] = %s" % (i + 1, var_str, str(t), str(dt)))
        res = diff(expr, var_str)
    elif isinstance(expr, Mul):
        steps.append("2. Product rule: d/d%s [f * g] = f' * g + f * g'." % var_str)
        res = diff(expr, var_str)
    elif isinstance(expr, Div):
        steps.append("2. Quotient rule: d/d%s [f / g] = (f' * g - f * g') / (g^2) for denominator %s." % (var_str, str(expr.den)))
        res = diff(expr, var_str)
    elif isinstance(expr, Pow):
        if var_str not in expr.exp.free_symbols():
            steps.append("2. Power rule: d/d%s [u^n] = n * u^(n-1) * u' with exponent reduction." % var_str)
        else:
            steps.append("2. Exponential rule: d/d%s [a^u] = a^u * ln(a) * u'." % var_str)
        res = diff(expr, var_str)
    elif isinstance(expr, Function):
        steps.append("2. Chain rule: d/d%s [f(g(%s))] = f'(g(%s)) * g'(%s) with inner function %s." % (var_str, var_str, var_str, var_str, str(expr.arg)))
        res = diff(expr, var_str)
    else:
        res = diff(expr, var_str)

    steps.append("Result: %s" % str(res))
    return steps


derivative_steps = diff_steps
differentiate_steps = diff_steps


# ---------------------------------------------------------------------------
# Symbolic & Definite Integration, Riemann Sums
# ---------------------------------------------------------------------------

def integrate(expr, var="x", a=None, b=None):
    """Compute symbolic indefinite or definite integral."""
    expr = to_expr(expr)
    var_str = str(var).strip()

    if a is not None and b is not None:
        return _definite_integral(expr, var_str, a, b)

    res = _integrate_node(expr, var_str)
    return simplify(res)


integral = integrate
anti_derivative = integrate


def _integrate_node(node, var):
    """Symbolic indefinite integration engine."""
    v = Symbol(var)

    if isinstance(node, Rational):
        return Mul(node, v)

    if isinstance(node, Symbol):
        if node.name == var:
            return Mul(Rational(1, 2), Pow(v, Rational(2, 1)))
        return Mul(node, v)

    if isinstance(node, Add):
        return Add(*[_integrate_node(a, var) for a in node.args])

    if isinstance(node, Sub):
        return Sub(_integrate_node(node.left, var), _integrate_node(node.right, var))

    if isinstance(node, Mul):
        # Extract constant factors: int(c * f(x) dx) = c * int(f(x) dx)
        c, k = _separate_coeff_and_term(node)
        if c != Rational(1, 1):
            return Mul(c, _integrate_node(k, var))

    # Power rule: x^n
    if isinstance(node, Pow):
        if isinstance(node.base, Symbol) and node.base.name == var:
            if isinstance(node.exp, Rational) and node.exp == Rational(-1, 1):
                return Ln(v)
            new_exp = simplify(Add(node.exp, Rational(1, 1)))
            return Div(Pow(v, new_exp), new_exp)

    # 1/x -> ln(x)
    if isinstance(node, Div):
        if isinstance(node.num, Rational) and isinstance(node.den, Symbol) and node.den.name == var:
            return Mul(node.num, Ln(v))
        if isinstance(node.num, Rational) and isinstance(node.den, Pow) and isinstance(node.den.base, Symbol) and node.den.base.name == var:
            # c / x^n = c * x^-n
            neg_pow = Pow(v, Mul(Rational(-1, 1), node.den.exp))
            return Mul(node.num, _integrate_node(neg_pow, var))

    # Trigonometric functions
    if isinstance(node, Function):
        arg = node.arg
        if isinstance(arg, Symbol) and arg.name == var:
            if isinstance(node, Sin):
                return Mul(Rational(-1, 1), Cos(v))
            if isinstance(node, Cos):
                return Sin(v)
            if isinstance(node, Exp):
                return Exp(v)

    return Mul(node, v)


def _definite_integral(expr, var, a, b):
    """Definite integral using Fundamental Theorem of Calculus with Simpson fallback."""
    a_val = float(a)
    b_val = float(b)
    if a_val == b_val:
        return Rational(0, 1)

    try:
        F = integrate(expr, var)
        fb = F.subs(var, b_val).evalf()
        fa = F.subs(var, a_val).evalf()
        return fb - fa
    except Exception:
        return riemann_sum(expr, var, a_val, b_val, n=100, method="simpson")


def riemann_sum(expr, var="x", a=0, b=1, n=10, method="midpoint"):
    """Numerical Riemann sum partition approximation."""
    expr = to_expr(expr)
    var_str = str(var).strip()
    a_f = float(a)
    b_f = float(b)
    n_i = int(n)
    if n_i <= 0:
        raise ValueError("Number of partitions n must be positive")

    dx = (b_f - a_f) / float(n_i)
    total = 0.0

    if method == "left":
        for i in range(n_i):
            xi = a_f + i * dx
            total += expr.subs(var_str, xi).evalf()
        return total * dx

    elif method == "right":
        for i in range(1, n_i + 1):
            xi = a_f + i * dx
            total += expr.subs(var_str, xi).evalf()
        return total * dx

    elif method == "trapezoid":
        f_a = expr.subs(var_str, a_f).evalf()
        f_b = expr.subs(var_str, b_f).evalf()
        sum_mid = 0.0
        for i in range(1, n_i):
            xi = a_f + i * dx
            sum_mid += expr.subs(var_str, xi).evalf()
        return (dx / 2.0) * (f_a + 2.0 * sum_mid + f_b)

    elif method == "simpson":
        if n_i % 2 != 0:
            n_i += 1
            dx = (b_f - a_f) / float(n_i)
        f_a = expr.subs(var_str, a_f).evalf()
        f_b = expr.subs(var_str, b_f).evalf()
        sum_odd = 0.0
        sum_even = 0.0
        for i in range(1, n_i):
            xi = a_f + i * dx
            val = expr.subs(var_str, xi).evalf()
            if i % 2 == 1:
                sum_odd += val
            else:
                sum_even += val
        return (dx / 3.0) * (f_a + 4.0 * sum_odd + 2.0 * sum_even + f_b)

    else:
        # Default: midpoint
        for i in range(n_i):
            xi = a_f + (i + 0.5) * dx
            total += expr.subs(var_str, xi).evalf()
        return total * dx


riemann = riemann_sum
approx_integral = riemann_sum


# ---------------------------------------------------------------------------
# Limits & Taylor Series
# ---------------------------------------------------------------------------

def limit(expr, var="x", target=0, direction="both"):
    """Evaluate mathematical limit as var approaches target using direct substitution, cancellation, and L'Hopital."""
    expr = to_expr(expr)
    var_str = str(var).strip()
    target_f = float(target)

    # First simplify expression to cancel removable rational factors
    s_expr = simplify(expr)

    # Try direct substitution
    try:
        val = s_expr.subs(var_str, target_f).evalf()
        if not math.isnan(val) and not math.isinf(val):
            return val
    except (ZeroDivisionError, ValueError, OverflowError):
        pass

    # L'Hopital's rule for rational expressions u(x) / v(x)
    if isinstance(s_expr, Div):
        u = s_expr.num
        v = s_expr.den
        for _ in range(5):
            u_prime = diff(u, var_str)
            v_prime = diff(v, var_str)
            try:
                up_val = u_prime.subs(var_str, target_f).evalf()
                vp_val = v_prime.subs(var_str, target_f).evalf()
                if abs(vp_val) > 1e-12:
                    return up_val / vp_val
            except Exception:
                pass
            u = u_prime
            v = v_prime

    # Numerical perturbation approach near target
    epsilons = [1e-4, 1e-5, 1e-6]
    for eps in epsilons:
        try:
            v_right = expr.subs(var_str, target_f + eps).evalf()
            v_left = expr.subs(var_str, target_f - eps).evalf()
            if direction == "right":
                return v_right
            elif direction == "left":
                return v_left
            else:
                if abs(v_right - v_left) < 1e-2:
                    return (v_right + v_left) / 2.0
                return v_right
        except Exception:
            continue

    return target_f


eval_limit = limit
calc_limit = limit


def series(expr, var="x", point=0, order=4):
    """Compute Taylor / Maclaurin polynomial series expansion around point up to specified order."""
    expr = to_expr(expr)
    var_str = str(var).strip()
    v = Symbol(var_str)
    pt_f = float(point)
    order_i = int(order)

    terms = []
    current_deriv = expr
    fact = 1

    for k in range(order_i):
        if k > 0:
            fact *= k
        try:
            c = current_deriv.subs(var_str, pt_f).evalf()
        except Exception:
            c = float(limit(current_deriv, var_str, pt_f))

        coef = float_to_rational(c)
        if not coef.is_zero:
            coeff_div_fact = coef / Rational(fact, 1)
            if k == 0:
                terms.append(coeff_div_fact)
            else:
                if pt_f == 0.0:
                    power_term = Pow(v, Rational(k, 1)) if k > 1 else v
                else:
                    diff_term = Sub(v, float_to_rational(pt_f))
                    power_term = Pow(diff_term, Rational(k, 1)) if k > 1 else diff_term

                if coeff_div_fact.is_one:
                    terms.append(power_term)
                elif coeff_div_fact == Rational(-1, 1):
                    terms.append(Mul(Rational(-1, 1), power_term))
                else:
                    terms.append(Mul(coeff_div_fact, power_term))

        current_deriv = diff(current_deriv, var_str)

    if not terms:
        return Rational(0, 1)
    if len(terms) == 1:
        return terms[0]
    return Add(*terms)


taylor = series
taylor_series = series
maclaurin = series


# ---------------------------------------------------------------------------
# Calculus Geometry: Tangent & Normal Lines
# ---------------------------------------------------------------------------

def tangent_line(expr, point_c, var="x"):
    """Compute linear tangent line equation y = m*x + b to curve at point x = point_c."""
    if isinstance(point_c, str) and not isinstance(var, str):
        point_c, var = var, point_c
    expr = to_expr(expr)
    var_str = str(var).strip()
    v = Symbol(var_str)
    c_f = float(point_c)

    y0 = expr.subs(var_str, c_f).evalf()
    df = diff(expr, var_str)
    m = df.subs(var_str, c_f).evalf()

    m_rat = float_to_rational(m)
    b_val = y0 - m * c_f
    b_rat = float_to_rational(b_val)

    if m_rat.is_zero:
        return b_rat
    if m_rat.is_one:
        mx_term = v
    elif m_rat == Rational(-1, 1):
        mx_term = Mul(Rational(-1, 1), v)
    else:
        mx_term = Mul(m_rat, v)

    if b_rat.is_zero:
        return mx_term
    if b_rat.num < 0:
        return Sub(mx_term, Rational(-b_rat.num, b_rat.den))
    return Add(mx_term, b_rat)


tangent = tangent_line
calc_tangent_line = tangent_line


def normal_line(expr, point_c, var="x"):
    """Compute normal line perpendicular to curve at point x = point_c."""
    if isinstance(point_c, str) and not isinstance(var, str):
        point_c, var = var, point_c
    expr = to_expr(expr)
    var_str = str(var).strip()
    v = Symbol(var_str)
    c_f = float(point_c)

    y0 = expr.subs(var_str, c_f).evalf()
    df = diff(expr, var_str)
    m = df.subs(var_str, c_f).evalf()

    if abs(m) < 1e-12:
        # Vertical normal line x = c
        return v

    m_normal = -1.0 / m
    m_rat = float_to_rational(m_normal)
    b_val = y0 - m_normal * c_f
    b_rat = float_to_rational(b_val)

    if m_rat.is_one:
        mx_term = v
    elif m_rat == Rational(-1, 1):
        mx_term = Mul(Rational(-1, 1), v)
    else:
        mx_term = Mul(m_rat, v)

    if b_rat.is_zero:
        return mx_term
    if b_rat.num < 0:
        return Sub(mx_term, Rational(-b_rat.num, b_rat.den))
    return Add(mx_term, b_rat)


normal = normal_line
calc_normal_line = normal_line


# ---------------------------------------------------------------------------
# Evaluation and Substitution Helpers
# ---------------------------------------------------------------------------

def evaluate(expr, **subs):
    """Evaluate expression with variable substitutions."""
    expr = to_expr(expr)
    return expr.evalf(subs)


eval_expr = evaluate
substitute = evaluate


def subs(expr, *args, **kwargs):
    """Substitute variables into expression."""
    expr = to_expr(expr)
    if args and isinstance(args[0], dict):
        d = dict(args[0])
        d.update(kwargs)
        return expr.subs(d)
    if len(args) == 2:
        return expr.subs(args[0], args[1])
    if kwargs:
        return expr.subs(kwargs)
    return expr


# ---------------------------------------------------------------------------
# Calculator UI & Dual-Mode CLI Execution
# ---------------------------------------------------------------------------

def run_ui():
    """Run interactive calculator UI mode on TI hardware or fallback to console."""
    if HAS_TI:
        ti_system.disp_clr()
        ti_system.disp_at(1, 1, "FlowCE CAS v1.0")
        ti_system.disp_at(2, 1, "TI-84 Evo Python")
        ti_system.disp_at(4, 1, "Ready. Type expr:")
        ti_draw.clear()
        ti_draw.set_color(0, 0, 128)
        ti_draw.draw_text(10, 20, "FlowCE CAS Ready")
    else:
        print("FlowCE CAS v1.0 - Pure Python TI-84 Evo Computer Algebra System")
        print("Enter expressions or functions (e.g. diff('x^2', 'x')). Press Ctrl+C or 'exit' to quit.")


def cli_main(args=None):
    """Command line interface entrypoint supporting batch flags and interactive REPL."""
    if args is None:
        args = sys.argv[1:]

    if not args:
        if sys.stdin.isatty():
            run_ui()
        return

    # Process command line arguments
    cmd = args[0]
    if cmd == "--diff" and len(args) >= 2:
        var = args[2] if len(args) >= 3 else "x"
        print(str(diff(args[1], var)))
    elif cmd == "--int" and len(args) >= 2:
        var = args[2] if len(args) >= 3 else "x"
        print(str(integrate(args[1], var)))
    elif cmd == "--sim" and len(args) >= 2:
        print(str(simplify(args[1])))
    else:
        # Direct expression evaluation
        try:
            node = parse(cmd)
            print(str(node))
        except Exception as err:
            print("Error: %s" % str(err))


if __name__ == "__main__":
    cli_main()
