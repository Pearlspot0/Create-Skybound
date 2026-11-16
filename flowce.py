# FlowCE CAS for TI-84 Evo / TI-84 Plus CE Python
# Ultra-compact MicroPython CAS engine.
import math
import sys

try:
    import gc
    gc.collect()
except ImportError:
    pass

try:
    import ti_system
    import ti_draw
    import ti_plotlib
    import ti_hub
    HAS_TI = True
except ImportError:
    HAS_TI = False

def gcd(a, b):
    a, b = abs(int(a)), abs(int(b))
    while b: a, b = b, a % b
    return a

def _bin(a, b, op):
    if isinstance(a, Rational) and isinstance(b, Rational):
        if op == '+': return Rational(a.num * b.den + b.num * a.den, a.den * b.den)
        if op == '-': return Rational(a.num * b.den - b.num * a.den, a.den * b.den)
        if op == '*': return Rational(a.num * b.num, a.den * b.den)
        if op == '/':
            if b.num == 0: raise ZeroDivisionError("div 0")
            return Rational(a.num * b.den, a.den * b.num)
        if op == '^':
            if b.den == 1:
                p = b.num
                return Rational(a.num ** p, a.den ** p) if p >= 0 else Rational(a.den ** (-p), a.num ** (-p))
            fv, base = float(b), float(a)
            if base < 0 and abs(fv - round(fv)) > 1e-9: raise ValueError("Negative base")
            return float_to_rational(base ** fv)
    if isinstance(a, Rational) and isinstance(b, (int, float)):
        b_rat = to_expr(b)
        if isinstance(b_rat, Rational): return _bin(a, b_rat, op)
        return float(a) + b if op == '+' else (float(a) - b if op == '-' else (float(a) * b if op == '*' else float(a) / b))
    if isinstance(b, Rational) and isinstance(a, (int, float)):
        a_rat = to_expr(a)
        if isinstance(a_rat, Rational): return _bin(a_rat, b, op)
        return a + float(b) if op == '+' else (a - float(b) if op == '-' else (a * float(b) if op == '*' else a / float(b)))
    if op == '+': return Add(a, b)
    if op == '-': return Sub(a, b)
    if op == '*': return Mul(a, b)
    if op == '/': return Div(a, b)
    if op == '^': return Pow(a, b)

class Expr(object):
    def __add__(self, o): return _bin(self, to_expr(o), '+')
    def __radd__(self, o): return _bin(to_expr(o), self, '+')
    def __sub__(self, o): return _bin(self, to_expr(o), '-')
    def __rsub__(self, o): return _bin(to_expr(o), self, '-')
    def __mul__(self, o): return _bin(self, to_expr(o), '*')
    def __rmul__(self, o): return _bin(to_expr(o), self, '*')
    def __truediv__(self, o): return _bin(self, to_expr(o), '/')
    def __rtruediv__(self, o): return _bin(to_expr(o), self, '/')
    def __div__(self, o): return self.__truediv__(o)
    def __rdiv__(self, o): return self.__rtruediv__(o)
    def __pow__(self, o): return _bin(self, to_expr(o), '^')
    def __rpow__(self, o): return _bin(to_expr(o), self, '^')
    def __neg__(self): return self * Rational(-1, 1)
    def __pos__(self): return self
    def __abs__(self): return Abs(self)
    def diff(self, v="x"): return diff(self, v)
    def diff_steps(self, v="x"): return diff_steps(self, v)
    def integrate(self, v="x", a=None, b=None): return integrate(self, v, a, b)
    def simplify(self): return simplify(self)
    def expand(self): return expand(self)
    def subs(self, var, val=None):
        if val is None and isinstance(var, dict):
            res = self
            for k, v in var.items(): res = res.subs(k, v)
            return res
        return self._subs_single(str(var), to_expr(val))
    def _subs_single(self, v, val): return self
    def evalf(self, d=None): return float(self) if not d else self.subs(d).evalf()
    def free_symbols(self): return set()
    @property
    def is_zero(self): return False
    @property
    def is_one(self): return False

class Rational(Expr):
    def __init__(self, n, d=1):
        if isinstance(n, str) and d == 1:
            p = n.split("/")
            if len(p) == 2: n, d = int(p[0].strip()), int(p[1].strip())
            else: r = float_to_rational(float(n)); n, d = r.num, r.den
        elif isinstance(n, Rational):
            n, d = n.num, n.den * (int(d.num) // int(d.den) if isinstance(d, Rational) else int(d))
        elif isinstance(n, float) and d == 1:
            r = float_to_rational(n); n, d = r.num, r.den
        else:
            n, d = int(n), (int(d.num) // int(d.den) if isinstance(d, Rational) else int(d))
        if d == 0: raise ZeroDivisionError("zero den")
        if d < 0: n, d = -n, -d
        g = gcd(n, d)
        self.num, self.den = n // g, d // g

    @property
    def is_zero(self): return self.num == 0
    @property
    def is_one(self): return self.num == 1 and self.den == 1
    @property
    def is_integer(self): return self.den == 1
    @property
    def is_negative(self): return self.num < 0

    def __neg__(self): return Rational(-self.num, self.den)
    def __abs__(self): return Rational(abs(self.num), self.den)
    def __float__(self): return float(self.num) / float(self.den)
    def __int__(self): return self.num // self.den
    def __eq__(self, o):
        if isinstance(o, Rational): return self.num == o.num and self.den == o.den
        if isinstance(o, int): return self.den == 1 and self.num == o
        return abs(float(self) - o) < 1e-12 if isinstance(o, float) else False
    def __hash__(self): return hash((self.num, self.den))
    def __str__(self): return str(self.num) if self.den == 1 else "%d/%d" % (self.num, self.den)
    def __repr__(self): return str(self)
    def evalf(self, d=None): return float(self.num) / float(self.den)

def float_to_rational(v, max_den=1000, tol=1e-6):
    if math.isnan(v) or math.isinf(v): return v
    sign, v = (-1 if v < 0 else 1), abs(v)
    if abs(v - round(v)) < tol: return Rational(sign * int(round(v)), 1)
    p0, q0, p1, q1, x = 0, 1, 1, 0, v
    for _ in range(12):
        a = int(x)
        p2, q2 = a * p1 + p0, a * q1 + q0
        if q2 > max_den: break
        p0, q0, p1, q1 = p1, q1, p2, q2
        if abs(v - float(p1) / float(q1)) < tol: return Rational(sign * p1, q1)
        d = x - a
        if d < 1e-12: break
        x = 1.0 / d
    return Rational(sign * p1, q1)

def to_expr(obj):
    if isinstance(obj, Expr): return obj
    if isinstance(obj, int): return Rational(obj, 1)
    if isinstance(obj, float):
        return Rational(int(obj), 1) if obj.is_integer() else float_to_rational(obj)
    if isinstance(obj, str): return parse(obj)
    return obj

class Symbol(Expr):
    def __init__(self, name): self.name = str(name).strip()
    def free_symbols(self): return {self.name}
    def _subs_single(self, v, val): return val if self.name == v else self
    def evalf(self, d=None):
        if d and self.name in d: return float(d[self.name])
        if self.name == "pi": return math.pi
        if self.name == "e": return math.e
        raise ValueError("Unbound: %s" % self.name)
    def __str__(self): return self.name
    def __repr__(self): return self.name
    def __eq__(self, o): return isinstance(o, Symbol) and self.name == o.name
    def __hash__(self): return hash(self.name)

def symbols(names_str):
    parts = names_str.replace(",", " ").split()
    syms = [Symbol(p) for p in parts]
    return syms[0] if len(syms) == 1 else tuple(syms)

class Nary(Expr):
    def __init__(self, *args):
        flat = []
        for a in args:
            x = to_expr(a)
            if isinstance(x, self.__class__): flat.extend(x.args)
            else: flat.append(x)
        self.args = tuple(flat)
    def free_symbols(self): return set().union(*[a.free_symbols() for a in self.args])
    def _subs_single(self, v, val): return self.__class__(*[a._subs_single(v, val) for a in self.args])
    def __eq__(self, o): return isinstance(o, self.__class__) and self.args == o.args
    def __hash__(self): return hash((self.__class__.__name__, self.args))

class Add(Nary):
    def evalf(self, d=None): return sum(a.evalf(d) for a in self.args)
    def __str__(self):
        if not self.args: return "0"
        parts = []
        for i, a in enumerate(self.args):
            s = str(a)
            if i > 0 and not s.startswith("-"): parts.extend(["+", s])
            elif i > 0 and s.startswith("-"): parts.extend(["-", s[1:].strip()])
            else: parts.append(s)
        return " ".join(parts)
    def __repr__(self): return "Add(%s)" % ", ".join(repr(a) for a in self.args)

class Mul(Nary):
    def evalf(self, d=None):
        p = 1.0
        for a in self.args: p *= a.evalf(d)
        return p
    def __str__(self):
        if not self.args: return "1"
        res = [("(%s)" % str(a) if isinstance(a, (Add, Sub)) else str(a)) for a in self.args]
        return "*".join(res)
    def __repr__(self): return "Mul(%s)" % ", ".join(repr(a) for a in self.args)

class Binary(Expr):
    def __init__(self, left, right):
        self.left, self.right = to_expr(left), to_expr(right)
        self.args = (self.left, self.right)
    def free_symbols(self): return self.left.free_symbols() | self.right.free_symbols()
    def _subs_single(self, v, val):
        return self.__class__(self.left._subs_single(v, val), self.right._subs_single(v, val))
    def __eq__(self, o): return isinstance(o, self.__class__) and self.left == o.left and self.right == o.right
    def __hash__(self): return hash((self.__class__.__name__, self.left, self.right))

class Sub(Binary):
    def evalf(self, d=None): return self.left.evalf(d) - self.right.evalf(d)
    def __str__(self):
        sr = ("(%s)" % str(self.right)) if isinstance(self.right, (Add, Sub)) else str(self.right)
        return "%s - %s" % (str(self.left), sr)
    def __repr__(self): return "Sub(%s, %s)" % (repr(self.left), repr(self.right))

class Div(Binary):
    @property
    def num(self): return self.left
    @property
    def den(self): return self.right
    def evalf(self, d=None):
        den = self.right.evalf(d)
        if den == 0: raise ZeroDivisionError("division by zero")
        return self.left.evalf(d) / den
    def __str__(self):
        sn = ("(%s)" % str(self.left)) if isinstance(self.left, (Add, Sub)) else str(self.left)
        sd = ("(%s)" % str(self.right)) if isinstance(self.right, (Add, Sub, Mul, Div)) else str(self.right)
        return "%s/%s" % (sn, sd)
    def __repr__(self): return "Div(%s, %s)" % (repr(self.left), repr(self.right))

class Pow(Binary):
    @property
    def base(self): return self.left
    @property
    def exp(self): return self.right
    def evalf(self, d=None): return (self.left.evalf(d)) ** (self.right.evalf(d))
    def __str__(self):
        sb = ("(%s)" % str(self.left)) if isinstance(self.left, (Add, Sub, Mul, Div)) else str(self.left)
        se = ("(%s)" % str(self.right)) if isinstance(self.right, (Add, Sub, Mul, Div)) else str(self.right)
        return "%s^%s" % (sb, se)
    def __repr__(self): return "Pow(%s, %s)" % (repr(self.left), repr(self.right))

class Function(Expr):
    def __init__(self, name, arg, base=None):
        self.name, self.arg, self.base, self.args = name, to_expr(arg), base, (to_expr(arg),)
    def free_symbols(self): return self.arg.free_symbols()
    def _subs_single(self, v, val):
        return Function(self.name, self.arg._subs_single(v, val), self.base)
    def evalf(self, d=None):
        v, n = self.arg.evalf(d), self.name
        if n == "sin": return math.sin(v)
        if n == "cos": return math.cos(v)
        if n == "tan": return math.tan(v)
        if n == "sec": return 1.0 / math.cos(v)
        if n == "csc": return 1.0 / math.sin(v)
        if n == "cot": return 1.0 / math.tan(v)
        if n == "asin": return math.asin(v)
        if n == "acos": return math.acos(v)
        if n == "atan": return math.atan(v)
        if n == "exp": return math.exp(v)
        if n == "ln": return math.log(v)
        if n == "log": return math.log(v) / math.log(self.base.evalf(d) if self.base else 10.0)
        if n == "sqrt": return math.sqrt(v)
        if n == "abs": return abs(v)
        raise ValueError("Unknown: %s" % n)
    def __str__(self): return "%s(%s)" % (self.name, str(self.arg))
    def __repr__(self): return "%s(%s)" % (self.name, repr(self.arg))
    def __eq__(self, o): return isinstance(o, Function) and self.name == o.name and self.arg == o.arg
    def __hash__(self): return hash((self.name, self.arg))

class Sin(Function): __init__ = lambda s, a: Function.__init__(s, "sin", a)
class Cos(Function): __init__ = lambda s, a: Function.__init__(s, "cos", a)
class Tan(Function): __init__ = lambda s, a: Function.__init__(s, "tan", a)
class Sec(Function): __init__ = lambda s, a: Function.__init__(s, "sec", a)
class Csc(Function): __init__ = lambda s, a: Function.__init__(s, "csc", a)
class Cot(Function): __init__ = lambda s, a: Function.__init__(s, "cot", a)
class Asin(Function): __init__ = lambda s, a: Function.__init__(s, "asin", a)
class Acos(Function): __init__ = lambda s, a: Function.__init__(s, "acos", a)
class Atan(Function): __init__ = lambda s, a: Function.__init__(s, "atan", a)
class Exp(Function): __init__ = lambda s, a: Function.__init__(s, "exp", a)
class Ln(Function): __init__ = lambda s, a: Function.__init__(s, "ln", a)
class Log(Function): __init__ = lambda s, a, b=None: Function.__init__(s, "log", a, b)
class Sqrt(Function): __init__ = lambda s, a: Function.__init__(s, "sqrt", a)
class Abs(Function): __init__ = lambda s, a: Function.__init__(s, "abs", a)

sin, cos, tan = Sin, Cos, Tan
sec, csc, cot = Sec, Csc, Cot
asin, acos, atan = Asin, Acos, Atan
exp, ln, log, sqrt, abs_ = Exp, Ln, Log, Sqrt, Abs
pi, e = Symbol("pi"), Symbol("e")

KNOWN_FUNCTIONS = {
    "sin": Sin, "cos": Cos, "tan": Tan, "sec": Sec, "csc": Csc, "cot": Cot,
    "asin": Asin, "acos": Acos, "atan": Atan, "exp": Exp, "ln": Ln, "log": Log,
    "sqrt": Sqrt, "abs": Abs,
}

KNOWN_CONSTANTS = {"pi": math.pi, "e": math.e}

def _tokenize(s):
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c <= ' ': i += 1; continue
        if c.isdigit() or (c == '.' and i + 1 < n and s[i+1].isdigit()):
            j = i + 1
            while j < n and (s[j].isdigit() or s[j] == '.'): j += 1
            if j < n and s[j] in 'eE':
                off = 2 if j + 1 < n and s[j+1] in '+-' else 1
                if j + off < n and s[j+off].isdigit():
                    k = j + off
                    while k < n and s[k].isdigit(): k += 1
                    j = k
            toks.append(('NUM', s[i:j])); i = j
        elif c.isalpha() or c == '_':
            j = i + 1
            while j < n and (s[j].isalnum() or s[j] == '_'): j += 1
            toks.append(('ID', s[i:j])); i = j
        elif s[i:i+2] == '**': toks.append(('OP', '^')); i += 2
        elif c in '+-*/^(),': toks.append(('OP', c)); i += 1
        else: raise SyntaxError(c)
    return toks

def _insert_implicit_multiplication(toks):
    res = []
    for i in range(len(toks)):
        res.append(toks[i])
        if i + 1 < len(toks):
            t1, t2 = toks[i], toks[i+1]
            c1 = t1[0] == 'NUM' or t1[1] == ')' or (t1[0] == 'ID' and t1[1].lower() not in KNOWN_FUNCTIONS)
            c2 = t2[0] in ('NUM', 'ID') or t2[1] == '('
            if c1 and c2: res.append(('OP', '*'))
    return res

class _Parser(object):
    def __init__(self, t): self.t, self.p = t, 0
    def peek(self): return self.t[self.p] if self.p < len(self.t) else ('EOF', '')
    def get(self):
        tok = self.peek(); self.p += 1; return tok
    def parse_expression(self, mp=1):
        left = self.parse_primary()
        while self.peek()[0] == 'OP':
            op = self.peek()[1]
            pr = 1 if op in '+-' else (2 if op in '*/' else (4 if op == '^' else 0))
            if pr < mp: break
            self.get()
            right = self.parse_expression(pr if op == '^' else pr + 1)
            if op == '+': left = Add(left, right)
            elif op == '-': left = Sub(left, right)
            elif op == '*': left = Mul(left, right)
            elif op == '/': left = Div(left, right)
            elif op == '^': left = Pow(left, right)
        return left
    def parse_primary(self):
        tok = self.peek()
        if tok == ('OP', '+'): self.get(); return self.parse_primary()
        if tok == ('OP', '-'): self.get(); return Mul(Rational(-1, 1), self.parse_expression(3))
        if tok[0] == 'NUM': self.get(); return Rational(tok[1])
        if tok == ('OP', '('):
            self.get(); expr = self.parse_expression(1)
            if self.get() != ('OP', ')'): raise SyntaxError(')')
            return expr
        if tok[0] == 'ID':
            self.get(); name, low = tok[1], tok[1].lower()
            if self.peek() == ('OP', '('):
                self.get(); args = []
                if self.peek() != ('OP', ')'):
                    while True:
                        args.append(self.parse_expression(1))
                        if self.peek() == ('OP', ','): self.get()
                        else: break
                if self.get() != ('OP', ')'): raise SyntaxError(')')
                if low == 'log' and len(args) == 2: return Log(args[0], args[1])
                if low in KNOWN_FUNCTIONS:
                    if len(args) != 1: raise ValueError(name)
                    return KNOWN_FUNCTIONS[low](args[0])
                return Function(name, args[0] if args else Rational(0))
            return Symbol(low) if low in KNOWN_CONSTANTS else Symbol(name)
        raise SyntaxError(str(tok))

def parse(expr_str):
    if expr_str is None: return None
    s = str(expr_str).strip()
    if not s: return None
    toks = _insert_implicit_multiplication(_tokenize(s))
    p = _Parser(toks)
    tree = p.parse_expression(1)
    if p.p < len(toks): raise SyntaxError("Dangling at %s" % str(toks[p.p]))
    return tree

parse_expr = parse
lexer_parser = parse

def _separate_coeff_and_term(expr):
    if isinstance(expr, Rational): return expr, Rational(1, 1)
    if isinstance(expr, Mul):
        coeff, rest = Rational(1, 1), []
        for a in expr.args:
            if isinstance(a, Rational): coeff = coeff * a
            else: rest.append(a)
        if not rest: return coeff, Rational(1, 1)
        return coeff, (rest[0] if len(rest) == 1 else Mul(*rest))
    return Rational(1, 1), expr

def simplify(expr):
    expr = to_expr(expr)
    if isinstance(expr, (Rational, Symbol)): return expr
    if isinstance(expr, Add):
        terms, c_sum, t_map = [], Rational(0, 1), []
        for a in expr.args:
            sa = simplify(a)
            if isinstance(sa, Add): terms.extend(sa.args)
            else: terms.append(sa)
        for t in terms:
            c, k = _separate_coeff_and_term(t)
            if k == Rational(1, 1): c_sum = c_sum + c
            else:
                for item in t_map:
                    if item[0] == k: item[1] = item[1] + c; break
                else: t_map.append([k, c])
        res = [k if c == Rational(1, 1) else (Mul(Rational(-1, 1), k) if c == Rational(-1, 1) else Mul(c, k)) for k, c in t_map if c.num]
        if c_sum.num or not res: res.append(c_sum)
        return res[0] if len(res) == 1 else Add(*res)
    if isinstance(expr, Sub):
        return simplify(Add(expr.left, Mul(Rational(-1, 1), expr.right)))
    if isinstance(expr, Mul):
        factors, coeff, b_map = [], Rational(1, 1), []
        for a in expr.args:
            sa = simplify(a)
            if isinstance(sa, Mul): factors.extend(sa.args)
            else: factors.append(sa)
        for f in factors:
            if isinstance(f, Rational): coeff = coeff * f
            else:
                b, e = (f.base, f.exp) if isinstance(f, Pow) else (f, Rational(1, 1))
                for item in b_map:
                    if item[0] == b: item[1] = simplify(Add(item[1], e)); break
                else: b_map.append([b, e])
        if coeff.num == 0: return Rational(0, 1)
        res = [b if e == Rational(1, 1) else Pow(b, e) for b, e in b_map if not (isinstance(e, Rational) and e.is_zero)]
        if not res: return coeff
        if coeff.is_one: return res[0] if len(res) == 1 else Mul(*res)
        if coeff == Rational(-1, 1) and len(res) == 1: return Mul(Rational(-1, 1), res[0])
        return Mul(coeff, *res)
    if isinstance(expr, Div):
        sn, sd = simplify(expr.num), simplify(expr.den)
        if isinstance(sd, Rational) and sd.is_zero: raise ZeroDivisionError("Div 0")
        if isinstance(sn, Rational) and sn.is_zero: return Rational(0, 1)
        if isinstance(sd, Rational) and sd.is_one: return sn
        if isinstance(sn, Rational) and isinstance(sd, Rational): return sn / sd
        if sn == sd: return Rational(1, 1)
        canc = _cancel_rational(sn, sd)
        return canc if canc is not None else Div(sn, sd)
    if isinstance(expr, Pow):
        sb, se = simplify(expr.base), simplify(expr.exp)
        if isinstance(se, Rational) and se.is_zero: return Rational(1, 1)
        if isinstance(se, Rational) and se.is_one: return sb
        if isinstance(sb, Rational) and sb.is_zero: return Rational(0, 1)
        if isinstance(sb, Rational) and sb.is_one: return Rational(1, 1)
        if isinstance(sb, Rational) and isinstance(se, Rational): return sb ** se
        return Pow(sb, se)
    if isinstance(expr, Function):
        sa, n = simplify(expr.arg), expr.name
        if isinstance(sa, Rational) and sa.is_zero and n in ("sin", "tan"): return Rational(0, 1)
        if isinstance(sa, Rational) and sa.is_zero and n in ("cos", "exp"): return Rational(1, 1)
        if isinstance(sa, Rational) and sa.is_one and n == "ln": return Rational(0, 1)
        return expr.__class__(sa)
    return expr

simplify_expr = simplify
algebraic_simplify = simplify

def _cancel_rational(num, den):
    syms = num.free_symbols() | den.free_symbols()
    if len(syms) != 1: return None
    var = list(syms)[0]
    pn, pd = _to_poly_coeffs(num, var), _to_poly_coeffs(den, var)
    if pn and pd:
        q, r = _poly_div(pn, pd)
        if all(c.is_zero for c in r): return _from_poly_coeffs(q, var)
    return None

def _to_poly_coeffs(expr, var):
    terms = expand(expr)
    terms = terms.args if isinstance(terms, Add) else (terms,)
    deg_map = {}
    for t in terms:
        c, k = _separate_coeff_and_term(t)
        if k == Rational(1, 1): d = 0
        elif isinstance(k, Symbol) and k.name == var: d = 1
        elif isinstance(k, Pow) and isinstance(k.base, Symbol) and k.base.name == var and isinstance(k.exp, Rational) and k.exp.den == 1 and k.exp.num >= 0:
            d = k.exp.num
        else: return None
        deg_map[d] = deg_map.get(d, Rational(0, 1)) + c
    return [deg_map.get(d, Rational(0, 1)) for d in range(max(deg_map.keys()) + 1)] if deg_map else [Rational(0, 1)]

def _from_poly_coeffs(coeffs, var):
    v, terms = Symbol(var), []
    for d, c in enumerate(coeffs):
        if c.is_zero: continue
        pt = Rational(1, 1) if d == 0 else (v if d == 1 else Pow(v, Rational(d, 1)))
        terms.append(pt if c.is_one else (Mul(Rational(-1, 1), pt) if c == Rational(-1, 1) else (c if d == 0 else Mul(c, pt))))
    return terms[0] if len(terms) == 1 else (Add(*terms) if terms else Rational(0, 1))

def _poly_div(p, q):
    while len(p) > 1 and p[-1].is_zero: p.pop()
    while len(q) > 1 and q[-1].is_zero: q.pop()
    if q[-1].is_zero: raise ZeroDivisionError("Poly div 0")
    dp, dq = len(p) - 1, len(q) - 1
    if dp < dq: return [Rational(0, 1)], p
    quot, rem = [Rational(0, 1)] * (dp - dq + 1), list(p)
    for i in range(dp - dq, -1, -1):
        quot[i] = rem[i + dq] / q[-1]
        for j in range(dq + 1): rem[i + j] = rem[i + j] - quot[i] * q[j]
    while len(rem) > 1 and rem[-1].is_zero: rem.pop()
    return quot, rem

def expand(expr):
    expr = to_expr(expr)
    if isinstance(expr, Mul):
        curr = [Rational(1, 1)]
        for a in [expand(x) for x in expr.args]:
            at = a.args if isinstance(a, Add) else (a,)
            curr = [Mul(c_t, a_t) for c_t in curr for a_t in at]
        return simplify(Add(*curr))
    if isinstance(expr, Pow) and isinstance(expr.exp, Rational) and expr.exp.den == 1 and 1 < expr.exp.num <= 10:
        base, res = expand(expr.base), expand(expr.base)
        for _ in range(expr.exp.num - 1): res = expand(Mul(res, base))
        return res
    if isinstance(expr, Add): return simplify(Add(*[expand(a) for a in expr.args]))
    if isinstance(expr, Sub): return simplify(Sub(expand(expr.left), expand(expr.right)))
    return expr

class StepList(list):
    def __str__(self): return "\n".join(self)
    def __repr__(self): return "\n".join(self)

def diff(expr, var="x", steps=False):
    expr, v = to_expr(expr), str(var).strip()
    if steps: return diff_steps(expr, v)
    return simplify(_diff_node(expr, v))

derivative = diff
differentiate = diff

def _diff_node(node, var):
    if isinstance(node, Rational): return Rational(0, 1)
    if isinstance(node, Symbol): return Rational(1, 1) if node.name == var else Rational(0, 1)
    if isinstance(node, Add): return Add(*[_diff_node(a, var) for a in node.args])
    if isinstance(node, Sub): return Sub(_diff_node(node.left, var), _diff_node(node.right, var))
    if isinstance(node, Mul):
        return Add(*[Mul(*[node.args[j] if i != j else _diff_node(node.args[j], var) for j in range(len(node.args))]) for i in range(len(node.args))])
    if isinstance(node, Div):
        u, v = node.num, node.den
        return Div(Sub(Mul(_diff_node(u, var), v), Mul(u, _diff_node(v, var))), Pow(v, Rational(2, 1)))
    if isinstance(node, Pow):
        b, e = node.base, node.exp
        b_dep, e_dep = var in b.free_symbols(), var in e.free_symbols()
        if not b_dep and not e_dep: return Rational(0, 1)
        if b_dep and not e_dep: return Mul(e, Pow(b, Sub(e, Rational(1, 1))), _diff_node(b, var))
        if not b_dep and e_dep: return Mul(node, Ln(b), _diff_node(e, var))
        du, dv = _diff_node(b, var), _diff_node(e, var)
        return Mul(node, Add(Mul(dv, Ln(b)), Div(Mul(e, du), b)))
    if isinstance(node, Function):
        arg, da, n = node.arg, _diff_node(node.arg, var), node.name
        if n == "sin": return Mul(Cos(arg), da)
        if n == "cos": return Mul(Rational(-1, 1), Sin(arg), da)
        if n == "tan": return Mul(Pow(Sec(arg), Rational(2, 1)), da)
        if n == "sec": return Mul(Sec(arg), Tan(arg), da)
        if n == "csc": return Mul(Rational(-1, 1), Csc(arg), Cot(arg), da)
        if n == "cot": return Mul(Rational(-1, 1), Pow(Csc(arg), Rational(2, 1)), da)
        if n == "exp": return Mul(Exp(arg), da)
        if n == "ln": return Div(da, arg)
        if n == "log": return Div(da, Mul(arg, Ln(node.base or Rational(10, 1))))
        if n == "sqrt": return Div(da, Mul(Rational(2, 1), Sqrt(arg)))
        if n == "asin": return Div(da, Sqrt(Sub(Rational(1, 1), Pow(arg, Rational(2, 1)))))
        if n == "acos": return Mul(Rational(-1, 1), Div(da, Sqrt(Sub(Rational(1, 1), Pow(arg, Rational(2, 1))))))
        if n == "atan": return Div(da, Add(Rational(1, 1), Pow(arg, Rational(2, 1))))
    return Rational(0, 1)

def diff_steps(expr, var="x"):
    expr, vs, s = to_expr(expr), str(var).strip(), StepList()
    s.append("1. Differentiating expression with respect to %s: d/d%s [%s]" % (vs, vs, str(expr)))
    syms = expr.free_symbols()
    if isinstance(expr, Rational) or (syms and vs not in syms):
        s.append("2. Constant rule: d/d%s [c] = 0 for constant expression." % vs)
    elif isinstance(expr, Symbol) and expr.name == vs:
        s.append("2. Linear variable rule: d/d%s [%s] = 1." % (vs, vs))
    elif isinstance(expr, (Add, Sub)):
        s.append("2. Sum / Difference rule: differentiating term-by-term: d/d%s [f +/- g] = f' +/- g'." % vs)
        for i, t in enumerate(expr.args):
            s.append("   Term %d: d/d%s [%s] = %s" % (i + 1, vs, str(t), str(diff(t, vs))))
    elif isinstance(expr, Mul):
        s.append("2. Product rule: d/d%s [f * g] = f' * g + f * g'." % vs)
    elif isinstance(expr, Div):
        s.append("2. Quotient rule: d/d%s [f / g] = (f' * g - f * g') / (g^2) for denominator %s." % (vs, str(expr.den)))
    elif isinstance(expr, Pow):
        s.append("2. %s rule: d/d%s [%s]." % ("Power" if vs not in expr.exp.free_symbols() else "Exponential", vs, str(expr)))
    elif isinstance(expr, Function):
        s.append("2. Chain rule: d/d%s [f(g(%s))] = f'(g(%s)) * g'(%s) with inner function %s." % (vs, vs, vs, vs, str(expr.arg)))
    s.append("Result: %s" % str(diff(expr, vs)))
    return s

derivative_steps = diff_steps
differentiate_steps = diff_steps

def integrate(expr, var="x", a=None, b=None):
    expr, vs = to_expr(expr), str(var).strip()
    if a is not None and b is not None:
        return _definite_integral(expr, vs, a, b)
    return simplify(_integrate_node(expr, vs))

integral = integrate
anti_derivative = integrate

def _integrate_node(node, var):
    v = Symbol(var)
    if isinstance(node, Rational): return Mul(node, v)
    if isinstance(node, Symbol):
        return Mul(Rational(1, 2), Pow(v, Rational(2, 1))) if node.name == var else Mul(node, v)
    if isinstance(node, Add): return Add(*[_integrate_node(a, var) for a in node.args])
    if isinstance(node, Sub): return Sub(_integrate_node(node.left, var), _integrate_node(node.right, var))
    if isinstance(node, Mul):
        c, k = _separate_coeff_and_term(node)
        if c != Rational(1, 1): return Mul(c, _integrate_node(k, var))
    if isinstance(node, Pow) and isinstance(node.base, Symbol) and node.base.name == var:
        if isinstance(node.exp, Rational) and node.exp == Rational(-1, 1): return Ln(v)
        new_exp = simplify(Add(node.exp, Rational(1, 1)))
        return Div(Pow(v, new_exp), new_exp)
    if isinstance(node, Div) and isinstance(node.num, Rational):
        if isinstance(node.den, Symbol) and node.den.name == var: return Mul(node.num, Ln(v))
        if isinstance(node.den, Pow) and isinstance(node.den.base, Symbol) and node.den.base.name == var:
            return Mul(node.num, _integrate_node(Pow(v, Mul(Rational(-1, 1), node.den.exp)), var))
    if isinstance(node, Function) and isinstance(node.arg, Symbol) and node.arg.name == var:
        if node.name == "sin": return Mul(Rational(-1, 1), Cos(v))
        if node.name == "cos": return Sin(v)
        if node.name == "exp": return Exp(v)
    return Mul(node, v)

def _definite_integral(expr, var, a, b):
    av, bv = float(a), float(b)
    if av == bv: return Rational(0, 1)
    try:
        F = integrate(expr, var)
        return F.subs(var, bv).evalf() - F.subs(var, av).evalf()
    except Exception:
        return riemann_sum(expr, var, av, bv, n=100, method="simpson")

def riemann_sum(expr, var="x", a=0, b=1, n=10, method="midpoint"):
    expr, vs, af, bf, ni = to_expr(expr), str(var).strip(), float(a), float(b), int(n)
    if ni <= 0: raise ValueError("n must be positive")
    dx = (bf - af) / float(ni)
    if method == "left":
        return sum(expr.subs(vs, af + i * dx).evalf() for i in range(ni)) * dx
    if method == "right":
        return sum(expr.subs(vs, af + i * dx).evalf() for i in range(1, ni + 1)) * dx
    fa, fb = expr.subs(vs, af).evalf(), expr.subs(vs, bf).evalf()
    if method == "trapezoid":
        return (dx / 2.0) * (fa + 2.0 * sum(expr.subs(vs, af + i * dx).evalf() for i in range(1, ni)) + fb)
    if method == "simpson":
        if ni % 2: ni += 1; dx = (bf - af) / float(ni)
        so = sum(expr.subs(vs, af + i * dx).evalf() for i in range(1, ni, 2))
        se = sum(expr.subs(vs, af + i * dx).evalf() for i in range(2, ni, 2))
        return (dx / 3.0) * (fa + 4.0 * so + 2.0 * se + fb)
    return sum(expr.subs(vs, af + (i + 0.5) * dx).evalf() for i in range(ni)) * dx

riemann = riemann_sum
approx_integral = riemann_sum

def limit(expr, var="x", target=0, direction="both"):
    expr, vs, tf = to_expr(expr), str(var).strip(), float(target)
    se = simplify(expr)
    try:
        val = se.subs(vs, tf).evalf()
        if not math.isnan(val) and not math.isinf(val): return val
    except (ZeroDivisionError, ValueError, OverflowError): pass
    if isinstance(se, Div):
        u, v = se.num, se.den
        for _ in range(5):
            u, v = diff(u, vs), diff(v, vs)
            try:
                up, vp = u.subs(vs, tf).evalf(), v.subs(vs, tf).evalf()
                if abs(vp) > 1e-12: return up / vp
            except Exception: pass
    for eps in [1e-4, 1e-5, 1e-6]:
        try:
            vr, vl = expr.subs(vs, tf + eps).evalf(), expr.subs(vs, tf - eps).evalf()
            if direction == "right": return vr
            if direction == "left": return vl
            return (vr + vl) / 2.0 if abs(vr - vl) < 1e-2 else vr
        except Exception: continue
    return tf

eval_limit = limit
calc_limit = limit

def series(expr, var="x", point=0, order=4):
    expr, vs, v, pf, oi = to_expr(expr), str(var).strip(), Symbol(str(var).strip()), float(point), int(order)
    terms, cur, fact = [], expr, 1
    for k in range(oi):
        if k > 0: fact *= k
        try: c = cur.subs(vs, pf).evalf()
        except Exception: c = float(limit(cur, vs, pf))
        coef = float_to_rational(c)
        if not coef.is_zero:
            cf = coef / Rational(fact, 1)
            pw = (v if k == 1 else Pow(v, Rational(k, 1))) if pf == 0.0 else (Sub(v, float_to_rational(pf)) if k == 1 else Pow(Sub(v, float_to_rational(pf)), Rational(k, 1)))
            if k == 0: terms.append(cf)
            elif cf.is_one: terms.append(pw)
            elif cf == Rational(-1, 1): terms.append(Mul(Rational(-1, 1), pw))
            else: terms.append(Mul(cf, pw))
        cur = diff(cur, vs)
    return terms[0] if len(terms) == 1 else (Add(*terms) if terms else Rational(0, 1))

taylor = series
taylor_series = series
maclaurin = series

def tangent_line(expr, point_c, var="x"):
    if isinstance(point_c, str) and not isinstance(var, str): point_c, var = var, point_c
    expr, vs, cf = to_expr(expr), str(var).strip(), float(point_c)
    v, y0, m = Symbol(vs), expr.subs(vs, cf).evalf(), diff(expr, vs).subs(vs, cf).evalf()
    mr, br = float_to_rational(m), float_to_rational(y0 - m * cf)
    if mr.is_zero: return br
    mx = v if mr.is_one else (Mul(Rational(-1, 1), v) if mr == Rational(-1, 1) else Mul(mr, v))
    if br.is_zero: return mx
    return Sub(mx, Rational(-br.num, br.den)) if br.num < 0 else Add(mx, br)

tangent = tangent_line
calc_tangent_line = tangent_line

def normal_line(expr, point_c, var="x"):
    if isinstance(point_c, str) and not isinstance(var, str): point_c, var = var, point_c
    expr, vs, cf = to_expr(expr), str(var).strip(), float(point_c)
    v, y0, m = Symbol(vs), expr.subs(vs, cf).evalf(), diff(expr, vs).subs(vs, cf).evalf()
    if abs(m) < 1e-12: raise ZeroDivisionError("Horizontal tangent")
    mr, br = float_to_rational(-1.0 / m), float_to_rational(y0 - (-1.0 / m) * cf)
    if mr.is_zero: return br
    mx = v if mr.is_one else (Mul(Rational(-1, 1), v) if mr == Rational(-1, 1) else Mul(mr, v))
    if br.is_zero: return mx
    return Sub(mx, Rational(-br.num, br.den)) if br.num < 0 else Add(mx, br)

normal = normal_line
calc_normal_line = normal_line

def evaluate(expr, **subs): return to_expr(expr).evalf(subs)

def subs(expr, *args, **kwargs):
    if len(args) == 2 and isinstance(args[0], str): return to_expr(expr).subs(args[0], args[1])
    if len(args) == 1 and isinstance(args[0], dict): return to_expr(expr).subs(args[0])
    return to_expr(expr).subs(kwargs)

MENU_ITEMS = [
    "1. Differentiate  (d/dx)",
    "2. Integrate      (S dx)",
    "3. Simplify Expression",
    "4. Limits & L'Hopital",
    "5. Taylor Series",
    "6. Tangent Line",
    "7. Normal Line",
    "8. Evaluate / Subs",
    "9. Interactive Shell",
]

def draw_gui_menu(selected=0):
    if not HAS_TI: return
    try:
        ti_draw.clear()
        ti_draw.set_color(18, 48, 88)
        ti_draw.fill_rect(0, 0, 320, 24)
        ti_draw.set_color(40, 140, 230)
        ti_draw.fill_rect(0, 24, 320, 2)
        ti_draw.set_color(255, 255, 255)
        ti_draw.draw_text(8, 6, "FlowCE Evo CAS")
        ti_draw.set_color(120, 200, 255)
        ti_draw.draw_text(210, 6, "v1.1 [Evo Edition]")
        ti_draw.set_color(25, 30, 42)
        ti_draw.fill_rect(8, 28, 304, 182)
        ti_draw.set_color(45, 55, 75)
        ti_draw.draw_rect(8, 28, 304, 182)
        for i, item in enumerate(MENU_ITEMS):
            y = 32 + i * 19
            if i == selected:
                ti_draw.set_color(38, 75, 125)
                ti_draw.fill_rect(12, y - 1, 296, 17)
                ti_draw.set_color(255, 255, 255)
            else:
                ti_draw.set_color(200, 215, 235)
            ti_draw.draw_text(16, y, item)
        ti_draw.set_color(14, 20, 30)
        ti_draw.fill_rect(0, 214, 320, 26)
        ti_draw.set_color(160, 200, 240)
        ti_draw.draw_text(8, 220, "[1-9] Select | [^/v] Move | [CLEAR] Exit")
    except Exception: pass

def draw_result_screen(title, query, result):
    if not HAS_TI:
        print("--- %s ---" % str(title))
        print("Input:  %s" % str(query))
        print("Result: %s" % str(result))
        return
    try:
        ti_draw.clear()
        ti_draw.set_color(18, 48, 88)
        ti_draw.fill_rect(0, 0, 320, 24)
        ti_draw.set_color(40, 140, 230)
        ti_draw.fill_rect(0, 24, 320, 2)
        ti_draw.set_color(255, 255, 255)
        ti_draw.draw_text(8, 6, "FlowCE Evo - " + str(title)[:24])
        ti_draw.set_color(25, 30, 42)
        ti_draw.fill_rect(8, 28, 304, 182)
        ti_draw.set_color(40, 140, 230)
        ti_draw.draw_rect(8, 28, 304, 182)
        ti_draw.set_color(130, 165, 205)
        ti_draw.draw_text(16, 36, "Input:")
        ti_draw.set_color(255, 255, 255)
        ti_draw.draw_text(16, 54, str(query)[:36])
        ti_draw.set_color(45, 55, 75)
        ti_draw.draw_line(16, 76, 296, 76)
        ti_draw.set_color(80, 220, 140)
        ti_draw.draw_text(16, 88, "Result:")
        ti_draw.set_color(255, 255, 255)
        rs = str(result)
        ti_draw.draw_text(16, 108, rs[:36])
        if len(rs) > 36: ti_draw.draw_text(16, 128, rs[36:72])
        if len(rs) > 72: ti_draw.draw_text(16, 148, rs[72:108])
        ti_draw.set_color(18, 48, 88)
        ti_draw.fill_rect(0, 214, 320, 26)
        ti_draw.set_color(220, 235, 255)
        ti_draw.draw_text(8, 220, "[ENTER] / [CLEAR] Return to Menu")
        ti_system.get_key(1)
    except Exception: pass

def prompt_ti_input(title, prompt, default_val=""):
    if HAS_TI:
        try:
            ti_system.disp_clr()
            ti_system.disp_at(1, "--- " + str(title) + " ---", "center")
            ti_system.disp_at(3, str(prompt))
            if default_val: ti_system.disp_at(5, "[Default: " + str(default_val) + "]")
        except Exception: pass
    try:
        val = input(prompt).strip()
    except Exception:
        val = ""
    return val if val else default_val

def run_action(idx):
    try:
        if idx == 0:
            f = prompt_ti_input("Differentiate", "f(x) = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            v = prompt_ti_input("Differentiate", "var [x] = ", "x")
            res = diff(f, v)
            draw_result_screen("Derivative", "d/d" + v + "(" + f + ")", str(res))
        elif idx == 1:
            f = prompt_ti_input("Integrate", "f(x) = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            v = prompt_ti_input("Integrate", "var [x] = ", "x")
            la = prompt_ti_input("Integrate", "lower lim [none] = ", "")
            if la:
                lb = prompt_ti_input("Integrate", "upper lim = ", "")
                res = integrate(f, v, la, lb)
                draw_result_screen("Definite Integral", "S[" + la + ".." + lb + "] " + f + " d" + v, str(res))
            else:
                res = integrate(f, v)
                draw_result_screen("Indefinite Integral", "S " + f + " d" + v, str(res) + " + C")
        elif idx == 2:
            f = prompt_ti_input("Simplify", "expr = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            res = simplify(parse(f))
            draw_result_screen("Simplify", f, str(res))
        elif idx == 3:
            f = prompt_ti_input("Limit", "f(x) = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            v = prompt_ti_input("Limit", "var [x] = ", "x")
            c = prompt_ti_input("Limit", "approach point c = ", "0")
            res = limit(f, v, float(c) if '.' in c else int(c))
            draw_result_screen("Limit", "lim(" + v + "->" + c + ") " + f, str(res))
        elif idx == 4:
            f = prompt_ti_input("Taylor Series", "f(x) = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            v = prompt_ti_input("Taylor Series", "var [x] = ", "x")
            c = prompt_ti_input("Taylor Series", "center c [0] = ", "0")
            n = prompt_ti_input("Taylor Series", "order n [3] = ", "3")
            res = series(f, v, int(c), int(n))
            draw_result_screen("Taylor Series", "Taylor(" + f + ", n=" + n + ")", str(res))
        elif idx == 5:
            f = prompt_ti_input("Tangent Line", "f(x) = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            c = prompt_ti_input("Tangent Line", "point x0 [1] = ", "1")
            res = tangent_line(f, c)
            draw_result_screen("Tangent Line", "Tangent to " + f + " @ x=" + c, "y = " + str(res))
        elif idx == 6:
            f = prompt_ti_input("Normal Line", "f(x) = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            c = prompt_ti_input("Normal Line", "point x0 [1] = ", "1")
            res = normal_line(f, c)
            draw_result_screen("Normal Line", "Normal to " + f + " @ x=" + c, "y = " + str(res))
        elif idx == 7:
            f = prompt_ti_input("Evaluate", "expr = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            x_val = prompt_ti_input("Evaluate", "x = ", "1")
            val = float(x_val) if '.' in x_val else int(x_val)
            res = evaluate(f, x=val)
            draw_result_screen("Evaluate", f + " @ x=" + x_val, str(res))
        elif idx == 8:
            run_interactive_shell()
    except Exception as err:
        draw_result_screen("Error", "Execution Error", str(err))
    finally:
        try: gc.collect()
        except Exception: pass

def run_interactive_shell():
    if HAS_TI:
        try:
            ti_system.disp_clr()
            ti_system.disp_at(1, "FlowCE CAS Terminal", "center")
            ti_system.disp_at(3, "Type 'menu' to return")
        except Exception: pass
    print("FlowCE Terminal. Type math expression or 'menu' to return.")
    while True:
        try:
            line = input("FlowCE> ").strip()
            if not line: continue
            if line.lower() in ("menu", "quit", "exit", "q"): break
            lower = line.lower()
            if lower.startswith("diff "):
                parts = line[5:].split()
                var = parts[1] if len(parts) > 1 else "x"
                print("= %s" % str(diff(parts[0], var)))
            elif lower.startswith("int "):
                parts = line[4:].split()
                var = parts[1] if len(parts) > 1 else "x"
                print("= %s + C" % str(integrate(parts[0], var)))
            elif lower.startswith("sim "):
                print("= %s" % str(simplify(parse(line[4:]))))
            else:
                print("= %s" % str(simplify(parse(line))))
            try: gc.collect()
            except Exception: pass
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as err:
            print("Error: %s" % str(err))

def run_ti_gui():
    selected = 0
    num_opts = len(MENU_ITEMS)
    while True:
        draw_gui_menu(selected)
        try:
            k = ti_system.get_key(1)
        except Exception:
            k = ti_system.disp_wait()
        if k == "" or k is None:
            break
        if k in (82, '1'): run_action(0)
        elif k in (83, '2'): run_action(1)
        elif k in (84, '3'): run_action(2)
        elif k in (72, '4'): run_action(3)
        elif k in (73, '5'): run_action(4)
        elif k in (74, '6'): run_action(5)
        elif k in (75, '7'): run_action(6)
        elif k in (62, '8'): run_action(7)
        elif k in (63, '9'): run_action(8)
        elif k in (25, 'up'): selected = (selected - 1) % num_opts
        elif k in (35, 'down'): selected = (selected + 1) % num_opts
        elif k in (105, 95, 'enter', '\n'): run_action(selected)
        elif k in (45, 'clear', 'esc', 'exit', 'q'): break
    try:
        ti_draw.clear()
        ti_system.disp_clr()
    except Exception: pass

def run_pc_cli():
    print("========================================")
    print(" FlowCE Evo CAS - Computer Algebra System")
    print("========================================")
    for item in MENU_ITEMS: print(" " + item)
    print(" [q] Exit")
    while True:
        try:
            choice = input("\nSelect [1-9, q]: ").strip().lower()
            if not choice: continue
            if choice in ("q", "quit", "exit"): break
            if choice in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                run_action(int(choice) - 1)
            else:
                print("= %s" % str(simplify(parse(choice))))
        except (KeyboardInterrupt, EOFError): break
        except Exception as err: print("Error: %s" % str(err))

def run_ui():
    if HAS_TI: run_ti_gui()
    else: run_pc_cli()

def cli_main(args=None):
    if args is None: args = sys.argv[1:]
    if not args:
        run_ui()
        return
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
        try:
            print(str(parse(cmd)))
        except Exception as err:
            print("Error: %s" % str(err))

if __name__ == "__main__":
    cli_main()
